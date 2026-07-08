from typing import Any, Dict


class EngineeringGraph:
    def __init__(self, index_data: Dict[str, Any]) -> None:
        self.index_data = index_data
        self.entities = {}

    def build(self) -> None:
        idx_data = self.index_data.get("index_data", {})

        # Categorize classes
        for filepath, data in idx_data.items():
            for cls in data.get("classes", []):
                name = cls["name"]
                bases = cls.get("bases", [])
                is_dataclass = cls.get("is_dataclass", False)
                is_enum = cls.get("is_enum", False)

                entity_type = "class"
                if name.endswith("Service"):
                    entity_type = "service"
                elif name.endswith("Provider"):
                    entity_type = "provider"
                elif name.endswith("Registry"):
                    entity_type = "registry"
                elif name.endswith("Event"):
                    entity_type = "event"
                elif is_dataclass:
                    entity_type = "dataclass"
                elif is_enum:
                    entity_type = "enum"
                elif "ABC" in bases or any("Interface" in b for b in bases):
                    entity_type = "interface"

                self.entities[name] = {
                    "name": name,
                    "type": entity_type,
                    "file": filepath,
                    "docstring": cls.get("docstring", ""),
                    "methods": cls.get("methods", []),
                    "bases": bases
                }
