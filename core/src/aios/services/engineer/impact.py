from typing import Dict, Any, List
import os

class ImpactAnalyzer:
    def __init__(self, graph: Any) -> None:
        self.graph = graph

    def analyze(self, entity_name: str) -> Dict[str, Any]:
        # Find file containing the entity
        target_file = None
        for name, ent in self.graph.entities.items():
            if name == entity_name:
                target_file = ent["file"]
                break

        if not target_file:
            return {"error": f"Entity {entity_name} not found"}

        target_base = os.path.basename(target_file).replace(".py", "")

        # Trace dependents
        dependents = []
        idx_data = self.graph.index_data.get("index_data", {})
        for filepath, data in idx_data.items():
            imports = [imp.split(".")[-1] for imp in data.get("imports", [])]
            if target_base in imports:
                dependents.append(filepath)

        # Trace tests
        affected_tests = []
        scan_res = self.graph.index_data.get("scan_results", {})
        for t in scan_res.get("tests", []):
            test_path = t["path"]
            if target_base in test_path:
                affected_tests.append(test_path)

        risk_score = min(100, 10 + len(dependents) * 15 + len(affected_tests) * 5)

        return {
            "entity": entity_name,
            "file": target_file,
            "dependents": dependents,
            "affected_tests": affected_tests,
            "risk_score": risk_score
        }
