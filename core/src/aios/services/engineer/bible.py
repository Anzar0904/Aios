import json
import os
from typing import Any, Dict, List

from aios.services.base import ServiceLifecycle
from aios.services.engineer.dependency import DependencyAnalyzer
from aios.services.engineer.graph import EngineeringGraph
from aios.services.engineer.impact import ImpactAnalyzer
from aios.services.engineer.rules import ArchitectureRuleEngine


class EngineeringBibleService(ServiceLifecycle):
    def __init__(
        self,
        model_service: Any = None,
        graph: EngineeringGraph = None,
        index_path: str = "docs/index.json",
    ) -> None:
        self.model_service = model_service
        self.graph = graph
        self.index_path = index_path
        self._is_initialized = False

    def initialize(self) -> None:
        if not self.graph:
            if not os.path.exists(self.index_path):
                # Fallback mock empty graph
                self.graph = EngineeringGraph({})
            else:
                with open(self.index_path, "r", encoding="utf-8") as f:
                    self.graph = EngineeringGraph(json.load(f))
        self.graph.build()
        self.dependency_analyzer = DependencyAnalyzer(self.graph)
        self.rule_engine = ArchitectureRuleEngine(self.graph)
        self.impact_analyzer = ImpactAnalyzer(self.graph)
        self._is_initialized = True

    def start(self) -> None:
        pass

    def shutdown(self) -> None:
        pass

    def search(self, query: str) -> List[Dict[str, Any]]:
        results = []
        query_lower = query.lower()
        for name, ent in self.graph.entities.items():
            if query_lower in name.lower() or query_lower in ent["file"].lower():
                results.append(ent)
        return results

    def get_decision_memory(self) -> Dict[str, Any]:
        return {
            "decisions": [
                {
                    "date": "2026-07-07",
                    "decision": (
                        "Freeze AI Core API architectures (Kernel, "
                        "OmniRoute, registries)."
                    ),
                },
                {
                    "date": "2026-07-08",
                    "decision": (
                        "Add incremental repository documentation "
                        "scanner and docintel agent."
                    ),
                },
            ]
        }

    def generate_engineering_context(self, request_desc: str) -> str:
        decisions = self.get_decision_memory()
        violations = self.rule_engine.validate()

        prompt = (
            f"You are the AI OS Engineering Bible Service. Given the request: '{request_desc}', "
            f"provide technical guidelines based on our codebase constraints.\n\n"
            f"Decision Memory: {decisions}\n"
            f"Architecture violations detected: {violations}\n"
        )
        if self.model_service:
            try:
                return self.model_service.execute_prompt(prompt)
            except Exception as e:
                return f"Failed to call LLM model: {e}"
        return (
            "Architecture Constraint Guidelines:\n"
            "- Do not modify frozen core APIs.\n"
            "- Avoid circular dependencies."
        )
