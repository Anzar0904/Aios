import abc
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from aios.services.base import ServiceLifecycle
from aios.services.engineering_profile import DocumentationProfile


class DocumentCategory(Enum):
    """Enumerate documentation category classifications."""

    __test__ = False
    README = "readme"
    CHANGELOG = "changelog"
    API_DOC = "api_doc"
    ARCHITECTURE = "architecture"
    ADR = "adr"
    ENGINEERING_REPORT = "engineering_report"
    VALIDATION_REPORT = "validation_report"
    RELEASE_NOTES = "release_notes"
    MIGRATION_GUIDE = "migration_guide"
    USER_GUIDE = "user_guide"
    DEVELOPER_GUIDE = "developer_guide"


class DocumentSource(Enum):
    """Enumerate artifact inputs source components."""

    __test__ = False
    ENGINEERING_INTEL = "engineering_intel"
    SOFTWARE_ENG = "software_eng"
    PATCH_GEN = "patch_gen"
    VALIDATION_REPORT = "validation_report"
    WORKSPACE_INTEL = "workspace_intel"
    MEMORY_INTEL = "memory_intel"
    KNOWLEDGE_HUB = "knowledge_hub"


@dataclass
class DocumentMetadata:
    """Consolidated metadata tagging a single document."""

    __test__ = False
    doc_id: str
    category: DocumentCategory
    source: DocumentSource
    title: str
    version: str
    author: str
    timestamp: float


@dataclass
class DocumentTemplate:
    """Document template settings outlining target headings structure."""

    __test__ = False
    template_id: str
    name: str
    structure: List[str]


@dataclass
class DocumentArtifact:
    """Represents a generated/registered documentation artifact."""

    __test__ = False
    artifact_id: str
    metadata: DocumentMetadata
    content: str
    template: Optional[DocumentTemplate] = None


@dataclass
class DocumentationWorkspace:
    """Active repository directory mapping configuration settings."""

    __test__ = False
    workspace_id: str
    path: str
    exclude_patterns: List[str] = field(default_factory=list)


@dataclass
class DocumentationSession:
    """Telemetry record tracking documentation generation sessions lifecycle."""

    __test__ = False
    session_id: str
    workspace: DocumentationWorkspace
    status: str  # "initialized", "planning", "completed", "failed"
    start_time: float


@dataclass
class DocumentationResult:
    """Aggregates documentation generation results."""

    __test__ = False
    result_id: str
    session_id: str
    artifacts: List[DocumentArtifact]
    success: bool
    error_message: Optional[str] = None


class DocumentationProfileAdapter:
    """Adapts engineering configurations to documentation-specific parameters."""

    __test__ = False

    def __init__(self, profile: DocumentationProfile) -> None:
        self._profile = profile

    def get_format(self) -> str:
        return self._profile.format

    def should_generate_api(self) -> bool:
        return self._profile.generate_api_docs

    def get_style_rules(self) -> Dict[str, Any]:
        return {"language": "en", "sections": ["header", "body", "footer"]}


class DocumentationPlanner(abc.ABC):
    """Plans template layouts based on target project profiles."""

    __test__ = False

    @abc.abstractmethod
    def plan_documentation(
        self, session: DocumentationSession, profile_adapter: DocumentationProfileAdapter
    ) -> List[DocumentTemplate]:
        """Assembles recommended lists of doc templates."""
        pass


class DocumentationRegistry:
    """Thread-safe registry caching documents and layout templates."""

    __test__ = False

    def __init__(self) -> None:
        self._artifacts: Dict[str, DocumentArtifact] = {}
        self._templates: Dict[str, DocumentTemplate] = {}

    def register_artifact(self, artifact: DocumentArtifact) -> None:
        self._artifacts[artifact.artifact_id] = artifact

    def get_artifact(self, artifact_id: str) -> Optional[DocumentArtifact]:
        return self._artifacts.get(artifact_id)

    def register_template(self, template: DocumentTemplate) -> None:
        self._templates[template.template_id] = template

    def get_template(self, template_id: str) -> Optional[DocumentTemplate]:
        return self._templates.get(template_id)


class DocumentationService(ServiceLifecycle, abc.ABC):
    """Coordinating service organizing document plans and registers."""

    __test__ = False

    @abc.abstractmethod
    def create_session(self, workspace: DocumentationWorkspace) -> DocumentationSession:
        """Initializes a new documentation tracking session."""
        pass

    @abc.abstractmethod
    def plan_session(self, session: DocumentationSession) -> List[DocumentTemplate]:
        """Compiles structure template lists matching target settings."""
        pass

    @abc.abstractmethod
    def register_artifact(self, artifact: DocumentArtifact) -> None:
        """Saves generated doc artifacts inside index registry."""
        pass

    @abc.abstractmethod
    def get_artifact(self, artifact_id: str) -> Optional[DocumentArtifact]:
        """Fetches registered documentation artifact."""
        pass

    @abc.abstractmethod
    def store_documentation_summary(self, result: DocumentationResult) -> None:
        """Stores summaries configurations in Memory."""
        pass

    @abc.abstractmethod
    def publish_documentation_summary(self, result: DocumentationResult) -> None:
        """Syncs documentation summaries with Knowledge Hub."""
        pass
