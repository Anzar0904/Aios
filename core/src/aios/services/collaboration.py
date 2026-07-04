import abc
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
from aios.services.base import ServiceLifecycle


class ReviewerRole(Enum):
    """Enumerate configurable human reviewer roles."""
    OWNER = "Owner"
    MAINTAINER = "Maintainer"
    REVIEWER = "Reviewer"
    ARCHITECT = "Architect"
    SECURITY = "Security Reviewer"
    QA = "QA Reviewer"
    OBSERVER = "Observer"


class ReviewAction(Enum):
    """Immutable log actions for collaborative reviews."""
    CREATE = "create"
    COMMENT = "comment"
    REPLY = "reply"
    RESOLVE = "resolve"
    REOPEN = "reopen"
    VOTE = "vote"
    STATUS_CHANGE = "status_change"


@dataclass
class Reviewer:
    """Configurable reviewer profile details containing permissions."""
    reviewer_id: str
    name: str
    role: ReviewerRole
    permissions: List[str] = field(default_factory=list)


@dataclass
class ReviewComment:
    """Individual human review comment linked to structural items."""
    comment_id: str
    author: str
    content: str
    comment_type: str  # "general", "file", "artifact", "validation", "documentation", "finding"
    timestamp: float
    linked_artifacts: List[str] = field(default_factory=list)
    status: str = "active"  # "active", "resolved"
    replies: List["ReviewComment"] = field(default_factory=list)


@dataclass
class ReviewThread:
    """Thread grouping root comments and nested replies."""
    thread_id: str
    root_comment: ReviewComment
    resolution_state: str = "open"  # "open", "resolved"
    resolved_by: Optional[str] = None
    resolved_at: Optional[float] = None


@dataclass
class ReviewVote:
    """Reviewer decision vote capturing rationale details."""
    voter_id: str
    vote_value: str  # "approve", "approve_with_conditions", "request_changes", "reject"
    rationale: str
    timestamp: float


@dataclass
class ReviewAuditLog:
    """Single immutable audit log entry details."""
    log_id: str
    action: ReviewAction
    actor: str
    details: str
    timestamp: float


@dataclass
class ReviewTimeline:
    """Immutable chronological review timeline containing audit items."""
    timeline_id: str
    events: List[ReviewAuditLog] = field(default_factory=list)


@dataclass
class ReviewCheckpoint:
    """State snapshot of active voting and comment statistics."""
    checkpoint_id: str
    version: str
    timestamp: float
    vote_summary: Dict[str, int] = field(default_factory=dict)
    thread_summary: Dict[str, int] = field(default_factory=dict)


@dataclass
class ReviewResolution:
    """Official gate review decision and outcome details."""
    resolution_id: str
    session_id: str
    decision: str
    summary: str
    timestamp: float


@dataclass
class ReviewFeedback:
    """Post-gate reviewer ratings and feedback notes."""
    feedback_id: str
    author: str
    rating: int  # e.g., 1-5 stars
    notes: str
    timestamp: float


@dataclass
class ReviewCollaborationReport:
    """Outcome report detailing thread states, timelines, and audit traces."""
    report_id: str
    workspace_id: str
    session_id: str
    threads: List[ReviewThread] = field(default_factory=list)
    timeline: Optional[ReviewTimeline] = None
    audit_log: List[ReviewAuditLog] = field(default_factory=list)
    vote_summary: Dict[str, int] = field(default_factory=dict)
    timestamp: float = 0.0


class ReviewCollaborationService(ServiceLifecycle, abc.ABC):
    """Primary service coordinating human feedback, threads, votes, and workspace logging."""

    @abc.abstractmethod
    def create_thread(self, workspace_id: str, session_id: str, comment: ReviewComment) -> ReviewThread:
        """Instantiates a new discussion thread."""
        pass

    @abc.abstractmethod
    def reply_to_comment(self, workspace_id: str, thread_id: str, comment_id: str, reply: ReviewComment) -> ReviewComment:
        """Appends nested comment reply inside an active discussion thread."""
        pass

    @abc.abstractmethod
    def resolve_thread(self, workspace_id: str, thread_id: str, resolver: str) -> None:
        """Resolves discussion thread marking resolved status."""
        pass

    @abc.abstractmethod
    def reopen_thread(self, workspace_id: str, thread_id: str, reopener: str) -> None:
        """Reopens discussion thread marking open status."""
        pass

    @abc.abstractmethod
    def cast_vote(self, workspace_id: str, session_id: str, vote: ReviewVote) -> None:
        """Casts vote outcome for active session."""
        pass

    @abc.abstractmethod
    def get_threads(self, workspace_id: str, session_id: str) -> List[ReviewThread]:
        """Retrieves active threads list for active session."""
        pass

    @abc.abstractmethod
    def get_timeline(self, workspace_id: str, session_id: str) -> ReviewTimeline:
        """Retrieves immutable execution timeline for session."""
        pass

    @abc.abstractmethod
    def get_audit_log(self, workspace_id: str, session_id: str) -> List[ReviewAuditLog]:
        """Retrieves append-only audit entries for session."""
        pass

    @abc.abstractmethod
    def store_collaboration_summary(self, workspace_id: str, session_id: str) -> None:
        """Caches metadata and statistics in memory. Never stores source code."""
        pass

    @abc.abstractmethod
    def publish_collaboration_report(self, report: ReviewCollaborationReport) -> None:
        """Publishes details to Notion database on demand."""
        pass
