import abc
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
from aios.services.base import ServiceLifecycle


class ApprovalState(Enum):
    """Enumerate states of the approval gating workflow state machine."""
    DRAFT = "Draft"
    SUBMITTED = "Submitted"
    UNDER_REVIEW = "Under Review"
    CHANGES_REQUESTED = "Changes Requested"
    UPDATED = "Updated"
    APPROVED = "Approved"
    APPROVED_WITH_CONDITIONS = "Approved With Conditions"
    PARTIALLY_APPROVED = "Partially Approved"
    REJECTED = "Rejected"
    EXPIRED = "Expired"
    ARCHIVED = "Archived"


VALID_TRANSITIONS = {
    ApprovalState.DRAFT: [ApprovalState.SUBMITTED, ApprovalState.ARCHIVED],
    ApprovalState.SUBMITTED: [ApprovalState.UNDER_REVIEW, ApprovalState.ARCHIVED],
    ApprovalState.UNDER_REVIEW: [
        ApprovalState.CHANGES_REQUESTED,
        ApprovalState.APPROVED,
        ApprovalState.APPROVED_WITH_CONDITIONS,
        ApprovalState.PARTIALLY_APPROVED,
        ApprovalState.REJECTED,
        ApprovalState.ARCHIVED
    ],
    ApprovalState.CHANGES_REQUESTED: [ApprovalState.UPDATED, ApprovalState.ARCHIVED],
    ApprovalState.UPDATED: [ApprovalState.UNDER_REVIEW, ApprovalState.ARCHIVED],
    ApprovalState.APPROVED: [ApprovalState.EXPIRED, ApprovalState.ARCHIVED],
    ApprovalState.APPROVED_WITH_CONDITIONS: [ApprovalState.EXPIRED, ApprovalState.ARCHIVED],
    ApprovalState.PARTIALLY_APPROVED: [ApprovalState.EXPIRED, ApprovalState.ARCHIVED],
    ApprovalState.REJECTED: [ApprovalState.ARCHIVED],
    ApprovalState.EXPIRED: [ApprovalState.ARCHIVED],
    ApprovalState.ARCHIVED: []
}


@dataclass
class ApprovalStateTransition:
    """Immutable transition details tracking state progression."""
    transition_id: str
    from_state: ApprovalState
    to_state: ApprovalState
    actor: str
    reason: str
    timestamp: float


@dataclass
class ApprovalHistoryEntry:
    """Immutable entry containing a session's workflow state transitions list."""
    entry_id: str
    session_id: str
    workspace_id: str
    state_transitions: List[ApprovalStateTransition] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ApprovalDecisionRecord:
    """Consolidated telemetry record for a completed approval session."""
    record_id: str
    session_id: str
    workspace_id: str
    final_state: ApprovalState
    confidence_score: float
    validation_score: float
    coverage_pct: float
    has_critical_failures: bool
    reviewer_count: int
    timestamp: float


@dataclass
class ApprovalStatistics:
    """Statistical summary metrics derived from historical records."""
    total_sessions: int
    approved_count: int
    rejected_count: int
    changes_requested_count: int
    average_confidence: float
    average_validation_score: float
    average_coverage: float
    transition_counts: Dict[str, int] = field(default_factory=dict)


@dataclass
class ApprovalTrend:
    """Temporal progression trend metrics details."""
    trend_id: str
    metric_name: str  # e.g., "validation_score", "coverage"
    direction: str  # "improving", "declining", "stable"
    values_over_time: List[tuple[float, float]] = field(default_factory=list)  # (timestamp, value)


@dataclass
class ApprovalPattern:
    """Identified recurring pattern or blocker discovered from histories."""
    pattern_id: str
    pattern_type: str  # e.g., "repeated_blocker", "documentation_gap"
    description: str
    occurrence_count: int


@dataclass
class ApprovalRecommendationHistory:
    """Historical recommendation compiled from quality patterns audits."""
    recommendation_id: str
    description: str
    source_pattern_id: str
    timestamp: float


@dataclass
class ApprovalHistoryReport:
    """Consolidated report encapsulating statistics, trends, and pattern recommendations."""
    report_id: str
    workspace_id: str
    statistics: ApprovalStatistics
    trends: List[ApprovalTrend] = field(default_factory=list)
    patterns: List[ApprovalPattern] = field(default_factory=list)
    recommendations: List[ApprovalRecommendationHistory] = field(default_factory=list)
    timestamp: float = 0.0


class ApprovalHistoryValidator(abc.ABC):
    """Enforces state transition rules, consistency metrics, and schema integrity."""

    @abc.abstractmethod
    def validate_transition(self, from_state: ApprovalState, to_state: ApprovalState) -> bool:
        """Returns True if transition is valid."""
        pass

    @abc.abstractmethod
    def validate_report(self, report: ApprovalHistoryReport) -> List[str]:
        """Returns validation error list."""
        pass


class ApprovalHistoryAnalyzer(abc.ABC):
    """Audits past decision records to extrapolate statistics, trends, and patterns."""

    @abc.abstractmethod
    def compile_statistics(self, records: List[ApprovalDecisionRecord]) -> ApprovalStatistics:
        """Aggregates decision records into stats metrics."""
        pass

    @abc.abstractmethod
    def analyze_trends(self, records: List[ApprovalDecisionRecord]) -> List[ApprovalTrend]:
        """Computes metric directions over time."""
        pass

    @abc.abstractmethod
    def discover_patterns(self, entries: List[ApprovalHistoryEntry], records: List[ApprovalDecisionRecord]) -> List[ApprovalPattern]:
        """Identifies recurring blocker patterns and gaps."""
        pass


class ApprovalHistoryService(ServiceLifecycle, abc.ABC):
    """Primary service coordinating state transitions, history logs, analytics, and reporting."""

    @abc.abstractmethod
    def create_history_entry(self, workspace_id: str, session_id: str, initial_state: ApprovalState, actor: str) -> ApprovalHistoryEntry:
        """Instantiates a new state-machine history log tracker for a session."""
        pass

    @abc.abstractmethod
    def transition_state(self, workspace_id: str, session_id: str, target_state: ApprovalState, actor: str, reason: str) -> ApprovalHistoryEntry:
        """Transitions state, validating transition guidelines and appending transitions log."""
        pass

    @abc.abstractmethod
    def record_decision(self, record: ApprovalDecisionRecord) -> None:
        """Records a completed session telemetry summary."""
        pass

    @abc.abstractmethod
    def get_history_entry(self, session_id: str) -> Optional[ApprovalHistoryEntry]:
        """Retrieves history transitions for a session."""
        pass

    @abc.abstractmethod
    def get_decision_records(self, workspace_id: str) -> List[ApprovalDecisionRecord]:
        """Retrieves recorded decisions for workspace."""
        pass

    @abc.abstractmethod
    def run_history_analysis(self, workspace_id: str) -> ApprovalHistoryReport:
        """Runs analyzer queries and compiles statistics, trends, and patterns reports."""
        pass

    @abc.abstractmethod
    def store_history_summary(self, workspace_id: str) -> None:
        """Saves metadata trend and statistics to memory. Never stores source code."""
        pass

    @abc.abstractmethod
    def publish_history_report(self, report: ApprovalHistoryReport) -> None:
        """Publishes history report to Knowledge Hub Notion database on demand."""
        pass
