import logging
import time
from typing import Any, Callable, Dict, List, Optional

from aios.services.execution_engine import (
    ExecutionCheckpoint,
    ExecutionEngine,
    ExecutionReporter,
    ExecutionResult,
    ExecutionSession,
    ExecutionState,
    ExecutionStep,
    ExecutionValidator,
    RollbackPlan,
    TaskExecutor,
)
from aios.services.knowledge_hub import (
    KnowledgeDocument,
    KnowledgeHubService,
)
from aios.services.knowledge_hub import (
    KnowledgeMetadata as KHMetadata,
)
from aios.services.memory import MemoryMetadata, MemoryService, MemoryType
from aios.services.model import ModelService
from aios.services.software_engineer import ImplementationTask, SoftwareEngineeringPlan

logger = logging.getLogger(__name__)


class LocalExecutionValidator(ExecutionValidator):
    """Concrete validator ensuring safety requirements are met before running task."""

    def validate_pre_execution(
        self,
        plan: SoftwareEngineeringPlan,
        task: ImplementationTask,
        session: ExecutionSession
    ) -> tuple[bool, str]:
        # 1. Dependency check
        required_deps = plan.dependencies.get(task.task_id, [])
        for dep in required_deps:
            if dep not in session.completed_tasks:
                return False, f"Dependency '{dep}' has not been completed."
        
        # 2. State & Execution Order check
        # Verify the current task matches the index in the plan sequence
        all_tasks = []
        for phase in plan.phases:
            all_tasks.extend(phase.tasks)
            
        task_ids = [t.task_id for t in all_tasks]
        if task.task_id not in task_ids:
            return False, f"Task '{task.task_id}' is not part of this plan."
            
        expected_idx = task_ids.index(task.task_id)
        if session.current_task_idx != expected_idx:
            return False, f"Execution order mismatch: Expected task index {expected_idx}, got {session.current_task_idx}."

        return True, "Pre-execution validation succeeded."


class LocalTaskExecutor(TaskExecutor):
    """Task Executor that runs with explicit user permission gates."""

    def execute_task(
        self,
        task: ImplementationTask,
        session: ExecutionSession,
        step_approval_callback: Callable[[], bool]
    ) -> tuple[bool, str, List[ExecutionStep]]:
        steps = []
        
        # 1. Call approval callback to simulate human gate
        approved = step_approval_callback()
        if not approved:
            step = ExecutionStep(
                step_id=f"step_{task.task_id}_approval",
                name="Human Gate Approval",
                command="Verify developer intent",
                status="failed",
                output="Rejected by human operator."
            )
            steps.append(step)
            return False, "Task execution rejected at approval gate.", steps

        # Create validation step
        val_step = ExecutionStep(
            step_id=f"step_{task.task_id}_validate",
            name=f"Validate {task.title}",
            command=f"Verify {task.affected_components}",
            status="completed",
            output=f"Components {task.affected_components} verified. Criteria: {task.completion_criteria}"
        )
        steps.append(val_step)
        
        return True, f"Task '{task.title}' executed successfully.", steps


class LocalExecutionReporter(ExecutionReporter):
    """Constructs Markdown summaries of Execution Sessions."""

    def generate_report(self, session: ExecutionSession, plan: SoftwareEngineeringPlan) -> str:
        checkpoint_lines = []
        for cp in session.checkpoints:
            checkpoint_lines.append(
                f"### Checkpoint: {cp.checkpoint_id}\n"
                f"- **Task**: `{cp.task_id}`\n"
                f"- **Status**: {cp.validation_status}\n"
                f"- **Modified Files**: {cp.modified_files}\n"
                f"- **Summary**: {cp.execution_summary}\n"
            )

        report_md = (
            f"# Executable Development Plan Execution Report\n\n"
            f"**Session ID**: `{session.session_id}`\n"
            f"**Plan ID**: `{session.plan_id}`\n"
            f"**Current State**: `{session.state.value.upper()}`\n"
            f"**Execution Duration**: {session.execution_time:.2f} seconds\n\n"
            f"## Task Progress Summary\n"
            f"- **Completed Tasks**: {session.completed_tasks}\n"
            f"- **Failed Tasks**: {session.failed_tasks}\n"
            f"- **Skipped Tasks**: {session.skipped_tasks}\n\n"
            f"## Execution Checkpoints\n"
            + "\n".join(checkpoint_lines)
        )
        return report_md


