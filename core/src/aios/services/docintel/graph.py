import os
from typing import Any, Dict, List, Set


class DependencyGraphBuilder:
    """Builds module, package, and service dependency graphs and generates Mermaid flowcharts."""

    def _get_module_name(self, filepath: str) -> str:
        """Converts file path to python dot-separated module name."""
        # Standardize path separators
        norm = filepath.replace(os.sep, "/")
        # Remove core/src/ prefix if present
        if norm.startswith("core/src/"):
            norm = norm[len("core/src/") :]
        elif norm.startswith("src/"):
            norm = norm[len("src/") :]

        if norm.endswith(".py"):
            norm = norm[:-3]
        return norm.replace("/", ".")

    def build_dependency_graph(
        self, scan_results: Dict[str, Any], index_data: Dict[str, Dict[str, Any]]
    ) -> Dict[str, List[str]]:
        """Constructs an adjacency list of module relationships based on imports."""
        graph = {}
        scanned_modules = set(scan_results.get("modules", []))

        for filepath, meta in index_data.items():
            mod = self._get_module_name(filepath)
            graph[mod] = []
            if "imports" in meta:
                for imp in meta["imports"]:
                    # Match imports against scanned modules
                    for scanned in scanned_modules:
                        if (imp == scanned or imp.startswith(scanned + ".")) and scanned != mod:
                            if scanned not in graph[mod]:
                                graph[mod].append(scanned)

        return graph

    def build_package_graph(
        self, scan_results: Dict[str, Any], dep_graph: Dict[str, List[str]]
    ) -> Dict[str, List[str]]:
        """Constructs an adjacency list of package-level dependencies."""
        graph = {}
        packages = set(scan_results.get("packages", []))

        # Helper to find package for a module
        def get_package(module: str) -> str:
            parts = module.split(".")
            for i in range(len(parts), 0, -1):
                parent = ".".join(parts[:i])
                if parent in packages:
                    return parent
            # Fallback to top-level name
            return parts[0] if parts else ""

        for source_mod, targets in dep_graph.items():
            src_pkg = get_package(source_mod)
            if not src_pkg:
                continue

            if src_pkg not in graph:
                graph[src_pkg] = []

            for target_mod in targets:
                target_pkg = get_package(target_mod)
                if target_pkg and target_pkg != src_pkg:
                    if target_pkg not in graph[src_pkg]:
                        graph[src_pkg].append(target_pkg)

        return graph

    def build_service_graph(
        self, scan_results: Dict[str, Any], dep_graph: Dict[str, List[str]]
    ) -> Dict[str, List[str]]:
        """Extracts the dependency graph filtered for services, providers, and registries."""
        graph = {}
        services = {s["path"] for s in scan_results.get("services", [])}
        providers = {p["path"] for p in scan_results.get("providers", [])}
        registries = {r["path"] for r in scan_results.get("registries", [])}

        special_modules = set()
        for path in services.union(providers).union(registries):
            special_modules.add(self._get_module_name(path))

        for source, targets in dep_graph.items():
            if source in special_modules:
                graph[source] = []
                for target in targets:
                    if target in special_modules:
                        graph[source].append(target)

        return graph

    def generate_mermaid(self, graph: Dict[str, List[str]], title: str = "Graph") -> str:
        """Converts adjacency lists to a Mermaid flowchart diagram."""
        lines = ["flowchart TD", f"    %% {title}"]
        seen_nodes: Set[str] = set()

        for source, targets in graph.items():
            source_label = source.split(".")[-1]
            source_id = source.replace(".", "_")
            if source_id not in seen_nodes:
                lines.append(f'    {source_id}["{source_label}"]')
                seen_nodes.add(source_id)

            for target in targets:
                target_label = target.split(".")[-1]
                target_id = target.replace(".", "_")
                if target_id not in seen_nodes:
                    lines.append(f'    {target_id}["{target_label}"]')
                    seen_nodes.add(target_id)
                lines.append(f"    {source_id} --> {target_id}")

        # If graph is empty, add a default node
        if len(lines) <= 2:
            lines.append("    EmptyNode[No Node Connections]")

        return "\n".join(lines)
