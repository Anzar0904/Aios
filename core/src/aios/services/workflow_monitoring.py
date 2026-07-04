import abc
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
from aios.services.base import ServiceLifecycle


class WorkflowExecutionState(str, Enum):
    """Workflow execution outcome/running state."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"
    SKIPPED = "skipped"


@dataclass
class WorkflowExecutionMetrics:
    """Execution timing and metadata telemetries."""
    duration_seconds: float
    latency_seconds: float
    retry_count: int
    cpu_usage_pct: float
    memory_usage_mb: float


@dataclass
class WorkflowExecutionRecord:
    """Consolidated telemetry trace describing a single run session."""
    execution_id: str
    workflow_id: str
    workspace_id: str
    state: WorkflowExecutionState
    metrics: WorkflowExecutionMetrics
    start_time: float
    end_time: Optional[float] = None
    error_message: Optional[str] = None


@dataclass
class WorkflowTelemetry:
    """Container grouping execution trace lists by workflow ID."""
    workflow_id: str
    workspace_id: str
    records: List[WorkflowExecutionRecord] = field(default_factory=list)


@dataclass
class WorkflowAlert:
    """Configure-triggered runtime anomaly warning alert."""
    alert_id: str
    workflow_id: str
    alert_type: str  # "repeated_failure", "long_duration", "high_retry", "health_degradation", "timeout"
    severity: str  # "info", "warning", "critical"
    message: str
    timestamp: float


@dataclass
class WorkflowHealthScore:
    """Workflow structural health evaluation metric."""
    workflow_id: str
    score: float  # 0.0 to 100.0
    reliability: float  # 0.0 to 1.0
    status: str  # "healthy", "warning", "degraded"


@dataclass
class WorkflowStatistics:
    """Compiled timing and rate metrics detailing workflow run aggregates."""
    total_runs: int
    success_rate: float
    failure_rate: float
    retry_rate: float
    average_duration: float
    median_duration: float
    p95_duration: float
    timeout_count: int
    cancelled_count: int
    skipped_count: int


@dataclass
class WorkflowMonitoringReport:
    """Consolidated telemetry summaries payload for syncing or writing."""
    report_id: str
    workspace_id: str
    statistics: Dict[str, WorkflowStatistics] = field(default_factory=dict)
    health_scores: Dict[str, WorkflowHealthScore] = field(default_factory=dict)
    alerts: List[WorkflowAlert] = field(default_factory=list)
    timestamp: float = 0.0


class WorkflowExecutionTracker(abc.ABC):
    """Tracks active trace sessions."""

    @abc.abstractmethod
    def track_execution(self, record: WorkflowExecutionRecord) -> None:
        """Saves run trace."""
        pass

    @abc.abstractmethod
    def get_executions(self, workflow_id: str) -> List[WorkflowExecutionRecord]:
        """Retrieves runs traces."""
        pass


class WorkflowPerformanceAnalyzer(abc.ABC):
    """Compiles statistics, timing medians, and averages."""

    @abc.abstractmethod
    def analyze_performance(self, records: List[WorkflowExecutionRecord]) -> WorkflowStatistics:
        """Returns statistics summary object."""
        pass


class WorkflowFailureAnalyzer(abc.ABC):
    """Analyzes failure rates and detects repeated blockers."""

    @abc.abstractmethod
    def analyze_failures(self, records: List[WorkflowExecutionRecord]) -> List[str]:
        """Identifies recurring errors list."""
        pass


class WorkflowRetryAnalyzer(abc.ABC):
    """Monitors retry triggers rates and delays."""

    @abc.abstractmethod
    def analyze_retries(self, records: List[WorkflowExecutionRecord]) -> Dict[str, Any]:
        """Returns retry analysis metrics."""
        pass


class WorkflowMonitoringValidator(abc.ABC):
    """Checks timestamps sequencing and integrity validation."""

    @abc.abstractmethod
    def validate_telemetry(self, records: List[WorkflowExecutionRecord]) -> List[str]:
        """Validates timestamp orders and consistency checks."""
        pass


class WorkflowMonitoringService(ServiceLifecycle, abc.ABC):
    """Main coordinator tracking executions, generating monitoring reports, and alerts."""

    @abc.abstractmethod
    def record_execution(self, record: WorkflowExecutionRecord) -> None:
        """Records execution trace and updates active summaries."""
        pass

    @abc.abstractmethod
    def get_telemetry_report(self, workspace_id: str) -> WorkflowMonitoringReport:
        """Generates compiled metrics report payload."""
        pass

    @abc.abstractmethod
    def get_alerts(self, workspace_id: str) -> List[WorkflowAlert]:
        """Retrieves active alerts list."""
        pass

    @abc.abstractmethod
    def get_history(self, workspace_id: str) -> List[WorkflowMonitoringReport]:
        """Retrieves completed reports."""
        pass

    @abc.abstractmethod
    def store_monitoring_summary(self, workspace_id: str) -> None:
        """Saves metadata summaries inside memory. Never stores source code/credentials."""
        pass

    @abc.abstractmethod
    def publish_monitoring_report(self, report: WorkflowMonitoringReport) -> None:
        """Synchronizes report details to Notion."""
        pass
