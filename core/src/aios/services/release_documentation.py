import abc
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from aios.services.base import ServiceLifecycle


@dataclass
class ReleaseSummary:
    """Consolidated metrics summary of a software version release."""
    __test__ = False
    version: str
    channel: str  # "alpha", "beta", "rc", "stable"
    release_date: float
    features_count: int
    fixes_count: int
    breaking_changes_count: int


@dataclass
class ReleaseArtifact:
    """Output artifact documentation container (Notes, Changelogs, Guides)."""
    __test__ = False
    artifact_id: str
    workspace_id: str
    version: str
    channel: str
    content: str
    timestamp: float


@dataclass
class ReleaseDocumentationReport:
    """Release validation health check report."""
    __test__ = False
    report_id: str
    workspace_id: str
    validation_passed: bool
    errors: List[str]
    timestamp: float


class ReleaseNotesGenerator(abc.ABC):
    """Formats ReleaseSummary details into standard Markdown Release Notes."""
    __test__ = False

    @abc.abstractmethod
    def generate_release_notes(self, summary: ReleaseSummary, details: Dict[str, Any]) -> str:
        """Assembles Markdown content."""
        pass


class ChangelogGenerator(abc.ABC):
    """Formats commits lists into Keep a Changelog standard format."""
    __test__ = False

    @abc.abstractmethod
    def generate_changelog(self, summary: ReleaseSummary, commits: List[Dict[str, Any]]) -> str:
        """Assembles Markdown content."""
        pass


class MigrationGuideGenerator(abc.ABC):
    """Formats breaking changes instructions into a clean step-by-step migration layout."""
    __test__ = False

    @abc.abstractmethod
    def generate_migration_guide(self, version_from: str, version_to: str, instructions: List[str]) -> str:
        """Assembles Markdown content."""
        pass


class UpgradeGuideGenerator(abc.ABC):
    """Formats deployment steps checklist into standard upgrade guides."""
    __test__ = False

    @abc.abstractmethod
    def generate_upgrade_guide(self, target_version: str, checklist: List[str]) -> str:
        """Assembles Markdown content."""
        pass


class ReleaseValidator(abc.ABC):
    """Validates markdown structure, semantic versioning formats, and duplicate releases entries."""
    __test__ = False

    @abc.abstractmethod
    def validate_release_document(self, artifact: ReleaseArtifact) -> List[str]:
        """Returns validation error list."""
        pass


class ReleaseDocumentPlanner(abc.ABC):
    """Plans release summaries depending on target workspaces and metadata versions."""
    __test__ = False

    @abc.abstractmethod
    def plan_release_documentation(self, workspace_id: str, target_version: str) -> ReleaseSummary:
        """Compiles target release scope metrics."""
        pass


class ReleaseDocumentationService(ServiceLifecycle, abc.ABC):
    """Coordinating service executing generators, validators, and memory summaries stores."""
    __test__ = False

    @abc.abstractmethod
    def create_release_notes(self, workspace_id: str, summary: ReleaseSummary, details: Dict[str, Any]) -> ReleaseArtifact:
        """Builds a Release Notes artifact."""
        pass

    @abc.abstractmethod
    def create_changelog(self, workspace_id: str, summary: ReleaseSummary, commits: List[Dict[str, Any]]) -> ReleaseArtifact:
        """Builds a Changelog artifact."""
        pass

    @abc.abstractmethod
    def create_migration_guide(self, workspace_id: str, version_from: str, version_to: str, instructions: List[str]) -> ReleaseArtifact:
        """Builds a Migration Guide artifact."""
        pass

    @abc.abstractmethod
    def create_upgrade_guide(self, workspace_id: str, target_version: str, checklist: List[str]) -> ReleaseArtifact:
        """Builds an Upgrade Guide artifact."""
        pass

    @abc.abstractmethod
    def store_release_summary(self, artifact: ReleaseArtifact) -> None:
        """Logs summaries metadata in Memory."""
        pass

    @abc.abstractmethod
    def publish_release_report(self, report: ReleaseDocumentationReport) -> None:
        """Pushes updates to Knowledge Hub Notion pages."""
        pass
