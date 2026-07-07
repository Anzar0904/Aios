from typing import Any, Dict, List


class DependencyGraphBuilder:
    """Builds package/module dependency trees and generates Mermaid diagrams."""

    def build_graph(
        self, scan_results: Dict[str, Any], index_data: Dict[str, Dict[str, Any]]
    ) -> Dict[str, List[str]]:
        """Constructs an adjacency list of module imports."""
        graph = {}
        for mod, meta in index_data.items():
            if "imports" in meta:
                graph[mod] = []
                for imp in meta["imports"]:
                    # Match against scanned modules to avoid external libs
                    for scanned in scan_results.get("modules", []):
                        if imp.startswith(scanned) and scanned != mod:
                            graph[mod].append(scanned)
        return graph

    def generate_mermaid(self, graph: Dict[str, List[str]]) -> str:
        """Converts adjacency lists to a Mermaid flowchart diagram."""
        lines = ["flowchart TD"]
        seen_nodes = set()

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

        return "\n".join(lines)
