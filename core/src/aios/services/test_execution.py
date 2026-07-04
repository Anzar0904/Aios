import abc
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from aios.services.base import ServiceLifecycle


@dataclass
class ExecutionTarget:
    """Represents a test file, class, or method target for execution."""
    __test__ = False
    target_id: str
    file_path: str
    test_class: Optional[str] = None
    test_method: Optional[str] = None


@dataclass
class ExecutionLog:
    """Represents a log line captured during execution."""
    __test__ = False
    timestamp: float
    level: str
    message: str


@dataclass
class ExecutionMetrics:
    """Consolidates execution test count totals."""
    __test__ = False
    total_tests: int
    passed_tests: int
    failed_tests: int
    skipped_tests: int
    duration: float


@dataclass
class ExecutionResult:
    """Assembled execution metrics outcome for a single test target execution."""
    __test__ = False
    target: ExecutionTarget
    success: bool
    exit_code: int
    metrics: ExecutionMetrics
    raw_output: str
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class ExecutionSummary:
    """Aggregated execution details for all execution targets run."""
    __test__ = False
    summary_id: str
    workspace_id: str
    overall_success: bool
    total_duration: float
    total_passed: int
    total_failed: int
    total_skipped: int
    timestamp: float
    results: List[ExecutionResult] = field(default_factory=list)


@dataclass
class ExecutionSession:
    """Tracks active execution session state details."""
    __test__ = False
    session_id: str
    workspace_id: str
    targets: List[ExecutionTarget]
    logs: List[ExecutionLog] = field(default_factory=list)
    summary: Optional[ExecutionSummary] = None


class TestFrameworkAdapter(abc.ABC):
    """Abstract interface defining framework-specific adapters."""
    __test__ = False

    @property
    @abc.abstractmethod
    def framework_name(self) -> str:
        """Returns adapter framework name identifier."""
        pass

    @abc.abstractmethod
    def execute_tests(self, workspace_root: str, targets: List[ExecutionTarget]) -> ExecutionResult:
        """Runs test execution using framework specific process invocation."""
        pass


class TestRunner(abc.ABC):
    """Standard execution runner orchestrating sessions."""
    __test__ = False

    @abc.abstractmethod
    def run_session(self, session: ExecutionSession, workspace_root: str) -> ExecutionSummary:
        """Executes targeted session within the workspace."""
        pass


class TestExecutor(abc.ABC):
    """Primary logic engine managing runner instances."""
    __test__ = False

    @abc.abstractmethod
    def execute(self, workspace_root: str, targets: List[ExecutionTarget]) -> ExecutionSummary:
        """Triggers execution over target list."""
        pass


class TestExecutionService(ServiceLifecycle, abc.ABC):
    """Coordinating service triggering execution runs, caching summaries, and publishing reports."""
    __test__ = False

    @abc.abstractmethod
    def execute_workspace_tests(
        self,
        workspace_id: str,
        workspace_root: str,
        targets: List[ExecutionTarget]
    ) -> ExecutionSummary:
        """Triggers targeted execution flow inside workspace."""
        pass

    @abc.abstractmethod
    def store_execution_summary(self, summary: ExecutionSummary) -> None:
        """Saves execution statistics inside Memory."""
        pass

    @abc.abstractmethod
    def publish_execution_report(self, summary: ExecutionSummary) -> None:
        """Syncs execution summary reports with Knowledge Hub."""
        pass
