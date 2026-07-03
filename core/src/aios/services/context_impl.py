import logging
import subprocess
from pathlib import Path

from aios.services.context import (
    ContextChangedEvent,
    ContextLoadedEvent,
    ContextService,
    WorkspaceContext,
)
from aios.services.event_bus import EventBusService

logger = logging.getLogger(__name__)


class LocalContextService(ContextService):
    """
    Concrete implementation of ContextService that resolves environment parameters
    and publishes events on context changes.
    """

    def __init__(self, event_bus: EventBusService) -> None:
        self._event_bus = event_bus
        self._context: WorkspaceContext | None = None

    def initialize(self) -> None:
        logger.info("Initializing LocalContextService")
        self._event_bus.register_event_type(ContextLoadedEvent)
        self._event_bus.register_event_type(ContextChangedEvent)

    def detect_context(self) -> WorkspaceContext:
        """Resolves the current execution context."""
        cwd = Path.cwd().resolve()

        git_repo_path = None
        git_branch = None

        try:
            # Check if git is available and resolve toplevel
            result = subprocess.run(
                ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True
            )
            git_repo_path = str(Path(result.stdout.strip()).resolve())

            # Resolve branch
            branch_result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                capture_output=True,
                text=True,
                check=True,
            )
            git_branch = branch_result.stdout.strip()
        except (subprocess.SubprocessError, FileNotFoundError, OSError) as e:
            # Gracefully handle non-git directory or lack of git binary
            logger.debug(f"Git environment resolution skipped: {e}")

        # Determine project root and name
        project_root = git_repo_path if git_repo_path else str(cwd)
        project_name = Path(project_root).name

        new_context = WorkspaceContext(
            working_directory=str(cwd),
            git_repo_path=git_repo_path,
            git_branch=git_branch,
            project_root=project_root,
            project_name=project_name,
        )

        old_context = self._context
        self._context = new_context

        if old_context is None:
            self._event_bus.publish(ContextLoadedEvent(context=new_context))
        elif old_context != new_context:
            self._event_bus.publish(
                ContextChangedEvent(old_context=old_context, new_context=new_context)
            )

        return new_context

    def get_current_context(self) -> WorkspaceContext | None:
        return self._context
