import json
import logging
import time
from pathlib import Path
from typing import Any, List, Optional

from aios.services.engineering_intelligence import (
    AffectedComponent,
    AffectedFile,
    ChangeImpactAnalyzer,
    ChangeRecommendation,
    ComplexityEstimator,
    EngineeringAnalyzer,
    EngineeringIntelligenceService,
    EngineeringPlan,
    EngineeringReport,
    ImplementationPlanner,
    RiskAnalyzer,
)
from aios.services.knowledge_hub import (
    KnowledgeDocument,
    KnowledgeHubService,
)
from aios.services.knowledge_hub import (
    KnowledgeMetadata as KHMetadata,
)
from aios.services.memory import MemoryMetadata, MemoryService, MemoryType
from aios.services.model import LLMRequest, ModelService
from aios.services.workspace_intelligence import (
    CodeIntelligenceService,
    CodeStructureSummary,
    WorkspaceIntelligenceService,
)

logger = logging.getLogger(__name__)


class LocalChangeImpactAnalyzer(ChangeImpactAnalyzer):
    """Rule-based change impact analyzer used as fallback."""

    def analyze_impact(
        self,
        workspace_root: str,
        objective: str,
        code_summary: CodeStructureSummary
    ) -> tuple[List[AffectedFile], List[AffectedComponent]]:
        affected_files = []
        affected_components = []
        
        target_files = list(code_summary.dependency_graph.keys())
        keywords = [w.lower() for w in objective.split() if len(w) > 3]

        # 1. Match files by keyword in filename
        for f in target_files:
            f_name = Path(f).name.lower()
            if any(k in f_name for k in keywords):
                affected_files.append(
                    AffectedFile(
                        file_path=f,
                        change_type="modify",
                        reason=f"File name matches keyword from objective: '{Path(f).name}'"
                    )
                )

        # 2. Match symbols by keyword
        for _name, sym in code_summary.symbols.items():
            sym_name_lower = sym.name.lower()
            if any(k in sym_name_lower for k in keywords):
                affected_components.append(
                    AffectedComponent(
                        name=sym.name,
                        component_type=sym.symbol_type,
                        impact_level="Medium",
                        description=f"Symbol matches objective keyword: '{sym.name}'"
                    )
                )

        # Fallbacks to ensure non-empty results if nothing matched
        if not affected_files and target_files:
            affected_files.append(
                AffectedFile(
                    file_path=target_files[0],
                    change_type="modify",
                    reason="Default file selected for engineering analysis fallback."
                )
            )

        if not affected_components and code_summary.symbols:
            # Pick a fallback class or module
            fallback_sym = list(code_summary.symbols.values())[0]
            affected_components.append(
                AffectedComponent(
                    name=fallback_sym.name,
                    component_type=fallback_sym.symbol_type,
                    impact_level="Low",
                    description="Default symbol selected as representative change target."
                )
            )

        return affected_files, affected_components


class LocalComplexityEstimator(ComplexityEstimator):
    """Rule-based complexity estimator used as fallback."""

    def estimate_complexity(
        self,
        affected_files: List[AffectedFile],
        affected_components: List[AffectedComponent],
        code_summary: CodeStructureSummary
    ) -> tuple[str, float]:
        count = len(affected_files)
        if count <= 1:
            return "Low", 3.0
        elif count <= 3:
            return "Medium", 8.5
        elif count <= 6:
            return "High", 18.0
        else:
            return "Very High", 35.5


class LocalRiskAnalyzer(RiskAnalyzer):
    """Rule-based risk analyzer used as fallback."""

    def analyze_risks(
        self,
        objective: str,
        affected_files: List[AffectedFile],
        affected_components: List[AffectedComponent],
        code_summary: CodeStructureSummary
    ) -> List[str]:
        risks = []
        # General heuristics
        if any(c.component_type == "method" and c.impact_level in ("High", "Critical") for c in affected_components):
            risks.append("Breaking public APIs if class method signatures are modified.")
        
        # Check dependency coupling
        if len(affected_files) > 3:
            risks.append("High coupling risk across multiple code directories.")
            
        # Standard safety risks
        risks.append("Circular dependency risks when introducing cross-module imports.")
        risks.append("Architecture violations if clean boundaries in bootstrap.py are bypassed.")
        risks.append("Missing test coverage if corresponding unit tests are not updated in core/tests.")
        return risks


