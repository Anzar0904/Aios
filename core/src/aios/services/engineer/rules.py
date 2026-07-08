from typing import List, Dict, Any
import os

class ArchitectureRuleEngine:
    def __init__(self, graph: Any) -> None:
        self.graph = graph

    def _get_layer(self, name_or_path: str) -> int:
        path_lower = name_or_path.lower()
        if "cli.py" in path_lower or "/cli/" in path_lower or ".cli" in path_lower:
            return 1
        if "kernel" in path_lower or "registry" in path_lower or "config" in path_lower:
            return 2
        if "brain" in path_lower or "services/action" in path_lower or "services/task" in path_lower or "services.action" in path_lower or "services.task" in path_lower:
            return 4
        if "services" in path_lower or "providers" in path_lower:
            return 3
        if "skills" in path_lower:
            return 5
        return 3  # Default layer

    def _is_abstract_contract(self, import_str: str) -> bool:
        # Abstract contracts typically end with Service or Interface and do not have Local/Impl/Concrete
        imp_lower = import_str.lower()
        if "impl" in imp_lower or "local" in imp_lower or "concrete" in imp_lower:
            return False
        return "service" in imp_lower or "interface" in imp_lower

    def validate(self) -> List[Dict[str, Any]]:
        violations = []
        idx_data = self.graph.index_data.get("index_data", {})

        def to_node_name(name_or_path: str) -> str:
            if "/" in name_or_path or name_or_path.endswith(".py"):
                return os.path.basename(name_or_path).replace(".py", "")
            return name_or_path.split(".")[-1]

        # 1. Build adjacency list for cycle detection
        adj = {}
        for filepath, data in idx_data.items():
            mod = to_node_name(filepath)
            adj[mod] = [to_node_name(imp) for imp in data.get("imports", [])]

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
                
                # Rule: Lower layers must not import from higher layers, unless it is an abstract contract
                if target_layer < source_layer:
                    # Exception: Abstract service contracts (from Layer 3) imported by Layer 4/5
                    if target_layer == 3 and self._is_abstract_contract(imp):
                        pass
                    else:
                        violations.append({
                            "type": "layering_violation",
                            "description": f"Layering violation: Lower layer module '{os.path.basename(filepath)}' (Layer {source_layer}) imports higher layer '{imp}' (Layer {target_layer})."
                        })

                # Rule: Core layers (1, 2, 3) must never import skills/plugins (Layer 5)
                if source_layer < 5 and target_layer == 5:
                    violations.append({
                        "type": "layering_violation",
                        "description": f"Layering violation: Core module '{os.path.basename(filepath)}' (Layer {source_layer}) imports plugin/extension '{imp}' (Layer {target_layer})."
                    })

                # Rule: Cross-layer imports must not target concrete implementations (Interface-Only Imports)
                if source_layer != target_layer:
                    imp_lower = imp.lower()
                    if target_layer == 3 and ("impl" in imp_lower or "local" in imp_lower):
                        violations.append({
                            "type": "invalid_import",
                            "description": f"Invalid import: module '{os.path.basename(filepath)}' (Layer {source_layer}) imports concrete implementation '{imp}' from Service Layer (Layer 3)."
                        })

        return violations
