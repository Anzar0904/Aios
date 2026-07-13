import json
import logging
import time
from typing import Any, List, Optional

from aios.services.knowledge_hub import (
    KnowledgeDocument,
    KnowledgeHubService,
)
from aios.services.knowledge_hub import (
    KnowledgeMetadata as KHMetadata,
)
from aios.services.memory import MemoryMetadata, MemoryService, MemoryType
from aios.services.model import LLMRequest, ModelService
from aios.services.test_engineer import (
    AITestEngineerService,
    TestCategory,
    TestPlan,
    TestPlanner,
    TestPlanningResult,
    TestPriority,
    TestRequirement,
    TestScope,
    TestStrategy,
    TestSuite,
    TestTarget,
)
from aios.services.workspace_intelligence import CodeStructureSummary

logger = logging.getLogger(__name__)


class LocalTestPlanner(TestPlanner):
    """Rule-based test planning logic to evaluate impact and strategies."""

    def plan_tests(
        self, objective: str, affected_files: List[str], code_summary: CodeStructureSummary
    ) -> TestPlanningResult:
        # Determine strategy based on risk
        has_critical_files = any(
            "kernel" in f or "bootstrap" in f or "security" in f for f in affected_files
        )
        strategy = TestStrategy.STRICT if has_critical_files else TestStrategy.STANDARD
        risk = "High" if has_critical_files else "Medium"

        # Select categories
        categories = [
            TestCategory.UNIT,
            TestCategory.STYLE_VALIDATION,
            TestCategory.STATIC_ANALYSIS,
        ]
        obj_lower = objective.lower()
        if "api" in obj_lower or "route" in obj_lower:
            categories.append(TestCategory.API)
        if "database" in obj_lower or "db" in obj_lower or "store" in obj_lower:
            categories.append(TestCategory.DATABASE)
        if "integration" in obj_lower:
            categories.append(TestCategory.INTEGRATION)
        if "security" in obj_lower:
            categories.append(TestCategory.SECURITY)

        # Build test targets
        targets = []
        for idx, f in enumerate(affected_files):
            # Resolve imports in code_summary
            imports = code_summary.dependency_graph.get(f, [])
            is_crit = "kernel" in f or "bootstrap" in f
            targets.append(
                TestTarget(
                    target_id=f"tgt_{idx}_{hash(f) % 1000}",
                    file_path=f,
                    symbols=imports[:5],
                    is_critical=is_crit,
                )
            )

        scope = TestScope(
            targets=targets,
            excluded_targets=[".venv", "node_modules"],
            coverage_goal=90.0 if has_critical_files else 85.0,
            risk_level=risk,
        )

        # Prioritize files: critical files first, then files with heavy dependencies
        prioritized_files = []
        dep_graph = code_summary.dependency_graph

        # Sort targets by dependency count (descending)
        sorted_targets = sorted(
            targets, key=lambda t: len(dep_graph.get(t.file_path, [])), reverse=True
        )
        prioritized_files = [t.file_path for t in sorted_targets]

        # Generate TestSuites
        suites = []
        for idx, cat in enumerate(categories):
            suites.append(
                TestSuite(
                    suite_id=f"suite_{cat.value}_{idx}",
                    name=f"Automated {cat.value.capitalize()} Suite",
                    category=cat,
                    target_files=prioritized_files,
                    estimated_execution_time=1.5 if cat == TestCategory.UNIT else 5.0,
                )
            )

        # Requirements
        requirements = [
            TestRequirement(
                requirement_id="req_cov",
                description=f"Achieve >={scope.coverage_goal}% branch statement coverage.",
                category=TestCategory.UNIT,
                priority=TestPriority.HIGH,
            ),
            TestRequirement(
                requirement_id="req_reg",
                description="Ensure zero regressions across core kernel state test cases.",
                category=TestCategory.REGRESSION,
                priority=TestPriority.CRITICAL,
            ),
        ]

        plan = TestPlan(
            plan_id=f"plan_{int(time.time())}",
            objective=objective,
            strategy=strategy,
            scope=scope,
            suites=suites,
            requirements=requirements,
        )

        checkpoints = [
            "Verify all files syntax check passes.",
            "Run unit suites locally to verify mock completions.",
            "Ensure code coverage meets designated target before patch approval.",
        ]

        sequence = [s.suite_id for s in suites]

        return TestPlanningResult(
            result_id=f"plan_res_{int(time.time())}",
            plan=plan,
            ordered_execution_sequence=sequence,
            validation_checkpoints=checkpoints,
            timestamp=time.time(),
        )