class LocalImplementationPlanner(ImplementationPlanner):
    """Rule-based implementation planner used as fallback."""

    def generate_plan(
        self,
        objective: str,
        affected_files: List[AffectedFile],
        affected_components: List[AffectedComponent],
        complexity: str,
        risks: List[str],
        code_summary: CodeStructureSummary
    ) -> EngineeringPlan:
        ordered_steps = [
            {
                "step_id": "step_1_design",
                "description": "Define abstract interfaces and contracts.",
                "actions": ["Create or edit service interfaces with abc.ABC definitions."]
            },
            {
                "step_id": "step_2_implement",
                "description": "Implement concrete local manager classes.",
                "actions": ["Develop the manager logic inheriting from abstract base classes."]
            },
            {
                "step_id": "step_3_bootstrap",
                "description": "Wire dependencies in bootstrap.py.",
                "actions": ["Instantiate, initialize, and register the service in Composition Root."]
            },
            {
                "step_id": "step_4_test",
                "description": "Develop and run comprehensive tests.",
                "actions": ["Add tests to core/tests/ and execute pytest."]
            }
        ]

        dependencies = {
            "step_2_implement": ["step_1_design"],
            "step_3_bootstrap": ["step_2_implement"],
            "step_4_test": ["step_3_bootstrap"]
        }

        required_services = ["ModelService", "MemoryService", "WorkspaceIntelligenceService"]
        execution_order = [f.file_path for f in affected_files]
        validation_strategy = (
            "Run the full test suite with coverage targets using: pytest. "
            "Validate that public service registry lookups resolve successfully."
        )

        return EngineeringPlan(
            plan_id=f"plan_{int(time.time())}",
            objective=objective,
            timestamp=time.time(),
            ordered_steps=ordered_steps,
            dependencies=dependencies,
            required_services=required_services,
            risks=risks,
            complexity=complexity,
            estimated_effort_hours=10.0 if complexity == "Medium" else 5.0,
            validation_strategy=validation_strategy,
            recommended_execution_order=execution_order
        )


