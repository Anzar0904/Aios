import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

from aios.services.model import LLMRequest, ModelService
from aios.services.memory import MemoryService, MemoryType, MemoryMetadata
from aios.services.knowledge_hub import (
    KnowledgeHubService,
    KnowledgeDocument,
    KnowledgeMetadata as KHMetadata,
)
from aios.services.engineering_intelligence import EngineeringReport
from aios.services.software_engineer import (
    ImplementationTask,
    ValidationStep,
    DevelopmentPhase,
    SoftwareEngineeringPlan,
    FeaturePlanner,
    TaskDecomposer,
    ExecutionPlanner,
    FilePlanner,
    TestingPlanner,
    DocumentationPlanner,
    ImplementationPlanner,
    SoftwareEngineerService,
)
from aios.services.persistence import PersistenceStatus, PersistencePolicy, EngineeringTaskRepository, PlanningRepository

logger = logging.getLogger(__name__)


class LocalFeaturePlanner(FeaturePlanner):
    """Rule-based feature planner fallback."""

    def plan_features(self, objective: str, engineering_report: EngineeringReport) -> List[DevelopmentPhase]:
        task_1 = ImplementationTask(
            task_id="task_1_interface",
            title="Design Interface Structures",
            description="Declare required classes and ServiceContracts with abc.ABC.",
            priority="High",
            estimated_effort_hours=2.0,
            affected_components=[c.name for c in engineering_report.affected_components],
            validation_requirements=["Python abstract compile checks"],
            completion_criteria="Abstract methods are documented and typed."
        )
        task_2 = ImplementationTask(
            task_id="task_2_logic",
            title="Develop Service Logic",
            description="Write concrete class logic inheriting from base contracts.",
            priority="High",
            estimated_effort_hours=4.5,
            affected_components=[f.file_path for f in engineering_report.affected_files],
            validation_requirements=["Unit test execution and imports validation"],
            completion_criteria="Service logic covers all operational edge cases."
        )
        
        phase_1 = DevelopmentPhase(
            phase_id="phase_1_core",
            name="Core Implementation",
            description="Formulate base contracts and concrete logic classes.",
            tasks=[task_1, task_2],
            validation_steps=[
                ValidationStep(
                    step_id="v_1",
                    name="Syntax Check",
                    command="python -m py_compile",
                    expected_result="0 compilation errors"
                )
            ]
        )
        return [phase_1]


class LocalTaskDecomposer(TaskDecomposer):
    """Rule-based task decomposer fallback."""

    def decompose_tasks(self, objective: str, engineering_report: EngineeringReport) -> List[ImplementationTask]:
        return [
            ImplementationTask(
                task_id="task_1_interface",
                title="Design Interface Structures",
                description="Declare required classes and ServiceContracts with abc.ABC.",
                priority="High",
                estimated_effort_hours=2.0,
                affected_components=[c.name for c in engineering_report.affected_components],
                validation_requirements=["Python abstract compile checks"],
                completion_criteria="Abstract methods are documented and typed."
            ),
            ImplementationTask(
                task_id="task_2_logic",
                title="Develop Service Logic",
                description="Write concrete class logic inheriting from base contracts.",
                priority="High",
                estimated_effort_hours=4.5,
                affected_components=[f.file_path for f in engineering_report.affected_files],
                validation_requirements=["Unit test execution and imports validation"],
                completion_criteria="Service logic covers all operational edge cases."
            )
        ]


class LocalExecutionPlanner(ExecutionPlanner):
    """Rule-based execution planner fallback."""

    def plan_execution(
        self,
        tasks: List[ImplementationTask]
    ) -> tuple[List[str], Dict[str, List[str]], str]:
        order = [t.task_id for t in tasks]
        dependencies = {}
        if len(order) >= 2:
            dependencies[order[1]] = [order[0]]
            
        rollback = (
            "1. Discard uncommitted file changes using git checkout/reset.\n"
            "2. Unregister class instances from service registries to avoid stale states."
        )
        return order, dependencies, rollback


class LocalFilePlanner(FilePlanner):
    """Rule-based file planner fallback."""

    def plan_files(self, objective: str, engineering_report: EngineeringReport) -> tuple[List[str], List[str]]:
        files = [f.file_path for f in engineering_report.affected_files]
        migrations = ["No database schema modifications or migrations required."]
        return files, migrations


