import abc
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

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