class LocalAITestEngineerService(AITestEngineerService):
    """Primary Test Engineer coordinating plans, caching results, and publishing reports."""

    def __init__(
        self,
        memory_service: MemoryService,
        knowledge_hub: Optional[KnowledgeHubService] = None,
        model_service: Optional[ModelService] = None,
        registry: Optional[Any] = None,
    ) -> None:
        self._memory = memory_service
        self._knowledge_hub = knowledge_hub
        self._model = model_service
        self._registry = registry

        self._planner = LocalTestPlanner()

    def initialize(self) -> None:
        logger.info("Initializing LocalAITestEngineerService")

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def generate_test_plan(
        self,
        workspace_id: str,
        objective: str,
        affected_files: List[str],
        code_summary: CodeStructureSummary,
    ) -> TestPlanningResult:
        logger.info(f"Generating test plan for objective: '{objective}'")

        # Rule-based generation
        result = self._planner.plan_tests(objective, affected_files, code_summary)

        # If Model Service is present, refine using LLM
        if self._model:
            try:
                target_names = [t.file_path for t in result.plan.scope.targets]
                [c.category.value for c in result.plan.suites]

                prompt = (
                    "You are the Lead Quality Assurance Architect for the Personal AI OS.\n"
                    f"Objective: {objective}\n"
                    f"Staged Changed Files: {target_names}\n"
                    f"Selected testing strategies: {result.plan.strategy.value}\n\n"
                    "Refine the testing checkpoints and requirements. Return a single, pure JSON object:\n"
                    "{\n"
                    '  "validation_checkpoints": [ "string" ],\n'
                    '  "coverage_goal": 90.0,\n'
                    '  "estimated_execution_time_total": 15.5\n'
                    "}"
                )

                response = self._model.execute_request(
                    LLMRequest(
                        prompt=prompt,
                        system_instruction="Output pure JSON only.",
                        task_category="testing",
                        preferences={"JSON_output": True},
                    )
                )

                content = response.content.strip()
                if content.startswith("```"):
                    content = content.split("```")[1]
                    if content.startswith("json"):
                        content = content[4:]

                data = json.loads(content)
                result.validation_checkpoints = data.get(
                    "validation_checkpoints", result.validation_checkpoints
                )
                result.plan.scope.coverage_goal = data.get(
                    "coverage_goal", result.plan.scope.coverage_goal
                )
            except Exception as e:
                logger.debug(f"LLM test refinement failed: {e}. Relying on rule defaults.")

        return result

    def store_test_plan(self, result: TestPlanningResult) -> None:
        summary = (
            f"Test Planning Result - ID: {result.result_id}\n"
            f"Strategy: {result.plan.strategy.value.upper()}\n"
            f"Risk Level: {result.plan.scope.risk_level}\n"
            f"Coverage Goal: {result.plan.scope.coverage_goal}%\n"
            f"Suites Count: {len(result.plan.suites)}\n"
            f"Sequence Queue: {result.ordered_execution_sequence}\n"
            f"Checkpoints: {result.validation_checkpoints}"
        )

        self._memory.add_memory(
            content=summary,
            memory_type=MemoryType.PROJECT,
            metadata=MemoryMetadata(
                workspace_id=result.result_id,
                session_id=result.result_id,
                tags=["test_planning", "validation_strategy"],
                importance=2,
                source_subsystem="test_engineer",
            ),
        )

    def publish_test_plan(self, result: TestPlanningResult) -> None:
        if not self._knowledge_hub:
            logger.warning("Knowledge Hub not registered. Skipping publish.")
            return

        targets_md = []
        for t in result.plan.scope.targets:
            critical_flag = " [CRITICAL]" if t.is_critical else ""
            targets_md.append(f"- `{t.file_path}` (Imports check: {t.symbols}){critical_flag}")

        suites_md = []
        for s in result.plan.suites:
            suites_md.append(
                f"- **{s.name}** ({s.category.value.upper()}) [Est. Time: {s.estimated_execution_time}s]"
            )

        report_md = (
            f"# Engineering Test Plan Report\n\n"
            f"**Plan ID**: `{result.plan.plan_id}`\n"
            f"**Objective**: {result.plan.objective}\n"
            f"**Strategy**: `{result.plan.strategy.value.upper()}`\n"
            f"**Risk Classification**: `{result.plan.scope.risk_level.upper()}`\n"
            f"**Coverage Target**: {result.plan.scope.coverage_goal}%\n\n"
            f"## Targets In Scope\n" + "\n".join(targets_md) + "\n\n"
            "## Prioritized Test Suites\n" + "\n".join(suites_md) + "\n\n"
            "## Validation Checkpoints\n"
            + "\n".join([f"- {cp}" for cp in result.validation_checkpoints])
        )

        doc = KnowledgeDocument(
            document_id=f"test_plan_{result.plan.plan_id}",
            title=f"Test Plan - {result.plan.plan_id}",
            content=report_md,
            metadata=KHMetadata(
                unique_id=f"test_plan_{result.plan.plan_id}",
                timestamp=result.timestamp,
                source_subsystem="test_engineer",
                category="Project",
            ),
        )
        self._knowledge_hub.sync_document(doc, "notion")
