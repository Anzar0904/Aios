import logging
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional

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
        self._context_path = Path(".agent/context.json")
        self._context_items = self._load_context_items()

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

    def build_enriched_context(self, query: str, token_budget: int = 4000) -> Dict[str, Any]:
        """Assembles enriched context from various sources."""

        from aios.registry import ServiceRegistry
        from aios.services.persistence import SemanticMemoryManager

        registry = ServiceRegistry._global_registry
        sem_mgr = None
        if registry:
            sem_mgr = registry.get(SemanticMemoryManager)

        runtime_state = {}
        curr_ctx = self.get_current_context()
        if curr_ctx:
            runtime_state = {
                "working_directory": curr_ctx.working_directory,
                "project_root": curr_ctx.project_root,
                "project_name": curr_ctx.project_name,
                "git_branch": curr_ctx.git_branch,
            }

        workspace_mems = []
        conversation_mems = []
        engineering_mems = []
        research_mems = []
        documentation_mems = []
        recent_retrievals = []

        if sem_mgr:
            try:
                workspace_mems = sem_mgr.retrieve_memories("workspace_memory", query, limit=3)
                conversation_mems = sem_mgr.retrieve_memories("conversation_memory", query, limit=3)
                engineering_mems = sem_mgr.retrieve_memories("engineering_memory", query, limit=3)
                research_mems = sem_mgr.retrieve_memories("research_memory", query, limit=3)
                documentation_mems = sem_mgr.retrieve_memories(
                    "documentation_memory", query, limit=3
                )
                recent_retrievals = list(sem_mgr.recent_retrievals)
            except Exception as e:
                logger.warning(f"LocalContextService: Semantic retrieval failed: {e}")

        assembled_parts = [f"Objective query: {query}"]
        assembled_parts.append(f"Runtime Context: {runtime_state}")

        if workspace_mems:
            assembled_parts.append("\n=== Workspace Memories ===")
            for m in workspace_mems:
                assembled_parts.append(f"- {m.get('payload', {}).get('text', '')}")

        if conversation_mems:
            assembled_parts.append("\n=== Conversation Memories ===")
            for m in conversation_mems:
                assembled_parts.append(f"- {m.get('payload', {}).get('text', '')}")

        if engineering_mems:
            assembled_parts.append("\n=== Engineering Memories ===")
            for m in engineering_mems:
                assembled_parts.append(f"- {m.get('payload', {}).get('text', '')}")

        if research_mems:
            assembled_parts.append("\n=== Research Memories ===")
            for m in research_mems:
                assembled_parts.append(f"- {m.get('payload', {}).get('text', '')}")

        if documentation_mems:
            assembled_parts.append("\n=== Documentation Memories ===")
            for m in documentation_mems:
                assembled_parts.append(f"- {m.get('payload', {}).get('text', '')}")

        assembled_text = "\n".join(assembled_parts)
        max_chars = token_budget * 4
        if len(assembled_text) > max_chars:
            assembled_text = assembled_text[:max_chars] + "\n...[TRUNCATED TO FIT BUDGET]..."

        return {
            "assembled_text": assembled_text,
            "runtime_state": runtime_state,
            "workspace_memories": workspace_mems,
            "conversation_memories": conversation_mems,
            "engineering_memories": engineering_mems,
            "research_memories": research_mems,
            "documentation_memories": documentation_mems,
            "recent_retrievals": recent_retrievals,
        }

    def _load_context_items(self) -> Dict[str, str]:
        if self._context_path.is_file():
            try:
                import json

                with open(self._context_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _save_context_items(self) -> None:
        try:
            self._context_path.parent.mkdir(parents=True, exist_ok=True)
            import json

            with open(self._context_path, "w", encoding="utf-8") as f:
                json.dump(self._context_items, f, indent=4)
        except Exception:
            pass

    def get_context_item(self, key: str) -> Optional[str]:
        return self._context_items.get(key.lower())

    def set_context_item(self, key: str, value: str) -> None:
        self._context_items[key.lower()] = value
        self._save_context_items()

    def clear_context(self) -> None:
        self._context_items.clear()
        self._save_context_items()
