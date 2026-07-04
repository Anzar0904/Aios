import json
import time
import uuid
from typing import Optional

from aios.brain.models import BrainContext, Workflow, WorkflowStep
from aios.brain.skill_selector import SkillSelector
from aios.services.model import LLMRequest, ModelService


class BrainPlanner:
    def __init__(self, skill_selector: SkillSelector, model_service: ModelService) -> None:
        self.skill_selector = skill_selector
        self.model_service = model_service

    def plan(
        self,
        objective: str,
        context: Optional[BrainContext] = None,
        capability: Optional[str] = None
    ) -> Workflow:
        objective_clean = objective.strip()

        # 1. Deterministic Exact Command Match Check
        selections = self.skill_selector.select_skills(objective_clean, capability=capability)
        if selections and selections[0].confidence == 1.0:
            sel = selections[0]
            matched_cmd = None
            for cmd in sel.matched_commands:
                if objective_clean.lower().startswith(cmd.lower()):
                    if matched_cmd is None or len(cmd) > len(matched_cmd):
                        matched_cmd = cmd

            if matched_cmd:
                args = objective_clean[len(matched_cmd):].strip()
                step = WorkflowStep(
                    step_id=f"step_{int(time.time())}_{uuid.uuid4().hex[:4]}",
                    description=f"Execute deterministic command: {matched_cmd}",
                    skill_id=sel.skill_id,
                    command=matched_cmd,
                    args=args,
                    status="pending"
                )
                return Workflow(
                    workflow_id=f"wf_{uuid.uuid4().hex[:6]}",
                    objective=objective_clean,
                    steps=[step],
                    status="pending",
                    created_at=time.time()
                )

        # 2. Multi-skill/Complex flow via LLM
        skills_info = []
        for skill in self.skill_selector.skill_registry.list_skills():
            if skill.enabled:
                skills_info.append({
                    "id": skill.metadata.id,
                    "description": skill.metadata.description,
                    "commands": skill.metadata.commands
                })

        prompt = (
            "You are the Brain Planner for Personal AI OS.\n"
            f"Your task is to decompose the user objective into a sequential list of steps using the available skills.\n\n"
            f"User Objective: \"{objective_clean}\"\n"
            f"Available Skills and their commands:\n"
            f"{json.dumps(skills_info, indent=2)}\n\n"
            "Generate a list of steps. For each step, specify:\n"
            "- description: a user-friendly description of the step\n"
            "- skill_id: the ID of the skill to use\n"
            "- command: the specific command name from the skill's list of commands\n"
            "- args: the arguments string to pass to the command\n\n"
            "Return strictly a JSON list of step definitions. Example:\n"
            "[\n"
            "  {\n"
            '    "description": "Clone the AIOS repo",\n'
            '    "skill_id": "github",\n'
            '    "command": "clone repository",\n'
            '    "args": "Anzar0904/aios"\n'
            "  }\n"
            "]\n"
        )

        steps = []
        try:
            model_name = getattr(self.model_service, "_default_model", None) or "claude-3-5-sonnet"
            res = self.model_service.execute_request(
                LLMRequest(
                    prompt=prompt,
                    system_instruction="You are a strict orchestration planner. Return JSON lists only.",
                    model_name=model_name
                )
            )
            text = res.content.strip()
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()

            raw_steps = json.loads(text)
            for i, rs in enumerate(raw_steps):
                steps.append(
                    WorkflowStep(
                        step_id=f"step_{i}_{uuid.uuid4().hex[:4]}",
                        description=rs.get("description", f"Step {i}"),
                        skill_id=rs.get("skill_id"),
                        command=rs.get("command"),
                        args=rs.get("args", ""),
                        status="pending"
                    )
                )
        except Exception:
            pass

        # 3. Heuristic / Single-step Fallback
        if not steps:
            if selections:
                sel = selections[0]
                cmd = sel.matched_commands[0] if sel.matched_commands else ""
                args = objective_clean
                if cmd and objective_clean.lower().startswith(cmd.lower()):
                    args = objective_clean[len(cmd):].strip()
                steps.append(
                    WorkflowStep(
                        step_id=f"step_fallback_{uuid.uuid4().hex[:4]}",
                        description=f"Fallback execution of {sel.skill_id} skill",
                        skill_id=sel.skill_id,
                        command=cmd,
                        args=args,
                        status="pending"
                    )
                )
            else:
                steps.append(
                    WorkflowStep(
                        step_id=f"step_system_fallback_{uuid.uuid4().hex[:4]}",
                        description="Fallback system execution",
                        skill_id="system",
                        command="help",
                        args=objective_clean,
                        status="pending"
                    )
                )

        return Workflow(
            workflow_id=f"wf_{uuid.uuid4().hex[:6]}",
            objective=objective_clean,
            steps=steps,
            status="pending",
            created_at=time.time()
        )
