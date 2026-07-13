import contextlib
import io
from typing import Any, Dict, List

from aios.brain.models import Workflow, WorkflowStep
from aios.services.action.approval import ApprovalManager
from aios.services.action.executor import ActionExecutor
from aios.services.action.models import ActionPlan, ActionStep, ActionType, RiskLevel
from aios.services.command import CommandRegistry
from aios.services.tool import ToolService


def group_steps_into_levels(steps: List[WorkflowStep]) -> List[List[WorkflowStep]]:
    """
    Validates dependencies, checks for circular paths, and groups steps
    into execution levels based on their dependency graphs.
    """
    if not steps:
        return []

    step_map = {step.step_id: step for step in steps}

    # 1. Validate dependencies exist
    for step in steps:
        for dep_id in step.depends_on:
            if dep_id not in step_map:
                raise ValueError(f"Step '{step.step_id}' depends on non-existent step '{dep_id}'")

    # 2. Cycle detection via DFS
    visited: Dict[str, int] = {step.step_id: 0 for step in steps}  # 0: unvisited, 1: visiting, 2: visited

    def has_cycle(sid: str) -> bool:
        visited[sid] = 1
        for dep_id in step_map[sid].depends_on:
            if visited[dep_id] == 1:
                return True
            if visited[dep_id] == 0:
                if has_cycle(dep_id):
                    return True
        visited[sid] = 2
        return False

    for step in steps:
        if visited[step.step_id] == 0:
            if has_cycle(step.step_id):
                raise ValueError("Circular dependency detected in workflow steps")

    # 3. Calculate levels (max depth of dependencies)
    memo: Dict[str, int] = {}

    def get_level(sid: str) -> int:
        if sid in memo:
            return memo[sid]
        step = step_map[sid]
        if not step.depends_on:
            val = 0
        else:
            val = max(get_level(dep_id) for dep_id in step.depends_on) + 1
        memo[sid] = val
        return val

    for step in steps:
        get_level(step.step_id)

    max_level = max(memo.values()) if memo else 0
    grouped = [[] for _ in range(max_level + 1)]
    for sid, lvl in memo.items():
        grouped[lvl].append(step_map[sid])

    return grouped


def visualize_workflow_graph(steps: List[WorkflowStep]) -> str:
    """Returns an ASCII graph visualization of the workflow graph levels."""
    try:
        grouped = group_steps_into_levels(steps)
    except Exception as e:
        return f"Workflow Graph Invalid: {e}"

    if not grouped:
        return "Empty Workflow Graph"

    lines = ["Workflow Graph Levels:"]
    for idx, lvl in enumerate(grouped):
        step_strs = [f"[{s.step_id} ({s.description[:20]}...)]" for s in lvl]
        lines.append(f"  Level {idx}: " + " | ".join(step_strs))
        if idx < len(grouped) - 1:
            lines.append("           ↓")
    return "\n".join(lines)


class WorkflowExecutor:
    def __init__(self, kernel: Any, command_registry: CommandRegistry) -> None:
        self.kernel = kernel
        self.command_registry = command_registry
        self.tool_service = kernel.registry.get(ToolService)

    def execute(self, workflow: Workflow) -> bool:
        workflow.status = "running"

        try:
            grouped_levels = group_steps_into_levels(workflow.steps)
            print(visualize_workflow_graph(workflow.steps))
        except Exception as e:
            workflow.status = "failed"
            # Set the first step error if exists, or global failure
            if workflow.steps:
                workflow.steps[0].status = "failed"
                workflow.steps[0].error = f"Workflow validation failed: {str(e)}"
            return False

        success = True
        for level in grouped_levels:
            for step in level:
                step.status = "running"
                
                # Determine if we should hand off to Action Engine
                is_action_engine_needed = (
                    step.skill_id == "action"
                    or step.command in ("write file", "delete file", "modify file")
                    or (step.skill_id == "filesystem" and step.command in ("write", "delete", "modify"))
                )

                if is_action_engine_needed:
                    success = self._execute_via_action_engine(step)
                else:
                    success = self._execute_via_command_registry(step)

                if not success:
                    workflow.status = "failed"
                    return False

        workflow.status = "completed"
        return True

    def _execute_via_action_engine(self, step: WorkflowStep) -> bool:
        try:
            action_type = ActionType.READ
            risk_level = RiskLevel.LOW
            tool_args = {}
            undo_args = None
            is_reversible = True

            cmd_lower = step.command.lower()
            if "write" in cmd_lower or "create" in cmd_lower:
                action_type = ActionType.WRITE
                risk_level = RiskLevel.LOW
                parts = step.args.split(maxsplit=1)
                path = parts[0] if parts else "temp.txt"
                content = parts[1] if len(parts) > 1 else ""
                tool_args = {"action": "write", "path": path, "content": content}
                undo_args = {"action": "delete", "path": path}
            elif "delete" in cmd_lower or "remove" in cmd_lower:
                action_type = ActionType.DELETE
                risk_level = RiskLevel.HIGH
                path = step.args.strip()
                tool_args = {"action": "delete", "path": path}
                undo_args = None
            elif "modify" in cmd_lower or "edit" in cmd_lower:
                action_type = ActionType.MODIFY
                risk_level = RiskLevel.MEDIUM
                parts = step.args.split(maxsplit=1)
                path = parts[0] if parts else "temp.txt"
                content = parts[1] if len(parts) > 1 else ""
                tool_args = {"action": "modify", "path": path, "content": content}
                undo_args = {"action": "write", "path": path}
            else:
                tool_args = {"action": "read", "path": step.args.strip()}

            act_step = ActionStep(
                description=step.description,
                action_type=action_type,
                risk_level=risk_level,
                tool_name="filesystem",
                tool_args=tool_args,
                is_reversible=is_reversible,
                undo_args=undo_args
            )
            act_step.status = "approved"

            plan = ActionPlan(objective=step.description, steps=[act_step])
            plan.status = "approved"

            approval_mgr = ApprovalManager()
            approval_mgr.approve_plan(plan)

            executor = ActionExecutor(self.tool_service)
            report = executor.execute_plan(plan)

            if plan.status == "completed":
                step.status = "completed"
                step.output = report
                return True
            else:
                step.status = "failed"
                step.error = report
                return False
        except Exception as e:
            step.status = "failed"
            step.error = f"Action Engine handoff failed: {str(e)}"
            return False

    def _execute_via_command_registry(self, step: WorkflowStep) -> bool:
        handler = self.command_registry.get_handler(step.command)
        if not handler:
            cmd = self.command_registry.get_command(step.command)
            if cmd:
                handler = self.command_registry.get_handler(cmd.name)

        if not handler:
            step.status = "failed"
            step.error = f"Command handler '{step.command}' not found in CommandRegistry."
            return False

        f = io.StringIO()
        try:
            with contextlib.redirect_stdout(f):
                result = handler(step.args)
            
            output = f.getvalue()
            if result is not None:
                output += f"\n{result}"

            step.status = "completed"
            step.output = output.strip()
            return True
        except Exception as e:
            step.status = "failed"
            step.error = f"Command execution failed: {str(e)}\nOutput so far: {f.getvalue().strip()}"
            return False