class LocalEngineeringAnalyzer(EngineeringAnalyzer):
    """Main Engineering Analyzer orchestrating LLM queries and fallbacks."""

    def __init__(
        self,
        code_intel: CodeIntelligenceService,
        model_service: Optional[ModelService] = None
    ) -> None:
        self._code_intel = code_intel
        self._model = model_service
        
        # Rule-based fallback engines
        self._impact_analyzer = LocalChangeImpactAnalyzer()
        self._complexity_estimator = LocalComplexityEstimator()
        self._risk_analyzer = LocalRiskAnalyzer()
        self._planner = LocalImplementationPlanner()

    def analyze_engineering(self, workspace_root: str, objective: str) -> EngineeringReport:
        # Get codebase structure details
        code_summary = self._code_intel.analyze_codebase(workspace_root)
        
        if self._model:
            try:
                target_files = list(code_summary.dependency_graph.keys())[:40]
                public_apis = code_summary.public_apis[:25]
                symbols_summary = []
                for _name, sym in list(code_summary.symbols.items())[:30]:
                    symbols_summary.append(f"{sym.symbol_type} {sym.name} in {sym.file_path}")

                prompt = (
                    "You are the Principal Software Architect for the Personal AI OS.\n"
                    f"Objective: {objective}\n\n"
                    f"Codebase Structure Metadata:\n"
                    f"Files: {target_files}\n"
                    f"Public APIs: {public_apis}\n"
                    f"Symbols: {symbols_summary}\n\n"
                    "Analyze this engineering work objective. Produce a single, pure JSON object (no markdown formatting, no other text) with the following structure:\n"
                    "{\n"
                    "  \"affected_files\": [\n"
                    "    { \"file_path\": \"string\", \"change_type\": \"modify|create|delete|refactor\", \"reason\": \"string\" }\n"
                    "  ],\n"
                    "  \"affected_components\": [\n"
                    "    { \"name\": \"string\", \"component_type\": \"class|method|function|interface|enum|module\", \"impact_level\": \"Low|Medium|High|Critical\", \"description\": \"string\" }\n"
                    "  ],\n"
                    "  \"recommendations\": [\n"
                    "    { \"target\": \"string\", \"recommendation\": \"string\", \"rationale\": \"string\" }\n"
                    "  ],\n"
                    "  \"complexity\": \"Low|Medium|High|Very High\",\n"
                    "  \"estimated_effort_hours\": 4.5,\n"
                    "  \"risks\": [ \"string\" ],\n"
                    "  \"plan\": {\n"
                    "    \"ordered_steps\": [\n"
                    "      { \"step_id\": \"string\", \"description\": \"string\", \"actions\": [\"string\"] }\n"
                    "    ],\n"
                    "    \"dependencies\": { \"step_id_or_component\": [\"dependency_step_id_or_component\"] },\n"
                    "    \"required_services\": [ \"string\" ],\n"
                    "    \"validation_strategy\": \"string\",\n"
                    "    \"recommended_execution_order\": [ \"string\" ]\n"
                    "  }\n"
                    "}"
                )

                res = self._model.execute_request(
                    LLMRequest(
                        prompt=prompt,
                        system_instruction="Output pure JSON only.",
                        task_category="coding",
                        preferences={"JSON_output": True}
                    )
                )
                
                content = res.content.strip()
                if content.startswith("```"):
                    content = content.split("```")[1]
                    if content.startswith("json"):
                        content = content[4:]
                        
                data = json.loads(content)
                
                affected_files = [
                    AffectedFile(
                        file_path=item["file_path"],
                        change_type=item["change_type"],
                        reason=item["reason"]
                    )
                    for item in data.get("affected_files", [])
                ]
                
                affected_components = [
                    AffectedComponent(
                        name=item["name"],
                        component_type=item["component_type"],
                        impact_level=item["impact_level"],
                        description=item["description"]
                    )
                    for item in data.get("affected_components", [])
                ]
                
                recommendations = [
                    ChangeRecommendation(
                        target=item["target"],
                        recommendation=item["recommendation"],
                        rationale=item["rationale"]
                    )
                    for item in data.get("recommendations", [])
                ]
                
                plan_data = data.get("plan", {})
                plan = EngineeringPlan(
                    plan_id=f"plan_{int(time.time())}",
                    objective=objective,
                    timestamp=time.time(),
                    ordered_steps=plan_data.get("ordered_steps", []),
                    dependencies=plan_data.get("dependencies", {}),
                    required_services=plan_data.get("required_services", []),
                    risks=data.get("risks", []),
                    complexity=data.get("complexity", "Medium"),
                    estimated_effort_hours=float(data.get("estimated_effort_hours", 8.0)),
                    validation_strategy=plan_data.get("validation_strategy", "pytest"),
                    recommended_execution_order=plan_data.get("recommended_execution_order", [])
                )
                
                return EngineeringReport(
                    report_id=f"eng_report_{int(time.time())}",
                    objective=objective,
                    timestamp=time.time(),
                    affected_files=affected_files,
                    affected_components=affected_components,
                    recommendations=recommendations,
                    plan=plan
                )
            except Exception as e:
                logger.debug(f"LLM engineering analysis failed: {e}. Falling back to rules.")

        # Heuristic rules fallback
        affected_files, affected_components = self._impact_analyzer.analyze_impact(
            workspace_root, objective, code_summary
        )
        complexity, effort = self._complexity_estimator.estimate_complexity(
            affected_files, affected_components, code_summary
        )
        risks = self._risk_analyzer.analyze_risks(
            objective, affected_files, affected_components, code_summary
        )
        plan = self._planner.generate_plan(
            objective, affected_files, affected_components, complexity, risks, code_summary
        )
        plan.estimated_effort_hours = effort

        recommendations = [
            ChangeRecommendation(
                target=objective,
                recommendation="Review all registry service lookups before initializing class instances.",
                rationale="Composition root dictates strict service registration sequences."
            )
        ]

        return EngineeringReport(
            report_id=f"eng_report_{int(time.time())}",
            objective=objective,
            timestamp=time.time(),
            affected_files=affected_files,
            affected_components=affected_components,
            recommendations=recommendations,
            plan=plan
        )


