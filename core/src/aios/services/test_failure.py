import abc
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List

from aios.services.base import ServiceLifecycle
from aios.services.test_execution import ExecutionSummary
from aios.services.workspace_intelligence import CodeStructureSummary


class FailureSeverity(Enum):
    """Enumerate failure severity classifications."""

    __test__ = False
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class FailureConfidence(Enum):
    """Enumerate failure confidence classifications."""

    __test__ = False
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CERTAIN = "certain"


@dataclass
class FailureSignature:
    """Represents a unique trace of a test execution failure."""

    __test__ = False
    signature_id: str
    error_message: str
    stack_trace: str
    exception_class: str


@dataclass
class FailurePattern:
    """Standard pattern classifying a failure family class."""

    __test__ = False
    pattern_id: str
    pattern_name: str  # "assertion_failure", "import_failure", "syntax_failure", "runtime_exception", "timeout"
    regex_signature: str


@dataclass
class FailureCluster:
    """Groups of similar failures based on pattern classification."""

    __test__ = False
    cluster_id: str
    pattern: FailurePattern
    signatures: List[FailureSignature]


@dataclass
class FailureRecommendation:
    """Actionable recommendation to address identified execution failures."""

    __test__ = False
    recommendation_id: str
    recommendation_type: str  # "additional_tests", "implementation_change", "config_correction", "fixture_fix", "dependency_fix", "documentation", "manual_review"
    description: str
    actionable_steps: List[str]


@dataclass
class FailureAnalysisReport:
    """Assembled report containing clustered failure diagnoses."""

    __test__ = False
    report_id: str
    workspace_id: str
    failed_suites_count: int
    clusters: List[FailureCluster]
    recommendations: List[FailureRecommendation]
    severity: FailureSeverity
    confidence: FailureConfidence
    timestamp: float


class RootCauseAnalyzer(abc.ABC):
    """Analyzes workspace dependencies and logs to isolate failure originations."""

    __test__ = False

    @abc.abstractmethod
    def analyze_root_cause(
        self, execution_summary: ExecutionSummary, code_summary: CodeStructureSummary
    ) -> Dict[str, Any]:
        """Correlates call graphs and log histories to map origin paths."""
        pass


class FailureAnalyzer(abc.ABC):
    """Identifies patterns, exception classes, and stacks signatures."""

    __test__ = False

    @abc.abstractmethod
    def classify_failure(self, raw_output: str) -> FailurePattern:
        """Parses stdout trace logs to classify failure types."""
        pass

    @abc.abstractmethod
    def cluster_failures(self, signatures: List[FailureSignature]) -> List[FailureCluster]:
        """Groups matching traces into signature clusters."""
        pass


class FailureAnalysisService(ServiceLifecycle, abc.ABC):
    """Coordinating diagnosis service executing failure analyses, caching outcomes, and publishing reports."""

    __test__ = False

    @abc.abstractmethod
    def diagnose_failures(
        self,
        workspace_id: str,
        execution_summary: ExecutionSummary,
        code_summary: CodeStructureSummary,
    ) -> FailureAnalysisReport:
        """Runs overall failure analysis diagnostic routines."""
        pass

    @abc.abstractmethod
    def store_failure_report(self, report: FailureAnalysisReport) -> None:
        """Saves failure reports summaries inside Memory."""
        pass

    @abc.abstractmethod
    def publish_failure_report(self, report: FailureAnalysisReport) -> None:
        """Syncs failure report with Knowledge Hub."""
        pass
