import os
import re
from typing import List
from aios.services.engineer.graph import EngineeringGraph

class DependencyAnalyzer:
    def __init__(self, graph: EngineeringGraph) -> None:
        self.graph = graph

    def _extract_types(self, type_str: str) -> List[str]:
        if not type_str or not isinstance(type_str, str):
            return []
        return re.findall(r"\b\w+\b", type_str)

    def _is_service(self, name: str) -> bool:
        if name in self.graph.entities:
            return self.graph.entities[name].get("type") == "service"
        return name.endswith("Service")

    def _is_provider(self, name: str) -> bool:
        if name in self.graph.entities:
            return self.graph.entities[name].get("type") == "provider"
        return name.endswith("Provider")

    def _is_event(self, name: str) -> bool:
        if name in self.graph.entities:
            return self.graph.entities[name].get("type") == "event"
        return name.endswith("Event")

    def generate_import_graph(self) -> str:
        dot_lines = ["digraph ImportGraph {", '  node [shape=box, fontname="Courier"];']
        idx_data = self.graph.index_data.get("index_data", {})
        
        for filepath, data in idx_data.items():
            mod_name = os.path.basename(filepath).replace(".py", "")
            for imp in data.get("imports", []):
                imp_mod = imp.split(".")[-1]
                dot_lines.append(f'  "{mod_name}" -> "{imp_mod}";')
        
        dot_lines.append("}")
        return "\n".join(dot_lines)

    def generate_service_graph(self) -> str:
        dot_lines = ["digraph ServiceGraph {", '  node [shape=box, fontname="Courier"];']
        edges = set()
        
        for name, entity in self.graph.entities.items():
            if entity.get("type") == "service" or name.endswith("Service"):
                for method in entity.get("methods", []):
                    if method.get("name") == "__init__":
                        for arg in method.get("arguments", []):
                            arg_name = arg.get("name")
                            if arg_name in ("self", "cls"):
                                continue
                            arg_type = arg.get("type")
                            if arg_type:
                                for dep in self._extract_types(arg_type):
                                    if self._is_service(dep) and dep != name:
                                        edges.add((name, dep))
                                        
        for src, dest in sorted(edges):
            dot_lines.append(f'  "{src}" -> "{dest}";')
            
        dot_lines.append("}")
        return "\n".join(dot_lines)

    def generate_event_graph(self) -> str:
        dot_lines = ["digraph EventGraph {", '  node [shape=box, fontname="Courier"];']
        edges = set()
        
        for name, entity in self.graph.entities.items():
            is_evt = entity.get("type") == "event" or name.endswith("Event")
            
            # Event bases
            if is_evt:
                for base in entity.get("bases", []):
                    if self._is_event(base) and base != name:
                        edges.add((base, name))
                        
            # Event references in methods of any class
            for method in entity.get("methods", []):
                for arg in method.get("arguments", []):
                    arg_name = arg.get("name")
                    if arg_name in ("self", "cls"):
                        continue
                    arg_type = arg.get("type")
                    if arg_type:
                        for dep in self._extract_types(arg_type):
                            if self._is_event(dep):
                                edges.add((name, dep))
                                
        for src, dest in sorted(edges):
            dot_lines.append(f'  "{src}" -> "{dest}";')
            
        dot_lines.append("}")
        return "\n".join(dot_lines)

    def generate_provider_graph(self) -> str:
        dot_lines = ["digraph ProviderGraph {", '  node [shape=box, fontname="Courier"];']
        edges = set()
        
        for name, entity in self.graph.entities.items():
            is_prov = entity.get("type") == "provider" or name.endswith("Provider")
            
            # Provider bases
            if is_prov:
                for base in entity.get("bases", []):
                    if (self._is_provider(base) or base.endswith("Interface") or "Base" in base) and base != name:
                        edges.add((base, name))
                        
            # References in methods of any class
            for method in entity.get("methods", []):
                for arg in method.get("arguments", []):
                    arg_name = arg.get("name")
                    if arg_name in ("self", "cls"):
                        continue
                    arg_type = arg.get("type")
                    if arg_type:
                        for dep in self._extract_types(arg_type):
                            if self._is_provider(dep) and dep != name:
                                edges.add((name, dep))
                                
        for src, dest in sorted(edges):
            dot_lines.append(f'  "{src}" -> "{dest}";')
            
        dot_lines.append("}")
        return "\n".join(dot_lines)
