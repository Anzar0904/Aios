import json
from typing import List, Optional

from aios.services.command.registry import CommandRegistry
from aios.services.model import LLMRequest, ModelService
from aios.services.task.models import TaskStep


class TaskPlanner:
    def __init__(
        self,
        registry: CommandRegistry,
        model_service: Optional[ModelService] = None,
    ) -> None:
        self.registry = registry
        self.model_service = model_service

    def plan(self, objective: str) -> List[TaskStep]:
        obj_lower = objective.lower()

        # Rule-based heuristics for common workflows
        if "review" in obj_lower and "release notes" in obj_lower:
            return [
                TaskStep("review repository"),
                TaskStep("review git changes"),
                TaskStep("generate release notes"),
            ]

        # Fallback to LLM planner if model service is available
        if self.model_service:
            all_cmds = [c.name for c in self.registry.list_commands()]

            prompt = (
                "You are the Task Planner for Personal AI OS.\n"
                "Decompose user's objective into sequence of existing commands.\n\n"
                "Available Commands:\n"
                + "\n".join([f"- {c}" for c in all_cmds])
                + "\n\n"
                f'Objective: "{objective}"\n\n'
                "Return strictly a JSON list of command strings. Do not invent commands. "
                "Choose only from the list of available commands. E.g.:\n"
                '["commands developer", "git review"]\n'
            )

            try:
                res = self.model_service.execute_request(
                    LLMRequest(
                        prompt=prompt,
                        system_instruction=(
                            "You are a strict code execution planner. "
                            "Return JSON lists only."
                        ),
                        model_name="claude-3-5-sonnet",
                    )
                )
                text = res.content.strip()
                if "```json" in text:
                    text = text.split("```json")[1].split("```")[0].strip()
                elif "```" in text:
                    text = text.split("```")[1].split("```")[0].strip()

                commands = json.loads(text)
                if isinstance(commands, list):
                    return [
                        TaskStep(c)
                        for c in commands
                        if (
                            c.lower() in all_cmds
                            or any(c.lower().startswith(ac + " ") for ac in all_cmds)
                        )
                    ]
            except Exception:
                pass

        # Simplest backup
        all_cmds = [c.name for c in self.registry.list_commands()]
        steps = []
        for cmd_name in all_cmds:
            if cmd_name in obj_lower:
                steps.append(TaskStep(cmd_name))
        if steps:
            return steps

        return [TaskStep("analyze repository")]
