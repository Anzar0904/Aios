import abc
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List

from aios.services.base import ServiceLifecycle
from aios.services.test_coverage import CoverageReport
from aios.services.test_execution import ExecutionSummary
from aios.services.test_failure import FailureAnalysisReport


class ValidationStatus(Enum):
    """Enumerate validation outcomes matching gating thresholds."""

    __test__ = False
    PASS = "pass"
    WARNING = "warning"
    FAIL = "fail"


class ValidationDecision(Enum):
    """Enumerate release decision status outcomes."""

    __test__ = False
    APPROVED = "approved"
    REJECTED = "rejected"
    MANUAL_REVIEW = "manual_review"


@dataclass
class ValidationFinding:
    """Detailed diagnostic discovery during validations."""

    __test__ = False
    finding_id: str
    severity: str  # "Low", "Medium", "High", "Critical"
    description: str
    file_path: str


@dataclass
class ValidationRecommendation:
    """Actionable recommendation to address validation findings."""

    __test__ = False
    recommendation_id: str
    recommendation_type: str
    description: str
    actionable_steps: List[str]


@dataclass
class ValidationEvidence:
    """Supporting telemetry record for validation gates."""

    __test__ = False
    evidence_id: str
    evidence_type: str  # "execution_summary", "coverage_report", "failure_report"
    summary_text: str
    metrics_pct: float


@dataclass
class ValidationGate:
    """Validation gate checking rules based on evidence telemetry."""

    __test__ = False
    gate_name: str
    status: ValidationStatus
    checked_rule: str
    evidence: List[ValidationEvidence] = field(default_factory=list)


@dataclass
class ValidationMetrics:
    """Consolidated statistics across test execution runs and coverage targets."""

    __test__ = False
    overall_score: float
    passed_gates_count: int
    failed_gates_count: int
    total_tests_run: int
    failed_tests_run: int
    achieved_coverage_pct: float


@dataclass
class ValidationScore:
    """Detailed score components including weights and penalty counts."""

    __test__ = False
    raw_score: float
    weight_metrics: Dict[str, float]
    confidence_penalty: float


@dataclass
class ValidationSummary:
    """Aggregated validation statistics summary."""

    __test__ = False
    summary_id: str
    workspace_id: str
    overall_status: ValidationStatus
    decision: ValidationDecision
    score: ValidationScore
    timestamp: float


@dataclass
class ValidationReport:
    """Assembled validation report package consumed by future AI OS services."""

    __test__ = False
    report_id: str
    workspace_id: str
    executive_summary: str
    summary: ValidationSummary
    gates: List[ValidationGate]
    findings: List[ValidationFinding]
    recommendations: List[ValidationRecommendation]
    metrics: ValidationMetrics
    timestamp: float


class ValidationService(ServiceLifecycle, abc.ABC):
    """Unified validation compiler synthesizing reports, logging decisions, and publishing summaries."""

    __test__ = False

    @abc.abstractmethod
    def synthesize_validation(
        self,
        workspace_id: str,
        execution_summary: ExecutionSummary,
        coverage_report: CoverageReport,
        failure_report: FailureAnalysisReport,
    ) -> ValidationReport:
        """Assembles authoritative validation report combining executions, coverages, and failure logs."""
        pass

    @abc.abstractmethod
    def store_validation_report(self, report: ValidationReport) -> None:
        """Stores validation summary details inside Memory."""
        pass

    @abc.abstractmethod
    def publish_validation_report(self, report: ValidationReport) -> None:
        """Syncs validation report with Knowledge Hub."""
        pass
