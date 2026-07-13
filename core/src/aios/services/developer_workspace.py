import abc
from dataclasses import dataclass, field
from typing import Any, Dict, List

from aios.services.base import ServiceLifecycle


@dataclass
class DeveloperWorkspaceInfo:
    git_status: str
    git_diff_summary: str
    staged_files: List[str] = field(default_factory=list)
    unstaged_files: List[str] = field(default_factory=list)
    untracked_files: List[str] = field(default_factory=list)
    detected_tests: List[str] = field(default_factory=list)
    build_systems: List[str] = field(default_factory=list)
    linters: List[str] = field(default_factory=list)
    diagnostics: Dict[str, Any] = field(default_factory=dict)
    extra: Dict[str, Any] = field(default_factory=dict)


class DeveloperWorkspaceService(ServiceLifecycle, abc.ABC):
    @abc.abstractmethod
    def get_workspace_info(self, workspace_root: str) -> DeveloperWorkspaceInfo:
        """Retrieves structured information about the active git state, tests, and configuration."""
        pass

    @abc.abstractmethod
    def execute_safe_command(
        self, command: str, args: List[str], workspace_root: str
    ) -> Dict[str, Any]:
        """Executes a development command (like tests or linting) safely, validating parameters."""
        pass
