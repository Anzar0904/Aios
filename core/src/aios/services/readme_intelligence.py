import abc
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from aios.services.base import ServiceLifecycle


@dataclass
class READMESection:
    """A single header section content in a README file."""
    __test__ = False
    heading: str
    content: str
    importance: int


@dataclass
class READMETemplate:
    """Target sections sequencing and design rules."""
    __test__ = False
    template_id: str
    sections_order: List[str]
    style_rules: Dict[str, Any]


@dataclass
class READMEArtifact:
    """Represents a generated/updated README artifact."""
    __test__ = False
    artifact_id: str
    workspace_id: str
    content: str
    sections: List[READMESection]
    timestamp: float


@dataclass
class READMESummary:
    """Metadata summary statistics for a README file."""
    __test__ = False
    summary_id: str
    overall_status: str  # "valid", "needs_updates", "invalid"
    sections_count: int
    last_generated: float


@dataclass
class READMEReport:
    """Comprehensive report analyzing discrepancies in an existing README."""
    __test__ = False
    report_id: str
    workspace_id: str
    analysis_summary: str
    missing_sections: List[str]
    outdated_sections: List[str]
    recommended_improvements: List[str]
    timestamp: float


class READMEAnalyzer(abc.ABC):
    """Analyzes workspace structures and current documentation to find gaps."""
    __test__ = False

    @abc.abstractmethod
    def analyze_readme(self, existing_content: str, workspace_metadata: Dict[str, Any]) -> READMEReport:
        """Compares current content to metadata targets to log missing headers."""
        pass


class READMEPlanner(abc.ABC):
    """Plans README sections order matching style conventions."""
    __test__ = False

    @abc.abstractmethod
    def plan_sections(self, report: READMEReport, template: READMETemplate) -> List[READMESection]:
        """Assembles list of sections with target heading priorities."""
        pass


class READMEValidator(abc.ABC):
    """Validates structural formatting and broken links inside markdown files."""
    __test__ = False

    @abc.abstractmethod
    def validate_readme(self, content: str) -> List[str]:
        """Returns validation error logs list."""
        pass


class READMEGenerator(abc.ABC):
    """Formats planning sections list into a single markdown string."""
    __test__ = False

    @abc.abstractmethod
    def generate_readme(self, workspace_id: str, sections: List[READMESection]) -> READMEArtifact:
        """Assembles Markdown content."""
        pass


class READMEUpdater(abc.ABC):
    """Updates targeted sections without overwriting custom modifications."""
    __test__ = False

    @abc.abstractmethod
    def update_readme(self, existing: READMEArtifact, changes: List[READMESection]) -> READMEArtifact:
        """Merges new section changes into an existing artifact."""
        pass


class READMEIntelligenceService(ServiceLifecycle, abc.ABC):
    """Coordinating service executing analyses, updates, and memory synchronizations."""
    __test__ = False

    @abc.abstractmethod
    def analyze_and_generate(
        self,
        workspace_id: str,
        existing_content: str,
        workspace_metadata: Dict[str, Any],
        template: READMETemplate
    ) -> READMEArtifact:
        """Analyzes gaps and generates an updated README artifact."""
        pass

    @abc.abstractmethod
    def store_readme_summary(self, summary: READMESummary) -> None:
        """Stores README summaries inside Memory."""
        pass

    @abc.abstractmethod
    def publish_readme_report(self, report: READMEReport) -> None:
        """Syncs README analysis records with Knowledge Hub."""
        pass
