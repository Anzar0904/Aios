import os
from typing import List, Optional

from aios.brain.models import BrainContext
from aios.services.context import ContextService
from aios.services.memory import MemoryService
from aios.services.project_intelligence import ProjectIntelligenceService
from aios.services.developer_workspace import DeveloperWorkspaceService
from aios.services.personal import PersonalService


class ContextManager:
    def __init__(
        self,
        context_service: ContextService,
        memory_service: MemoryService,
        project_intel: Optional[ProjectIntelligenceService] = None,
        dev_workspace: Optional[DeveloperWorkspaceService] = None,
        personal_service: Optional[PersonalService] = None
    ) -> None:
        self.context_service = context_service
        self.memory_service = memory_service
        self.project_intel = project_intel
        self.dev_workspace = dev_workspace
        self.personal_service = personal_service

    def assemble_context(self, objective: str) -> BrainContext:
        ctx = self.context_service.get_current_context()

        project_root = ctx.project_root if ctx else os.getcwd()
        project_name = ctx.project_name if ctx else os.path.basename(project_root)
        git_branch = ctx.git_branch if ctx else None

        memories: List[str] = []
        try:
            # Query memory service by search
            matched_memories = self.memory_service.search_memory(objective)
            memories = [m.content for m in matched_memories]

            # If search memories are empty, try loading workspace memories
            if not memories and ctx and hasattr(ctx, "working_directory"):
                ws_mems = self.memory_service.load_workspace_memory(ctx.working_directory)
                memories = [m.content for m in ws_mems]
        except Exception:
            pass

        extra = {}
        if self.project_intel:
            try:
                proj_context = self.project_intel.analyze_workspace(project_root)
                extra["project_intelligence"] = proj_context
            except Exception:
                pass

        if self.dev_workspace:
            try:
                workspace_info = self.dev_workspace.get_workspace_info(project_root)
                extra["developer_workspace"] = workspace_info
            except Exception:
                pass

        if self.personal_service:
            try:
                personal_ctx = self.personal_service.get_relevant_context(objective)
                extra["personal_intelligence"] = personal_ctx
            except Exception:
                pass

        return BrainContext(
            project_root=project_root,
            project_name=project_name,
            git_branch=git_branch,
            memories=memories,
            system_status="READY",
            extra=extra
        )



