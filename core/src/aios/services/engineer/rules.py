import os
from typing import Any, Dict, List


def filepath_to_module_path(filepath: str) -> str:
    # Remove .py
    if filepath.endswith(".py"):
        filepath = filepath[:-3]
    # Remove /__init__
    if filepath.endswith("/__init__"):
        filepath = filepath[:-9]
    # Normalize slashes
    filepath = filepath.replace("\\", "/")
    
    # Strip any prefix before "aios/" or "skills/"
    for prefix in ["aios/", "skills/"]:
        if prefix in filepath:
            idx = filepath.find(prefix)
            filepath = filepath[idx:]
            break
    # Replace slashes with dots
    return filepath.replace("/", ".")

class ArchitectureRuleEngine:
    def __init__(self, graph: Any) -> None:
        self.graph = graph

    def _get_layer(self, name_or_path: str) -> int:
        path_lower = name_or_path.lower()
        if "cli.py" in path_lower or "/cli/" in path_lower or ".cli" in path_lower:
            return 1
        if "kernel" in path_lower or "registry" in path_lower or "config" in path_lower:
            return 2
        if (
            "brain" in path_lower
            or "services/action" in path_lower
            or "services/task" in path_lower
            or "services.action" in path_lower
            or "services.task" in path_lower
        ):
            return 4
        if "services" in path_lower or "providers" in path_lower:
            return 3
        if "skills" in path_lower:
            return 5
        return 3  # Default layer

    def _is_abstract_contract(self, import_str: str) -> bool:
        # Abstract contracts typically end with Service or Interface
        # and do not have Local/Impl/Concrete
        imp_lower = import_str.lower()
        if "impl" in imp_lower or "local" in imp_lower or "concrete" in imp_lower:
            return False
            
        # Extract the last part (module or class/type)
        parts = import_str.split(".")
        last_part = parts[-1]
        last_part_lower = last_part.lower()
        
        # Must contain "service" (but not be exactly "services") or contain "interface"
        if last_part_lower == "services":
            return False
            
        return "service" in last_part_lower or "interface" in last_part_lower

    def validate(self) -> List[Dict[str, Any]]:
        violations = []
        idx_data = self.graph.index_data.get("index_data", {})

        # Build mapping from file path to full module path
        filepath_to_mod = {}
        for filepath in idx_data.keys():
            filepath_to_mod[filepath] = filepath_to_module_path(filepath)

        known_modules = set(filepath_to_mod.values())

        # Resolve an import string to a known module path if possible
        def resolve_import(imp: str) -> str:
            # Try to find the longest matching known module
            best_match = None
            for known_mod in known_modules:
                if imp == known_mod or imp.startswith(known_mod + "."):
                    if best_match is None or len(known_mod) > len(best_match):
                        best_match = known_mod
            return best_match if best_match is not None else imp

        # 1. Build adjacency list for cycle detection
        adj = {}
        for filepath, data in idx_data.items():
            mod = filepath_to_mod[filepath]
            resolved_imports = []
            for imp in data.get("imports", []):
                resolved = resolve_import(imp)
                if resolved in known_modules:
                    resolved_imports.append(resolved)
            adj[mod] = resolved_imports

        # DFS cycle detection
        visited = {}
        path = []
        path_set = set()

        def dfs(node):
            if node in path_set:
                idx = path.index(node)
                cycle = path[idx:] + [node]
                violations.append({
                    "type": "circular_dependency",
                    "description": f"Circular dependency cycle: {' -> '.join(cycle)}"
                })
                return
            if node in visited:
                return
            path.append(node)
            path_set.add(node)
            for neighbor in adj.get(node, []):
                dfs(neighbor)
            path_set.remove(node)
            path.pop()
            visited[node] = True

        for k in adj.keys():
            dfs(k)

        # 2. Layering & Invalid Import validation
        for filepath, data in idx_data.items():
            source_layer = self._get_layer(filepath)
            imports = data.get("imports", [])
            for imp in imports:
                target_layer = self._get_layer(imp)
                
                # Rule: Lower layers must not import from higher layers,
                # unless it is an abstract contract
                if target_layer < source_layer:
                    # Exception: Abstract service contracts (from Layer 3) imported by Layer 4/5
                    if target_layer == 3 and self._is_abstract_contract(imp):
                        pass
                    else:
                        violations.append({
                            "type": "layering_violation",
                            "description": (
                                f"Layering violation: Lower layer module "
                                f"'{os.path.basename(filepath)}' (Layer {source_layer}) "
                                f"imports higher layer '{imp}' (Layer {target_layer})."
                            )
                        })

                # Rule: Kernel (Layer 2) cannot import higher layers (Layer 4/5) directly
                if source_layer == 2 and target_layer >= 4:
                    violations.append({
                        "type": "layering_violation",
                        "description": (
                            f"Layering violation: Kernel module '{os.path.basename(filepath)}' "
                            f"(Layer {source_layer}) imports higher layer '{imp}' "
                            f"(Layer {target_layer})."
                        )
                    })

                # Rule: Core layers (1, 2, 3) must never import skills/plugins (Layer 5)
                if source_layer <= 3 and target_layer == 5:
                    violations.append({
                        "type": "layering_violation",
                        "description": (
                            f"Layering violation: Core module "
                            f"'{os.path.basename(filepath)}' (Layer {source_layer}) "
                            f"imports plugin/extension '{imp}' (Layer {target_layer})."
                        )
                    })

                # Rule: Cross-layer imports must not target concrete implementations
                if source_layer != target_layer:
                    imp_lower = imp.lower()
                    if target_layer == 3 and ("impl" in imp_lower or "local" in imp_lower):
                        violations.append({
                            "type": "invalid_import",
                            "description": (
                                f"Invalid import: module "
                                f"'{os.path.basename(filepath)}' (Layer {source_layer}) "
                                f"imports concrete implementation '{imp}' "
                                f"from Service Layer (Layer 3)."
                            )
                        })

        # Deduplicate violations by type and description
        unique_violations = []
        seen = set()
        for v in violations:
            key = (v["type"], v["description"])
            if key not in seen:
                seen.add(key)
                unique_violations.append(v)

        return unique_violations
