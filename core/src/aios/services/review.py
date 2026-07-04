import abc
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional
from aios.services.base import ServiceLifecycle


class ReviewCategory(Enum):
    """Enumerate review domains evaluated by the Review Engine."""
    ARCHITECTURE = "Architecture"
    MAINTAINABILITY = "Maintainability"
    PERFORMANCE = "Performance"
    SECURITY = "Security"
    RELIABILITY = "Reliability"
    TESTING = "Testing"
    DOCUMENTATION = "Documentation"
    COMPLEXITY = "Complexity"
    DEPENDENCY_RISK = "Dependency Risk"
    BACKWARD_COMPATIBILITY = "Backward Compatibility"
    OPERATIONAL_READINESS = "Operational Readiness"
    FUTURE_SCALABILITY = "Future Scalability"


class ReviewSeverity(Enum):
    """Enumerate finding impact levels."""
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class ReviewEvidence:
    """Aggregated evidence details backing a review finding."""
    source: str
    evidence_type: str
    data: Dict[str, Any]
    timestamp: float


@dataclass
class ReviewRecommendation:
    """Actionable remediation steps addressing review finding diagnostics."""
    recommendation_id: str
    description: str
    actionable_steps: List[str] = field(default_factory=list)


@dataclass
class ReviewFinding:
    """Diagnostic discover details compiled during code review."""
    finding_id: str
    category: ReviewCategory
    severity: ReviewSeverity
    confidence: float
    description: str
    evidence: List[ReviewEvidence] = field(default_factory=list)
    recommendation: ReviewRecommendation = field(default_factory=lambda: ReviewRecommendation("", ""))
    related_components: List[str] = field(default_factory=list)
    related_files: List[str] = field(default_factory=list)
    blocking: bool = False


@dataclass
class ReviewSummary:
    """Executive metrics summary detailing overall review outcomes."""
    summary_id: str
    executive_summary: str
    overall_health: str  # "healthy", "degraded", "critical"
    risk_summary: str
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    blocking_issues: List[str] = field(default_factory=list)
    recommendations: List[ReviewRecommendation] = field(default_factory=list)
    reviewer_confidence: float = 0.0
    timestamp: float = 0.0


@dataclass
class ReviewReport:
    """Aggregated code review outcome report payload."""
    report_id: str
    session_id: str
    workspace_id: str
    summary: ReviewSummary
    findings: List[ReviewFinding] = field(default_factory=list)
    timestamp: float = 0.0


@dataclass
class ReviewSession:
    """Lifecycle tracking for an active code review evaluation run."""
    session_id: str
    workspace_id: str
    package_id: str
    report: Optional[ReviewReport]
    status: str  # "open", "closed"
    created_at: float
    closed_at: Optional[float] = None


class ReviewAnalyzer(abc.ABC):
    """Core review analyzer engine auditing packages to discover findings."""

    @abc.abstractmethod
    def analyze_package(self, workspace_id: str, package: Any) -> tuple[ReviewSummary, List[ReviewFinding]]:
        """Scans the package components and returns compiled summary and findings list."""
        pass


class ReviewValidator(abc.ABC):
    """Enforces integrity, completeness, and consistency checks on review findings."""

    @abc.abstractmethod
    def validate_review(self, report: ReviewReport) -> List[str]:
        """Validates consistency and returns warnings list."""
        pass


class ReviewEngine(ServiceLifecycle, abc.ABC):
    """Primary service coordinating reviews, workspace persistence, memory stores, and reports syncs."""

    @abc.abstractmethod
    def run_review(self, workspace_id: str, package: Any) -> ReviewSession:
        """Executes full automated analysis on approval package."""
        pass

    @abc.abstractmethod
    def get_session(self, session_id: str) -> Optional[ReviewSession]:
        """Retrieves session details by id."""
        pass

    @abc.abstractmethod
    def get_history(self, workspace_id: str) -> List[ReviewSummary]:
        """Retrieves past review summary history for workspace."""
        pass

    @abc.abstractmethod
    def store_review_summary(self, session: ReviewSession) -> None:
        """Saves severity statistics and summary in memory. Never saves source code."""
        pass

    @abc.abstractmethod
    def publish_review_report(self, report: ReviewReport) -> None:
        """Publishes sync report to Knowledge Hub on demand."""
        pass
