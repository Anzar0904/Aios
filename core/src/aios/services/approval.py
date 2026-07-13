import abc
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from aios.services.base import ServiceLifecycle


class ApprovalStatus(Enum):
    """Enumerate approval outcomes matching gating criteria."""

    PENDING = "pending"
    APPROVED = "approved"
    APPROVED_WITH_CONDITIONS = "approved_with_conditions"
    PARTIALLY_APPROVED = "partially_approved"
    MANUAL_REVIEW = "manual_review"
    CHANGES_REQUESTED = "changes_requested"
    REJECTED = "rejected"


@dataclass
class ApprovalDecision:
    """Approval decision outcome featuring reasoning and reviewer details."""

    status: ApprovalStatus
    reasoning: str
    reviewer_notes: List[str] = field(default_factory=list)
    timestamp: float = 0.0


@dataclass
class ApprovalEvidence:
    """Aggregated engineering evidence from systems components."""

    source: str  # e.g., "validation_report", "engineering_intelligence"
    evidence_type: str
    data: Dict[str, Any]
    timestamp: float


@dataclass
class ApprovalRule(abc.ABC):
    """Abstract rule interface evaluating approval package inputs."""

    rule_name: str
    description: str

    @abc.abstractmethod
    def evaluate(self, package: "ApprovalPackage") -> tuple[bool, str]:
        """Evaluates compliance, returning (passed, reason)."""
        pass


@dataclass
class ApprovalPolicy:
    """Configurable collection of validation and risk rules."""

    policy_id: str
    name: str
    rules: List[ApprovalRule] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ApprovalPackage:
    """Unified container encapsulating all aggregated evidence and summaries."""

    package_id: str
    workspace_id: str
    engineering_summary: str
    validation_summary: Dict[str, Any]
    documentation_summary: Dict[str, Any]
    risk_summary: Dict[str, Any]
    affected_files: List[str]
    affected_components: List[str]
    coverage_summary: Dict[str, Any]
    failure_summary: Dict[str, Any]
    recommendations: List[str]
    policy: ApprovalPolicy
    reviewer_notes: List[str]
    approval_history: List[Any]
    confidence_score: float
    overall_health: str  # "healthy", "degraded", "critical"
    evidence: List[ApprovalEvidence] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ApprovalRequest:
    """Client request initiating a validation gate review process."""

    request_id: str
    workspace_id: str
    target_version: str
    policy_id: str
    evidence: List[ApprovalEvidence] = field(default_factory=list)
    timestamp: float = 0.0


@dataclass
class ApprovalSession:
    """Lifecycle tracking for an active approval evaluation session."""

    session_id: str
    request: ApprovalRequest
    package: Optional[ApprovalPackage]
    decision: Optional[ApprovalDecision]
    status: str  # "open", "closed"
    created_at: float
    closed_at: Optional[float] = None


@dataclass
class ApprovalSummary:
    """Aggregated approval summary details stored inside Memory."""

    summary_id: str
    session_id: str
    workspace_id: str
    status: ApprovalStatus
    confidence_score: float
    overall_health: str
    timestamp: float


@dataclass
class ApprovalHistory:
    """Chronological execution logs trace tracking approval decisions."""

    history_id: str
    workspace_id: str
    records: List[ApprovalSummary] = field(default_factory=list)


@dataclass
class ApprovalReport:
    """Report compiled for external Knowledge Hub syncs."""

    report_id: str
    workspace_id: str
    session_id: str
    decision: ApprovalDecision
    package_summary: Dict[str, Any]
    timestamp: float


class ApprovalValidator(abc.ABC):
    """Enforces structural completeness and compliance constraints."""

    @abc.abstractmethod
    def validate_package(self, package: ApprovalPackage) -> List[str]:
        """Returns validation error list."""
        pass

    @abc.abstractmethod
    def check_duplicate_request(
        self, request: ApprovalRequest, history: List[ApprovalSummary]
    ) -> bool:
        """Returns True if the request is a duplicate."""
        pass


