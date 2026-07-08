import os
from typing import Any, Dict

from aios.services.engineer.rules import filepath_to_module_path


class ImpactAnalyzer:
    def __init__(self, graph: Any) -> None:
        self.graph = graph

    def analyze(self, entity_name: str) -> Dict[str, Any]:
        # Find file containing the entity
        target_file = None
        ent = self.graph.entities.get(entity_name)
        if ent:
            target_file = ent["file"]

        if not target_file:
            return {"error": f"Entity {entity_name} not found"}

        target_base = os.path.basename(target_file).replace(".py", "")
        target_module = filepath_to_module_path(target_file)

        # Trace dependents (only source files, excluding the target file itself)
        dependents = []
        idx_data = self.graph.index_data.get("index_data", {})
        for filepath, data in idx_data.items():
            if filepath == target_file:
                continue
            # Skip test files in dependents
            if "tests/" in filepath or os.path.basename(filepath).startswith("test_"):
                continue

            for imp in data.get("imports", []):
                if imp == target_module or imp.startswith(target_module + "."):
                    dependents.append(filepath)
                    break

        # Trace tests (both test files importing the module, and test paths containing target_base)
        affected_tests = []
        for filepath, data in idx_data.items():
            if "tests/" in filepath or os.path.basename(filepath).startswith("test_"):
                for imp in data.get("imports", []):
                    if imp == target_module or imp.startswith(target_module + "."):
                        affected_tests.append(filepath)
                        break

        scan_res = self.graph.index_data.get("scan_results", {})
        for t in scan_res.get("tests", []):
            test_path = t["path"]
            if target_base in test_path and test_path not in affected_tests:
                affected_tests.append(test_path)

        risk_score = min(100, 10 + len(dependents) * 15 + len(affected_tests) * 5)

        return {
            "entity": entity_name,
            "file": target_file,
            "dependents": dependents,
            "affected_tests": affected_tests,
            "risk_score": risk_score,
        }