class LocalTestingPlanner(TestingPlanner):
    """Rule-based testing planner fallback."""

    def plan_testing(self, objective: str, engineering_report: EngineeringReport) -> tuple[List[str], str, str]:
        required_tests = ["core/tests/test_software_engineer.py"]
        validation_strategy = "Execute pytest command locally."
        testing_strategy = "Formulate unit test fixtures and mock remote services."
        return required_tests, validation_strategy, testing_strategy


class LocalDocumentationPlanner(DocumentationPlanner):
    """Rule-based documentation planner fallback."""

    def plan_documentation(self, objective: str, engineering_report: EngineeringReport) -> List[str]:
        return ["PROJECT_STATUS.md", "KNOWLEDGE_BASE.md"]


class LocalImplementationPlanner(ImplementationPlanner):
    """Main implementation planner orchestrating LLM execution and rule fallbacks."""

    def __init__(self, model_service: Optional[ModelService] = None) -> None:
        self._model = model_service
        self._feature_planner = LocalFeaturePlanner()
        self._task_decomposer = LocalTaskDecomposer()
        self._execution_planner = LocalExecutionPlanner()
        self._file_planner = LocalFilePlanner()
        self._testing_planner = LocalTestingPlanner()
        self._doc_planner = LocalDocumentationPlanner()

    def plan_implementation(self, objective: str, engineering_report: EngineeringReport) -> SoftwareEngineeringPlan:
        if self._model:
            try:
                prompt = (
                    "You are the Lead Software Engineer for the Personal AI OS.\n"
                    f"Objective: {objective}\n\n"
                    f"Engineering Assessment Summary:\n"
                    f"- Complexity: {engineering_report.plan.complexity}\n"
                    f"- Estimated effort: {engineering_report.plan.estimated_effort_hours}h\n"
                    f"- Affected files: {[f.file_path for f in engineering_report.affected_files]}\n"
                    f"- Affected components: {[c.name for c in engineering_report.affected_components]}\n"
                    f"- Risks: {engineering_report.plan.risks}\n\n"
                    "Generate a highly detailed, structured software engineering execution plan in pure JSON format (no markdown formatting, no other text) with the following structure:\n"
                    "{\n"
                    "  \"phases\": [\n"
                    "    {\n"
                    "      \"phase_id\": \"string\",\n"
                    "      \"name\": \"string\",\n"
                    "      \"description\": \"string\",\n"
                    "      \"tasks\": [\n"
                    "        {\n"
                    "          \"task_id\": \"string\",\n"
                    "          \"title\": \"string\",\n"
                    "          \"description\": \"string\",\n"
                    "          \"priority\": \"High|Medium|Low\",\n"
                    "          \"estimated_effort_hours\": 2.5,\n"
                    "          \"affected_components\": [\"string\"],\n"
                    "          \"validation_requirements\": [\"string\"],\n"
                    "          \"completion_criteria\": \"string\"\n"
                    "        }\n"
                    "      ],\n"
                    "      \"validation_steps\": [\n"
                    "        { \"step_id\": \"string\", \"name\": \"string\", \"command\": \"string\", \"expected_result\": \"string\" }\n"
                    "      ]\n"
                    "    }\n"
                    "  ],\n"
                    "  \"execution_order\": [ \"string\" ],\n"
                    "  \"required_files\": [ \"string\" ],\n"
                    "  \"dependencies\": { \"task_id\": [\"dependency_task_id\"] },\n"
                    "  \"required_tests\": [ \"string\" ],\n"
                    "  \"documentation_updates\": [ \"string\" ],\n"
                    "  \"migration_requirements\": [ \"string\" ],\n"
                    "  \"rollback_strategy\": \"string\",\n"
                    "  \"verification_strategy\": \"string\",\n"
                    "  \"testing_strategy\": \"string\"\n"
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
                
                phases = []
                for p_data in data.get("phases", []):
                    tasks = [
                        ImplementationTask(
                            task_id=t["task_id"],
                            title=t["title"],
                            description=t["description"],
                            priority=t["priority"],
                            estimated_effort_hours=float(t["estimated_effort_hours"]),
                            affected_components=t["affected_components"],
                            validation_requirements=t["validation_requirements"],
                            completion_criteria=t["completion_criteria"]
                        )
                        for t in p_data.get("tasks", [])
                    ]
                    steps = [
                        ValidationStep(
                            step_id=v["step_id"],
                            name=v["name"],
                            command=v["command"],
                            expected_result=v["expected_result"]
                        )
                        for v in p_data.get("validation_steps", [])
                    ]
                    phases.append(
                        DevelopmentPhase(
                            phase_id=p_data["phase_id"],
                            name=p_data["name"],
                            description=p_data["description"],
                            tasks=tasks,
                            validation_steps=steps
                        )
                    )

                return SoftwareEngineeringPlan(
                    plan_id=f"dev_plan_{int(time.time())}",
                    objective=objective,
                    timestamp=time.time(),
                    phases=phases,
                    execution_order=data.get("execution_order", []),
                    required_files=data.get("required_files", []),
                    dependencies=data.get("dependencies", {}),
                    required_tests=data.get("required_tests", []),
                    documentation_updates=data.get("documentation_updates", []),
                    migration_requirements=data.get("migration_requirements", []),
                    rollback_strategy=data.get("rollback_strategy", ""),
                    verification_strategy=data.get("verification_strategy", ""),
                    testing_strategy=data.get("testing_strategy", "")
                )
            except Exception as e:
                logger.debug(f"LLM software engineering planning failed: {e}. Falling back to rules.")

        # Fallback to rules
        phases = self._feature_planner.plan_features(objective, engineering_report)
        tasks = self._task_decomposer.decompose_tasks(objective, engineering_report)
        order, deps, rollback = self._execution_planner.plan_execution(tasks)
        files, migrations = self._file_planner.plan_files(objective, engineering_report)
        req_tests, val_strat, test_strat = self._testing_planner.plan_testing(objective, engineering_report)
        docs = self._doc_planner.plan_documentation(objective, engineering_report)

        return SoftwareEngineeringPlan(
            plan_id=f"dev_plan_{int(time.time())}",
            objective=objective,
            timestamp=time.time(),
            phases=phases,
            execution_order=order,
            required_files=files,
            dependencies=deps,
            required_tests=req_tests,
            documentation_updates=docs,
            migration_requirements=migrations,
            rollback_strategy=rollback,
            verification_strategy=val_strat,
            testing_strategy=test_strat
        )


class LocalSoftwareEngineerService(SoftwareEngineerService):
    """Concrete implementation of SoftwareEngineerService."""

    def __init__(
        self,
        memory_service: MemoryService,
        knowledge_hub: Optional[KnowledgeHubService] = None,
        model_service: Optional[ModelService] = None,
        registry: Optional[Any] = None
    ) -> None:
        self._memory = memory_service
        self._knowledge_hub = knowledge_hub
        self._model = model_service
        self._registry = registry

        self._planner = LocalImplementationPlanner(model_service)
        self._task_repo = None
        self._planning_repo = None

    def initialize(self) -> None:
        logger.info("Initializing LocalSoftwareEngineerService")
        if self._registry:
            try:
                self._task_repo = self._registry.get(EngineeringTaskRepository)
                self._planning_repo = self._registry.get(PlanningRepository)
            except Exception as e:
                logger.warning(f"Failed to load M3 repositories: {e}")
        else:
            self._task_repo = None
            self._planning_repo = None

    def _get_policy(self) -> PersistencePolicy:
        if self._task_repo and hasattr(self._task_repo, "service") and self._task_repo.service.config:
            return self._task_repo.service.config.policy
        return PersistencePolicy.STRICT

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def create_development_plan(self, objective: str, engineering_report: EngineeringReport) -> SoftwareEngineeringPlan:
        logger.info(f"Creating development plan for: '{objective}'")
        plan = self._planner.plan_implementation(objective, engineering_report)

        if self._planning_repo and self._task_repo:
            policy = self._get_policy()
            try:
                # Save planning session
                plan_mapped = {
                    "id": plan.plan_id if hasattr(plan, "plan_id") else f"plan_{int(plan.timestamp)}",
                    "execution_plan": {
                        "objective": plan.objective,
                        "rollback_strategy": plan.rollback_strategy,
                        "testing_strategy": plan.testing_strategy,
                        "verification_strategy": plan.verification_strategy,
                        "timestamp": plan.timestamp
                    },
                    "decision_tree": {},
                    "architecture_decisions": {},
                    "dependency_graph": {},
                    "planning_statistics": {},
                    "planning_version": 1,
                    "timestamp": plan.timestamp
                }
                res_plan = self._planning_repo.save(plan_mapped)
                if res_plan.status != PersistenceStatus.SUCCESS:
                    if policy == PersistencePolicy.STRICT:
                        raise RuntimeError(f"Strict persistence save failure: {res_plan.message}")
                    else:
                        logger.warning(f"Persistence best-effort fallback: {res_plan.message}")

                # Save individual tasks
                for phase in plan.phases:
                    for task in phase.tasks:
                        task_mapped = {
                            "id": task.task_id,
                            "name": task.title,
                            "description": task.description,
                            "priority": task.priority,
                            "status": "pending",
                            "creation_time": plan.timestamp,
                            "update_time": plan.timestamp,
                            "completion_time": 0.0,
                            "workspace": "default_workspace",
                            "current_phase": phase.name,
                            "assigned_agent": "ai_software_engineer",
                            "dependencies": json.dumps([]),
                            "retry_count": 0,
                            "operation_results": json.dumps({})
                        }
                        res_task = self._task_repo.save(task_mapped)
                        if res_task.status != PersistenceStatus.SUCCESS:
                            if policy == PersistencePolicy.STRICT:
                                raise RuntimeError(f"Strict persistence save failure: {res_task.message}")
                            else:
                                logger.warning(f"Persistence best-effort fallback: {res_task.message}")
            except Exception as e:
                if policy == PersistencePolicy.STRICT:
                    raise RuntimeError(f"Strict persistence save failure: {e}") from e
                logger.warning(f"Database error saving development plan/tasks: {e}.")

        return plan

    def store_development_plan(self, plan: SoftwareEngineeringPlan) -> None:
        task_details = []
        for phase in plan.phases:
            for task in phase.tasks:
                task_details.append(f"- {task.title} ({task.priority}): {task.description}")

        summary_content = (
            f"Software Development Plan for: '{plan.objective}'\n"
            f"Rollback Strategy: {plan.rollback_strategy}\n"
            f"Testing Strategy: {plan.testing_strategy}\n"
            f"Tasks:\n" + "\n".join(task_details)
        )
        
        self._memory.add_memory(
            content=summary_content,
            memory_type=MemoryType.PROJECT,
            metadata=MemoryMetadata(
                workspace_id="default_workspace",
                session_id="software_engineer_session",
                tags=["development_plan", "task_decomposition"],
                importance=2,
                source_subsystem="software_engineer"
            )
        )

    def publish_development_plan(self, plan: SoftwareEngineeringPlan) -> None:
        if not self._knowledge_hub:
            logger.warning("Knowledge Hub not registered. Skipping publish.")
            return

        phases_md = []
        for p in plan.phases:
            tasks_md = []
            for t in p.tasks:
                tasks_md.append(
                    f"### Task: {t.title} ({t.priority})\n"
                    f"- **Description**: {t.description}\n"
                    f"- **Effort**: {t.estimated_effort_hours}h\n"
                    f"- **Completion Criteria**: {t.completion_criteria}\n"
                )
            
            steps_md = []
            for s in p.validation_steps:
                steps_md.append(f"- **{s.name}**: `{s.command}` -> Expect: {s.expected_result}")
                
            phases_md.append(
                f"## Phase: {p.name}\n"
                f"*{p.description}*\n\n"
                + "\n".join(tasks_md) + "\n"
                f"### Phase Validation Steps\n" + "\n".join(steps_md)
            )

        report_md = (
            f"# Software Engineering Execution Plan\n\n"
            f"**Objective**: {plan.objective}\n"
            f"**Timestamp**: {plan.timestamp}\n\n"
            + "\n\n".join(phases_md) + "\n\n"
            f"## Testing & Verification\n"
            f"- **Verification Strategy**: {plan.verification_strategy}\n"
            f"- **Testing Strategy**: {plan.testing_strategy}\n\n"
            f"## Risks & Rollback\n"
            f"- **Rollback Strategy**: {plan.rollback_strategy}\n"
        )

        doc = KnowledgeDocument(
            document_id=f"dev_plan_{int(plan.timestamp)}",
            title=f"Development Plan - {plan.objective}",
            content=report_md,
            metadata=KHMetadata(
                unique_id=f"dev_plan_{int(plan.timestamp)}",
                timestamp=plan.timestamp,
                source_subsystem="software_engineer",
                category="Project"
            )
        )
        self._knowledge_hub.sync_document(doc, "notion")
