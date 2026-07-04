import abc
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from aios.services.base import ServiceLifecycle


@dataclass
class RepositoryHealth:
    """Represents health metrics of the repository."""
    file_count: int
    folder_count: int
    test_count: int
    documentation_coverage: float  # Scale of 0.0 to 1.0
    adr_count: int
    readme_coverage: float  # Scale of 0.0 to 1.0
    config_completeness: float  # Scale of 0.0 to 1.0
    statistics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RepositorySummary:
    """Contains full high-level and detailed analysis of a code repository."""
    summary_id: str
    timestamp: float
    high_level_architecture: str
    components: List[str]
    dependencies: Dict[str, List[str]]
    service_graph: Dict[str, Any]
    entry_points: List[str]
    execution_paths: List[str]
    design_patterns: List[str]
    architectural_observations: List[str]
    languages: Dict[str, int]
    frameworks: List[str]
    package_managers: List[str]
    health: RepositoryHealth
    metadata: Dict[str, Any] = field(default_factory=dict)


class RepositoryAnalyzer(abc.ABC):
    """Component to inspect files, structures, configuration, CI/CD, and Docker files."""

    @abc.abstractmethod
    def analyze(self, workspace_root: str) -> Dict[str, Any]:
        """Scans the repository structure, config files, and build pipelines."""
        pass


class ArchitectureAnalyzer(abc.ABC):
    """Component to evaluate high-level layout, components, and execution paths."""

    @abc.abstractmethod
    def analyze(self, workspace_root: str, project_context: Any) -> Dict[str, Any]:
        """Identifies architectural layout, key components, entrypoints, and observations."""
        pass


class DependencyAnalyzer(abc.ABC):
    """Component to map imports, packages, and dependency relations."""

    @abc.abstractmethod
    def analyze(self, workspace_root: str, project_context: Any) -> Dict[str, List[str]]:
        """Extracts dependency relationships between components and modules."""
        pass


class TechnologyAnalyzer(abc.ABC):
    """Component to identify languages, databases, linters, frameworks, and deployment options."""

    @abc.abstractmethod
    def analyze(self, workspace_root: str, project_context: Any) -> Dict[str, Any]:
        """Identifies frameworks, database adapters, test configurations, linters, and clouds."""
        pass


class DocumentationAnalyzer(abc.ABC):
    """Component to analyze documentation files, README completeness, and ADR counts."""

    @abc.abstractmethod
    def analyze(self, workspace_root: str, project_context: Any) -> Dict[str, Any]:
        """Measures documentation coverage, ADR counts, and README files quality details."""
        pass


class WorkspaceIntelligenceService(ServiceLifecycle, abc.ABC):
    """Unified service representing primary repository analysis and project health verification."""

    @abc.abstractmethod
    def analyze_repository(self, workspace_root: str) -> RepositorySummary:
        """Executes full repository analyzers, maps dependencies, and generates summary metrics."""
        pass

    @abc.abstractmethod
    def store_summary_in_memory(self, summary: RepositorySummary) -> None:
        """Stores the structured summary and health metrics inside the memory service."""
        pass

    @abc.abstractmethod
    def publish_to_knowledge_hub(self, summary: RepositorySummary) -> None:
        """Publishes the repository summary report to the Knowledge Hub."""
        pass
