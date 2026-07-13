import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from aios.brain.context_manager import ContextManager
from aios.brain.models import BrainResponse, Workflow
from aios.brain.planner import BrainPlanner
from aios.brain.provider_selector import ProviderSelector
from aios.brain.skill_selector import SkillSelector
from aios.brain.workflow import WorkflowExecutor
from aios.kernel import Kernel
from aios.services.command import CommandRegistry
from aios.services.context import ContextService
from aios.services.developer_workspace import DeveloperWorkspaceService
from aios.services.memory import MemoryService
from aios.services.model import LLMRequest, ModelService
from aios.services.personal import PersonalService
from aios.services.project_intelligence import ProjectIntelligenceService
from aios.skills.manager import SkillManager
from aios.skills.registry import SkillRegistry


class Brain:
    def __init__(self, kernel: Kernel, command_registry: CommandRegistry) -> None:
        self.kernel = kernel
        self.command_registry = command_registry

        # Resolve services
        self.model_service = kernel.registry.get(ModelService)
        self.memory_service = kernel.registry.get(MemoryService)
        self.context_service = kernel.registry.get(ContextService)

        # Initialize Skill System components for the Brain
        ctx = self.context_service.get_current_context()
        workspace_root = ctx.project_root if ctx else "."
        skills_dir = Path(workspace_root) / "skills"

        self.skill_registry = SkillRegistry()
        self.skill_manager = SkillManager(skills_dir, self.skill_registry)
        self.skill_manager.load_all_skills()

        # Initialize Brain components
        self.skill_selector = SkillSelector(self.skill_registry)
        self.provider_selector = ProviderSelector(self.model_service)
        try:
            project_intel = self.kernel.registry.get(ProjectIntelligenceService)
        except Exception:
            project_intel = None
        try:
            dev_workspace = self.kernel.registry.get(DeveloperWorkspaceService)
        except Exception:
            dev_workspace = None
        try:
            personal_service = self.kernel.registry.get(PersonalService)
        except Exception:
            personal_service = None
        self.context_manager = ContextManager(
            self.context_service, self.memory_service, project_intel, dev_workspace, personal_service
        )
        self.planner = BrainPlanner(self.skill_selector, self.model_service)
        self.workflow_executor = WorkflowExecutor(self.kernel, self.command_registry)

        # State tracking
        self.history: List[Workflow] = []
        self.active_workflow: Optional[Workflow] = None

    def execute(self, query: str, capability: Optional[str] = None) -> BrainResponse:
        # 1. Assemble context
        context = self.context_manager.assemble_context(query)

        # 2. Select Provider/Model
        provider_selection = self.provider_selector.select_provider(query, context)

        # 3. Create Plan / Workflow
        workflow = self.planner.plan(query, context, capability=capability)
        self.active_workflow = workflow
        self.history.append(workflow)

        # 4. Execute Workflow
        success = self.workflow_executor.execute(workflow)

        # 5. Merge Results into a single response
        step_summaries = []
        for step in workflow.steps:
            if step.status == "completed":
                step_summaries.append(f"Step '{step.description}' completed:\n{step.output}")
            else:
                step_summaries.append(f"Step '{step.description}' failed:\n{step.error}")

        if len(workflow.steps) == 1:
            step = workflow.steps[0]
            if step.status == "completed":
                final_response = step.output
            else:
                final_response = f"Workflow failed: {step.error}"
        else:
            # Multi-skill response merge using selected model
            prompt = (
                "You are the Brain coordinator for Personal AI OS.\n"
                f"You planned and executed a multi-step workflow for the user objective: \"{query}\".\n"
                "Here are the outputs from each executed step:\n"
                f"{chr(10).join(step_summaries)}\n\n"
                "Consolidate these outputs into a single, user-friendly response that directly answers the user's objective."
            )
            try:
                res = self.model_service.execute_request(
                    LLMRequest(
                        prompt=prompt,
                        model_name=provider_selection.model_name
                    )
                )
                final_response = res.content
            except Exception as e:
                final_response = (
                    f"Workflow execution completed (success={success}) but failed to merge results: {e}\n\n"
                    + "\n\n".join(step_summaries)
                )

        workflow.completed_at = time.time()

        steps_executed = [
            {
                "step_id": s.step_id,
                "description": s.description,
                "skill_id": s.skill_id,
                "command": s.command,
                "args": s.args,
                "status": s.status,
                "output": s.output,
                "error": s.error,
            }
            for s in workflow.steps
        ]

        return BrainResponse(
            success=success,
            response=final_response,
            workflow_id=workflow.workflow_id,
            steps_executed=steps_executed,
            provider_info={
                "provider_name": provider_selection.provider_name,
                "model_name": provider_selection.model_name,
                "reason": provider_selection.reason,
            },
        )

    def explain(self, query: str, capability: Optional[str] = None) -> Dict[str, Any]:
        """Simulates planning and routing decisions without executing them."""
        context = self.context_manager.assemble_context(query)
        provider_selection = self.provider_selector.select_provider(query, context)
        workflow = self.planner.plan(query, context, capability=capability)
        selections = self.skill_selector.select_skills(query, capability=capability)

        skills_list = [
            {"skill_id": s.skill_id, "confidence": s.confidence, "reason": s.reason}
            for s in selections
        ]

        steps_list = [
            {
                "description": s.description,
                "skill_id": s.skill_id,
                "command": s.command,
                "args": s.args,
            }
            for s in workflow.steps
        ]

        return {
            "objective": query,
            "selected_skills": skills_list,
            "provider": {
                "provider_name": provider_selection.provider_name,
                "model_name": provider_selection.model_name,
                "reason": provider_selection.reason,
            },
            "context": {
                "project_root": context.project_root,
                "project_name": context.project_name,
                "git_branch": context.git_branch,
                "memories_count": len(context.memories),
            },
            "workflow": {
                "workflow_id": workflow.workflow_id,
                "steps": steps_list,
            },
        }
