import abc
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from aios.services.base import ServiceLifecycle


@dataclass
class DecisionRecord:
    """An individual ADR specification."""
    __test__ = False
    adr_id: str
    title: str
    status: str
    context: str
    decision: str
    alternatives: List[str] = field(default_factory=list)
    consequences: str = ""


@dataclass
class ImplementationSummary:
    """Summary of features and timelines."""
    __test__ = False
    summary_id: str
    features_added: List[str] = field(default_factory=list)
    timeline_steps: List[str] = field(default_factory=list)
    files_modified: List[str] = field(default_factory=list)


@dataclass
class EngineeringTimeline:
    """Timeline details mapping milestone timings."""
    __test__ = False
    timeline_id: str
    milestones: List[str] = field(default_factory=list)
    durations: Dict[str, float] = field(default_factory=dict)


@dataclass
class ChangeSummary:
    """Summary metrics of modified codebase lines."""
    __test__ = False
    change_id: str
    additions_count: int
    deletions_count: int


@dataclass
class ValidationSummary:
    """Summary mapping test executions results."""
    __test__ = False
    validation_id: str
    tests_run_count: int
    passed_count: int
    coverage_percentage: float


@dataclass
class RiskSummary:
    """Risk tiers assessments tags."""
    __test__ = False
    risk_id: str
    risk_level: str
    impacted_areas: List[str] = field(default_factory=list)


@dataclass
class EngineeringDocumentArtifact:
    """Output artifact documentation container."""
    __test__ = False
    artifact_id: str
    workspace_id: str
    content: str
    timestamp: float
    adr_records: List[DecisionRecord] = field(default_factory=list)


@dataclass
class EngineeringDocumentationReport:
    """Executive engineering metrics report."""
    __test__ = False
    report_id: str
    workspace_id: str
    executive_summary: str
    risk_assessment: str
    timestamp: float
    recommendations: List[str] = field(default_factory=list)


class ADRGenerator(abc.ABC):
    """Formats DecisionRecord specs into single Markdown outputs."""
    __test__ = False

    @abc.abstractmethod
    def generate_adr(self, record: DecisionRecord) -> str:
        """Outputs Markdown representations."""
        pass


class EngineeringReportGenerator(abc.ABC):
    """Combines metrics datasets into comprehensive reports."""
    __test__ = False

    @abc.abstractmethod
    def generate_engineering_report(
        self,
        summary: ImplementationSummary,
        validation: ValidationSummary,
        risk: RiskSummary
    ) -> str:
        """Assembles Markdown content."""
        pass


class EngineeringDocumentPlanner(abc.ABC):
    """Plans layout structure matching target style rules."""
    __test__ = False

    @abc.abstractmethod
    def plan_engineering_documents(self, workspace_id: str) -> List[DecisionRecord]:
        """Assembles list of decisions requiring documenting."""
        pass


class EngineeringDocumentValidator(abc.ABC):
    """Validates markdown structure completeness or duplicate ADR indexes."""
    __test__ = False

    @abc.abstractmethod
    def validate_engineering_document(self, artifact: EngineeringDocumentArtifact) -> List[str]:
        """Returns validation error list."""
        pass


class EngineeringDocumentationService(ServiceLifecycle, abc.ABC):
    """Coordinating service planning timelines summaries and publishing metrics."""
    __test__ = False

    @abc.abstractmethod
    def create_adr_document(self, workspace_id: str, record: DecisionRecord) -> EngineeringDocumentArtifact:
        """Builds an ADR document artifact."""
        pass

    @abc.abstractmethod
    def create_engineering_report(
        self,
        workspace_id: str,
        summary: ImplementationSummary,
        validation: ValidationSummary,
        risk: RiskSummary
    ) -> EngineeringDocumentArtifact:
        """Builds an engineering report artifact."""
        pass

    @abc.abstractmethod
    def store_engineering_summary(self, artifact: EngineeringDocumentArtifact) -> None:
        """Logs summaries metadata in Memory."""
        pass

    @abc.abstractmethod
    def publish_engineering_report(self, report: EngineeringDocumentationReport) -> None:
        """Pushes updates to Knowledge Hub Notion pages."""
        pass
