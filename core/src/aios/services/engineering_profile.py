import abc
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from aios.services.base import ServiceLifecycle


@dataclass
class ProjectProfile:
    """Project-specific metadata parameters."""
    __test__ = False
    project_name: str
    version: str
    description: str


@dataclass
class CodingProfile:
    """Language and coding standard definitions."""
    __test__ = False
    language: str
    coding_standards: List[str]
    naming_conventions: Dict[str, str]


@dataclass
class TestingProfile:
    """Testing frameworks configurations and target policies."""
    __test__ = False
    framework: str
    min_statement_coverage: float
    min_branch_coverage: float


@dataclass
class ExecutionProfile:
    """Execution sandbox environments preferences."""
    __test__ = False
    max_timeout_seconds: int
    sandbox_enabled: bool


@dataclass
class DocumentationProfile:
    """Docs formats and generation preferences."""
    __test__ = False
    format: str
    generate_api_docs: bool


@dataclass
class GitHubProfile:
    """Repository organization details."""
    __test__ = False
    org_name: str
    repo_name: str
    default_branch: str


@dataclass
class ReleaseProfile:
    """Versioning methods and auto-release policies."""
    __test__ = False
    auto_release: bool
    versioning_scheme: str


@dataclass
class AutomationProfile:
    """Task automations and retry settings."""
    __test__ = False
    cron_expression: str
    max_retries: int


@dataclass
class WorkspaceProfile:
    """Sandbox workspaces limits and exclusions."""
    __test__ = False
    workspace_root: str
    exclude_patterns: List[str]


@dataclass
class EngineeringProfile:
    """Consolidated profile representing engineering configurations."""
    __test__ = False
    profile_id: str
    project: ProjectProfile
    coding: CodingProfile
    testing: TestingProfile
    execution: ExecutionProfile
    documentation: DocumentationProfile
    github: GitHubProfile
    release: ReleaseProfile
    automation: AutomationProfile
    workspace: WorkspaceProfile
    timestamp: float


class ProfileSerializer(abc.ABC):
    """Serializes profile models to/from JSON or dictionaries."""
    __test__ = False

    @abc.abstractmethod
    def serialize(self, profile: EngineeringProfile) -> Dict[str, Any]:
        """Converts model to dictionary format."""
        pass

    @abc.abstractmethod
    def deserialize(self, data: Dict[str, Any]) -> EngineeringProfile:
        """Converts dictionary to strongly-typed profile."""
        pass


class ProfileLoader(abc.ABC):
    """Retrieves profile files from disk or environmental configs."""
    __test__ = False

    @abc.abstractmethod
    def load_from_file(self, file_path: str) -> Dict[str, Any]:
        """Loads configuration dictionary from path."""
        pass


class ProfileManager(abc.ABC):
    """Merges and validates multiple profiles using precedence matrices."""
    __test__ = False

    @abc.abstractmethod
    def merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """Performs deep merges over profiles configs."""
        pass

    @abc.abstractmethod
    def validate(self, profile: EngineeringProfile) -> List[str]:
        """Runs validation checks, returning list of validation errors."""
        pass


class ProfileRegistry:
    """Thread-safe registry cache for loaded engineering profiles."""
    __test__ = False

    def __init__(self) -> None:
        self._profiles: Dict[str, EngineeringProfile] = {}

    def register(self, profile_id: str, profile: EngineeringProfile) -> None:
        self._profiles[profile_id] = profile

    def get(self, profile_id: str) -> Optional[EngineeringProfile]:
        return self._profiles.get(profile_id)


class EngineeringProfileService(ServiceLifecycle, abc.ABC):
    """Coordinating configurations service managing engineering profiles."""
    __test__ = False

    @abc.abstractmethod
    def get_profile(self, profile_id: str) -> Optional[EngineeringProfile]:
        """Retrieves targeted engineering profile configuration."""
        pass

    @abc.abstractmethod
    def save_profile(self, profile: EngineeringProfile) -> None:
        """Caches engineering profile instance."""
        pass

    @abc.abstractmethod
    def store_profile_summary(self, profile: EngineeringProfile) -> None:
        """Saves profile metadata configuration in Memory."""
        pass

    @abc.abstractmethod
    def publish_profile_summary(self, profile: EngineeringProfile) -> None:
        """Syncs profile specifications with Knowledge Hub."""
        pass
