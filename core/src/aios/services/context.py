import abc
from dataclasses import dataclass
from typing import Any, Dict

from aios.services.base import ServiceLifecycle
from aios.services.event_bus import Event


@dataclass(frozen=True)
class WorkspaceContext:
    """Strongly typed representation of the active workspace context."""

    working_directory: str
    git_repo_path: str | None
    git_branch: str | None
    project_root: str
    project_name: str


@dataclass(frozen=True, kw_only=True)
class ContextLoadedEvent(Event):
    """Published immediately after workspace context is successfully detected."""

    context: WorkspaceContext


@dataclass(frozen=True, kw_only=True)
class ContextChangedEvent(Event):
    """Published when the active workspace context changes."""

    old_context: WorkspaceContext | None
    new_context: WorkspaceContext


class ContextService(ServiceLifecycle, abc.ABC):
    """Interface for detecting, resolving, and refreshing workspace context."""

    @abc.abstractmethod
    def detect_context(self) -> WorkspaceContext:
        """Inspects the workspace and resolves context signals."""
        pass

    @abc.abstractmethod
    def get_current_context(self) -> WorkspaceContext | None:
        """Returns the currently active workspace context."""
        pass

    @abc.abstractmethod
    def build_enriched_context(self, query: str, token_budget: int = 4000) -> Dict[str, Any]:
        """Assembles enriched context from runtime, workspace, conversation,

        engineering, research, documentation memories, and recent retrievals.
        """
        pass