class LocalEngineeringIntelligenceService(EngineeringIntelligenceService):
    """Concrete Engineering Intelligence service implementation."""

    def __init__(
        self,
        code_intel: CodeIntelligenceService,
        workspace_intel: WorkspaceIntelligenceService,
        memory_service: MemoryService,
        knowledge_hub: Optional[KnowledgeHubService] = None,
        model_service: Optional[ModelService] = None,
        registry: Optional[Any] = None
    ) -> None:
        self._code_intel = code_intel
        self._workspace_intel = workspace_intel
        self._memory = memory_service
        self._knowledge_hub = knowledge_hub
        self._model = model_service
        self._registry = registry
        
        self._analyzer = LocalEngineeringAnalyzer(code_intel, model_service)

    def initialize(self) -> None:
        logger.info("Initializing LocalEngineeringIntelligenceService")

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def generate_report(self, workspace_root: str, objective: str) -> EngineeringReport:
        logger.info(f"Generating engineering report for objective: '{objective}'")
        return self._analyzer.analyze_engineering(workspace_root, objective)

    def store_report(self, report: EngineeringReport) -> None:
        summary_content = (
            f"Engineering Plan for Objective: '{report.objective}'\n"
            f"Complexity: {report.plan.complexity}\n"
            f"Estimated Effort: {report.plan.estimated_effort_hours} hours\n"
            f"Affected Files Count: {len(report.affected_files)}\n"
            f"Validation Strategy: {report.plan.validation_strategy}\n"
            f"Execution Steps: {[s.get('description', '') for s in report.plan.ordered_steps]}"
        )
        self._memory.add_memory(
            content=summary_content,
            memory_type=MemoryType.PROJECT,
            metadata=MemoryMetadata(
                workspace_id="default_workspace",
                session_id="engineering_intelligence_session",
                tags=["engineering_plan", "impact_analysis"],
                importance=2,
                source_subsystem="engineering_intelligence"
            )
        )

    def publish_report(self, report: EngineeringReport) -> None:
        if not self._knowledge_hub:
            logger.warning("Knowledge Hub not registered. Skipping publish.")
            return

        report_md = (
            f"# Engineering Plan: {report.objective}\n\n"
            f"## Summary\n"
            f"- **Complexity**: {report.plan.complexity}\n"
            f"- **Estimated Effort**: {report.plan.estimated_effort_hours} hours\n"
            f"- **Timestamp**: {report.timestamp}\n\n"
            f"## Affected Files\n" + "\n".join([f"- `{f.file_path}` ({f.change_type}): {f.reason}" for f in report.affected_files]) + "\n\n"
            "## Affected Components\n" + "\n".join([f"- `{c.name}` ({c.component_type}) [{c.impact_level}]: {c.description}" for c in report.affected_components]) + "\n\n"
            "## Implementation Plan\n" + "\n".join([f"{idx}. **{step.get('description', '')}**\n   - Actions: {', '.join(step.get('actions', []))}" for idx, step in enumerate(report.plan.ordered_steps, 1)]) + "\n\n"
            "## Risks & Mitigations\n" + "\n".join([f"- {risk}" for risk in report.plan.risks]) + "\n\n"
            f"## Validation Strategy\n{report.plan.validation_strategy}\n"
        )
        
        doc = KnowledgeDocument(
            document_id=f"eng_report_{int(report.timestamp)}",
            title=f"Engineering Plan - {report.objective}",
            content=report_md,
            metadata=KHMetadata(
                unique_id=f"eng_report_{int(report.timestamp)}",
                timestamp=report.timestamp,
                source_subsystem="engineering_intelligence",
                category="Project"
            )
        )
        self._knowledge_hub.sync_document(doc, "notion")
