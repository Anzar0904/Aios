import abc
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, List, Optional

from aios.services.base import ServiceLifecycle
from aios.services.software_engineer import ImplementationTask, SoftwareEngineeringPlan


class ExecutionState(Enum):
    """Lifecycle states of a plan execution session."""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ExecutionStep:
    """Represents an individual step or action during task execution."""
    step_id: str
    name: str
    command: str
    status: str  # "pending", "running", "completed", "failed"
    output: Optional[str] = None


@dataclass
class ExecutionCheckpoint:
    """Saves execution state after a task completes, supporting resume and rollback."""
    checkpoint_id: str
    task_id: str
    timestamp: float
    modified_files: List[str]
    validation_status: str  # "passed", "failed"
    execution_summary: str


@dataclass
class RollbackPlan:
    """Prepares instructions to revert changes without autonomously performing edits."""
    plan_id: str
    task_id: str
    timestamp: float
    rollback_instructions: str
    target_files: List[str]


@dataclass
class ExecutionSession:
    """State tracking for a specific plan execution session."""
    session_id: str
    plan_id: str
    state: ExecutionState
    current_task_idx: int
    completed_tasks: List[str] = field(default_factory=list)
    failed_tasks: List[str] = field(default_factory=list)
    skipped_tasks: List[str] = field(default_factory=list)
    checkpoints: List[ExecutionCheckpoint] = field(default_factory=list)
    start_time: float = 0.0
    execution_time: float = 0.0


@dataclass
class ExecutionResult:
    """Unified result payload for session execution completions or state updates."""
    success: bool
    completed_tasks: List[str]
    failed_tasks: List[str]
    skipped_tasks: List[str]
    execution_time_seconds: float
    checkpoints: List[ExecutionCheckpoint]
    message: str


class ExecutionValidator(abc.ABC):
    """Performs pre-flight checks validating repository status, dependencies, and execution orders."""

    @abc.abstractmethod
    def validate_pre_execution(
        self,
        plan: SoftwareEngineeringPlan,
        task: ImplementationTask,
        session: ExecutionSession
    ) -> tuple[bool, str]:
        """Validates that a task is safe to execute based on state and dependency availability."""
        pass


class TaskExecutor(abc.ABC):
    """Executes a single task, asking for explicit human approval for actions."""

    @abc.abstractmethod
    def execute_task(
        self,
        task: ImplementationTask,
        session: ExecutionSession,
        step_approval_callback: Callable[[], bool]
    ) -> tuple[bool, str, List[ExecutionStep]]:
        """Sequentially runs execution actions if human approval callback returns True."""
        pass


class ExecutionReporter(abc.ABC):
    """Generates execution summary logs and Markdown reports."""

    @abc.abstractmethod
    def generate_report(self, session: ExecutionSession, plan: SoftwareEngineeringPlan) -> str:
        """Formulates an execution summary report."""
        pass


class ExecutionEngine(ServiceLifecycle, abc.ABC):
    """Central engine orchestration session lifetimes, checkpoints, validations, and rollbacks."""

    @abc.abstractmethod
    def create_session(self, plan: SoftwareEngineeringPlan) -> ExecutionSession:
        """Initializes a new ExecutionSession tracking a SoftwareEngineeringPlan."""
        pass

    @abc.abstractmethod
    def start_execution(self, session_id: str, step_approval_callback: Callable[[], bool]) -> ExecutionResult:
        """Begins executing tasks in a session."""
        pass

    @abc.abstractmethod
    def pause_execution(self, session_id: str) -> None:
        """Pauses the execution loop."""
        pass

    @abc.abstractmethod
    def resume_execution(self, session_id: str, step_approval_callback: Callable[[], bool]) -> ExecutionResult:
        """Resumes a paused execution session."""
        pass

    @abc.abstractmethod
    def cancel_execution(self, session_id: str) -> None:
        """Cancels a running session."""
        pass

    @abc.abstractmethod
    def generate_rollback_plan(self, session_id: str) -> RollbackPlan:
        """Generates a rollback report mapping changes back to the start of the session."""
        pass

    @abc.abstractmethod
    def store_execution_summary(self, session_id: str) -> None:
        """Saves execution history to Memory Intelligence."""
        pass

    @abc.abstractmethod
    def publish_execution_report(self, session_id: str) -> None:
        """Syncs the execution status report with the Knowledge Hub."""
        pass