class ApprovalManager(abc.ABC):
    """Orchestrates session creation, packages compiling, and policies evaluation."""

    @abc.abstractmethod
    def create_session(self, request: ApprovalRequest) -> ApprovalSession:
        """Creates a new approval session."""
        pass

    @abc.abstractmethod
    def compile_package(self, session: ApprovalSession) -> ApprovalPackage:
        """Aggregates evidence and compiles the approval package."""
        pass

    @abc.abstractmethod
    def evaluate_policy(self, package: ApprovalPackage) -> ApprovalDecision:
        """Evaluates policy rules and produces an approval decision."""
        pass


class ApprovalEngineService(ServiceLifecycle, abc.ABC):
    """Conductor service managing requests, histories, memory stores, and reports syncs."""

    @abc.abstractmethod
    def request_approval(self, request: ApprovalRequest) -> ApprovalSession:
        """Submits an approval request and runs the full evaluation loop."""
        pass

    @abc.abstractmethod
    def get_session(self, session_id: str) -> Optional[ApprovalSession]:
        """Retrieves an active or completed session."""
        pass

    @abc.abstractmethod
    def get_history(self, workspace_id: str) -> Optional[ApprovalHistory]:
        """Retrieves history of approval runs for a workspace."""
        pass

    @abc.abstractmethod
    def store_approval_summary(self, session: ApprovalSession) -> None:
        """Saves metadata-only approval logs in Memory. Never saves source code."""
        pass

    @abc.abstractmethod
    def publish_approval_report(self, report: ApprovalReport) -> None:
        """Synchronizes report summaries on Notion."""
        pass

    @abc.abstractmethod
    def list_queue(self) -> List[Dict[str, Any]]:
        """List all requests in the approval queue."""
        pass

    @abc.abstractmethod
    def list_pending(self) -> List[Dict[str, Any]]:
        """List all pending requests in the queue."""
        pass

    @abc.abstractmethod
    def approve_request(self, request_id: str) -> bool:
        """Approve a request by ID."""
        pass

    @abc.abstractmethod
    def reject_request(self, request_id: str) -> bool:
        """Reject a request by ID."""
        pass

    @abc.abstractmethod
    def cancel_request(self, request_id: str) -> bool:
        """Cancel a request by ID."""
        pass

    @abc.abstractmethod
    def retry_request(self, request_id: str) -> bool:
        """Retry execution of an approved or failed request."""
        pass

    @abc.abstractmethod
    def execute_request(self, request_id: str) -> Dict[str, Any]:
        """Execute an approved request."""
        pass

    @abc.abstractmethod
    def expire_requests(self) -> None:
        """Expire time-limited pending requests."""
        pass

    @abc.abstractmethod
    def get_policies(self) -> Dict[str, Any]:
        """Get all configured policies."""
        pass

    @abc.abstractmethod
    def update_policy(self, policy_id: str, config: Dict[str, Any]) -> None:
        """Update a policy configuration."""
        pass

    @abc.abstractmethod
    def get_preview(self, request_id: str) -> Dict[str, Any]:
        """Generate or retrieve action preview details."""
        pass

    @abc.abstractmethod
    def list_audit_trail(self) -> List[Dict[str, Any]]:
        """Retrieve audit log items."""
        pass

    @abc.abstractmethod
    def generate_reports(self, output_dir: Optional[Any] = None) -> Dict[str, Any]:
        """Generate markdown reports under docs/approval/."""
        pass

    @abc.abstractmethod
    def classify_risk(self, action: str, details: Dict[str, Any]) -> str:
        """Classify action risk level (low, medium, high, critical)."""
        pass

    @abc.abstractmethod
    def resolve_policy(self, action: str, project: str, client: str) -> str:
        """Resolve policy string for specified action, project, and client."""
        pass

    @abc.abstractmethod
    def log_audit_trail(self, entry: Dict[str, Any]) -> None:
        """Log operational governance event into secure audit logs."""
        pass

    @abc.abstractmethod
    def queue_request_item(self, request_item: Dict[str, Any]) -> None:
        """Persist a new action request item in queue."""
        pass
