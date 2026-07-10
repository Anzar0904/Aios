import abc
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from aios.services.base import ServiceLifecycle


@dataclass
class ProjectContext:
    project_root: str
    languages: Dict[str, int] = field(default_factory=dict)
    frameworks: List[str] = field(default_factory=list)
    package_managers: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    git_branch: Optional[str] = None
    git_commits: List[str] = field(default_factory=list)
    todo_markers: List[Dict[str, Any]] = field(default_factory=list)
    statistics: Dict[str, Any] = field(default_factory=dict)
    structure: List[str] = field(default_factory=list)
    adr_count: int = 0
    extra: Dict[str, Any] = field(default_factory=dict)


class ProjectIntelligenceService(ServiceLifecycle, abc.ABC):
    @abc.abstractmethod
    def analyze_workspace(self, workspace_root: str) -> ProjectContext:
        """
        Analyzes the workspace, respects gitignore and build targets,
        uses incremental caching for fast rescans, and returns a unified ProjectContext.
        """
        pass

    @abc.abstractmethod
    def list_projects(self) -> List[Dict[str, Any]]:
        """List all registered projects."""
        pass

    @abc.abstractmethod
    def get_project_profile(self, project_id: str) -> Dict[str, Any]:
        """Get the unified Project Profile containing all system integration states."""
        pass

    @abc.abstractmethod
    def discover_project(self, workspace_path: str) -> Dict[str, Any]:
        """Discover frameworks, databases, deployments, workflows, and CI/CD targets."""
        pass

    @abc.abstractmethod
    def get_architecture_map(self, project_id: str) -> Dict[str, Any]:
        """Retrieve modules, services, dependency graphs, and data flows."""
        pass

    @abc.abstractmethod
    def get_health_scorecard(self, project_id: str) -> Dict[str, Any]:
        """Compute metrics for technical debt, test coverage, and documentation depth."""
        pass

    @abc.abstractmethod
    def query_knowledge_graph(self, project_id: str, query: str) -> Dict[str, Any]:
        """Query connections between files, modules, databases, commits, and workflows."""
        pass

    @abc.abstractmethod
    def get_dependency_audit(self, project_id: str) -> Dict[str, Any]:
        """Track version mismatches, security advisories, and upgrade suggestions."""
        pass

    @abc.abstractmethod
    def get_timeline(self, project_id: str) -> Dict[str, Any]:
        """Generate historical timeline merging commits, migrations, deploys, and updates."""
        pass

    @abc.abstractmethod
    def get_risk_analysis(self, project_id: str) -> Dict[str, Any]:
        """Assess risk levels for coverage gaps, security configuration, and drift."""
        pass

    @abc.abstractmethod
    def query_project_memory(self, project_id: str, query: str) -> List[Dict[str, Any]]:
        """Perform semantic retrieval over design decisions and past issue resolutions."""
        pass

    @abc.abstractmethod
    def generate_reports(
        self, project_id: str, output_dir: Optional[Path] = None
    ) -> Dict[str, Any]:
        """Generate markdown documentation reports under docs/project/ directory."""
        pass

    @abc.abstractmethod
    def clear_cache(self) -> None:
        """Invalidate caching layers."""
        pass