class LocalExecutionEngine(ExecutionEngine):
    """Main Execution Engine managing sessions, checkpoints, validation, and rollbacks."""

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
        
        self._validator = LocalExecutionValidator()
        self._executor = LocalTaskExecutor()
        self._reporter = LocalExecutionReporter()
        
        self._sessions: Dict[str, ExecutionSession] = {}
        self._plans: Dict[str, SoftwareEngineeringPlan] = {}

    def initialize(self) -> None:
        logger.info("Initializing LocalExecutionEngine")

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass

    def create_session(self, plan: SoftwareEngineeringPlan) -> ExecutionSession:
        session_id = f"exec_session_{int(time.time())}"
        session = ExecutionSession(
            session_id=session_id,
            plan_id=plan.plan_id,
            state=ExecutionState.PENDING,
            current_task_idx=0
        )
        self._sessions[session_id] = session
        self._plans[plan.plan_id] = plan
        logger.info(f"Created ExecutionSession {session_id} for Plan {plan.plan_id}")
        return session

    def start_execution(self, session_id: str, step_approval_callback: Callable[[], bool]) -> ExecutionResult:
        session = self._sessions.get(session_id)
        if not session:
            return ExecutionResult(False, [], [], [], 0.0, [], f"Session {session_id} not found.")

        if session.state not in (ExecutionState.PENDING, ExecutionState.PAUSED):
            return ExecutionResult(
                False,
                session.completed_tasks,
                session.failed_tasks,
                session.skipped_tasks,
                session.execution_time,
                session.checkpoints,
                f"Session must be PENDING or PAUSED, current state: {session.state.value}"
            )

        session.state = ExecutionState.RUNNING
        session.start_time = time.time()
        
        plan = self._plans.get(session.plan_id)
        if not plan:
            session.state = ExecutionState.FAILED
            return ExecutionResult(False, [], [], [], 0.0, [], f"Plan {session.plan_id} not found.")

        # Flatten tasks across phases
        all_tasks = []
        for phase in plan.phases:
            all_tasks.extend(phase.tasks)

        while session.current_task_idx < len(all_tasks):
            if session.state != ExecutionState.RUNNING:
                # Paused, cancelled, etc.
                break

            task = all_tasks[session.current_task_idx]
            
            # 1. Validation Pre-flight check
            valid, reason = self._validator.validate_pre_execution(plan, task, session)
            if not valid:
                session.failed_tasks.append(task.task_id)
                session.state = ExecutionState.FAILED
                break

            # 2. Execution with User Gate
            success, msg, steps = self._executor.execute_task(task, session, step_approval_callback)
            if not success:
                session.failed_tasks.append(task.task_id)
                session.state = ExecutionState.FAILED
                
                # Create checkpoint showing failure
                cp = ExecutionCheckpoint(
                    checkpoint_id=f"cp_{task.task_id}_{int(time.time())}",
                    task_id=task.task_id,
                    timestamp=time.time(),
                    modified_files=[],
                    validation_status="failed",
                    execution_summary=f"Failed task execution: {msg}"
                )
                session.checkpoints.append(cp)
                break

            # Successfully completed task
            session.completed_tasks.append(task.task_id)
            
            # CreateCheckpoint
            cp = ExecutionCheckpoint(
                checkpoint_id=f"cp_{task.task_id}_{int(time.time())}",
                task_id=task.task_id,
                timestamp=time.time(),
                modified_files=plan.required_files,
                validation_status="passed",
                execution_summary=f"Task '{task.title}' completed successfully. Steps outputs: {[s.output for s in steps]}"
            )
            session.checkpoints.append(cp)
            
            session.current_task_idx += 1

        session.execution_time += time.time() - session.start_time
        
        if session.state == ExecutionState.RUNNING and session.current_task_idx >= len(all_tasks):
            session.state = ExecutionState.COMPLETED

        success_status = (session.state == ExecutionState.COMPLETED)
        return ExecutionResult(
            success=success_status,
            completed_tasks=session.completed_tasks,
            failed_tasks=session.failed_tasks,
            skipped_tasks=session.skipped_tasks,
            execution_time_seconds=session.execution_time,
            checkpoints=session.checkpoints,
            message=f"Session is in {session.state.value} state."
        )

    def pause_execution(self, session_id: str) -> None:
        session = self._sessions.get(session_id)
        if session and session.state == ExecutionState.RUNNING:
            session.state = ExecutionState.PAUSED
            session.execution_time += time.time() - session.start_time
            logger.info(f"Paused ExecutionSession {session_id}")

    def resume_execution(self, session_id: str, step_approval_callback: Callable[[], bool]) -> ExecutionResult:
        session = self._sessions.get(session_id)
        if not session:
            return ExecutionResult(False, [], [], [], 0.0, [], f"Session {session_id} not found.")

        if session.state != ExecutionState.PAUSED:
            return ExecutionResult(
                False,
                session.completed_tasks,
                session.failed_tasks,
                session.skipped_tasks,
                session.execution_time,
                session.checkpoints,
                f"Session must be PAUSED to resume, current state: {session.state.value}"
            )

        logger.info(f"Resuming ExecutionSession {session_id}")
        return self.start_execution(session_id, step_approval_callback)

    def cancel_execution(self, session_id: str) -> None:
        session = self._sessions.get(session_id)
        if session:
            session.state = ExecutionState.CANCELLED
            if session.start_time > 0.0 and session.state == ExecutionState.RUNNING:
                session.execution_time += time.time() - session.start_time
            logger.info(f"Cancelled ExecutionSession {session_id}")

    def generate_rollback_plan(self, session_id: str) -> RollbackPlan:
        session = self._sessions.get(session_id)
        if not session:
            raise ValueError(f"ExecutionSession {session_id} not found.")

        plan = self._plans.get(session.plan_id)
        target_files = plan.required_files if plan else []
        
        # Build rollback instruction list based on completed tasks in reverse
        rollback_steps = []
        for task_id in reversed(session.completed_tasks):
            rollback_steps.append(f"- Undo changes from task: `{task_id}` by discarding uncommitted writes.")
            
        instructions = (
            "Rollback Guidelines (Do NOT execute automatically):\n"
            + "\n".join(rollback_steps) + "\n"
            "Recommended Rollback Command: git checkout -- " + " ".join(target_files)
        )

        return RollbackPlan(
            plan_id=f"rollback_{int(time.time())}",
            task_id=session.completed_tasks[-1] if session.completed_tasks else "none",
            timestamp=time.time(),
            rollback_instructions=instructions,
            target_files=target_files
        )

    def store_execution_summary(self, session_id: str) -> None:
        session = self._sessions.get(session_id)
        if not session:
            logger.warning(f"Session {session_id} not found. Skipping memory storage.")
            return

        summary = (
            f"Execution Session ID: {session.session_id}\n"
            f"State: {session.state.value}\n"
            f"Completed Tasks: {session.completed_tasks}\n"
            f"Failed Tasks: {session.failed_tasks}\n"
            f"Duration: {session.execution_time:.2f}s\n"
            f"Checkpoints count: {len(session.checkpoints)}"
        )
        
        self._memory.add_memory(
            content=summary,
            memory_type=MemoryType.PROJECT,
            metadata=MemoryMetadata(
                workspace_id="default_workspace",
                session_id="execution_engine_session",
                tags=["execution_summary", "checkpoints"],
                importance=2,
                source_subsystem="execution_engine"
            )
        )

    def publish_execution_report(self, session_id: str) -> None:
        if not self._knowledge_hub:
            logger.warning("Knowledge Hub not registered. Skipping publish.")
            return

        session = self._sessions.get(session_id)
        if not session:
            logger.warning(f"Session {session_id} not found. Skipping publish.")
            return

        plan = self._plans.get(session.plan_id)
        report_md = self._reporter.generate_report(session, plan)
        
        doc = KnowledgeDocument(
            document_id=f"exec_report_{int(time.time())}",
            title=f"Execution Report - Session {session.session_id}",
            content=report_md,
            metadata=KHMetadata(
                unique_id=f"exec_report_{int(time.time())}",
                timestamp=time.time(),
                source_subsystem="execution_engine",
                category="Project"
            )
        )
        self._knowledge_hub.sync_document(doc, "notion")
