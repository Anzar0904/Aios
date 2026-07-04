import time
from typing import Any

from aios.services.action.models import ActionPlan, ActionStep, RiskLevel
from aios.services.action.report import ActionReportGenerator
from aios.services.action.rollback import RollbackCoordinator


class ActionExecutor:
    def __init__(self, tool_service: Any) -> None:
        self.tool_service = tool_service
        self.rollback_coordinator = RollbackCoordinator(tool_service)
        self.report_generator = ActionReportGenerator()

    def execute_step(self, step: ActionStep) -> bool:
        if step.status != "approved":
            step.status = "failed"
            step.error = f"Step was not approved (status: {step.status})"
            return False

        is_fs = step.tool_name == "filesystem"
        is_write_op = step.tool_args.get("action") in ("write", "delete", "modify")
        if is_fs and is_write_op:
            path = step.tool_args.get("path")
            if path:
                read_res = self.tool_service.execute_tool(
                    "filesystem", {"action": "read", "path": path}
                )
                if read_res.success:
                    step.backup_content = read_res.output
                else:
                    step.backup_content = ""

        step.status = "running"
        try:
            res = self.tool_service.execute_tool(step.tool_name, step.tool_args)
            if res.success:
                step.status = "completed"
                step.output = str(res.output) if hasattr(res, "output") else ""
                return True
            else:
                step.status = "failed"
                step.error = res.error if hasattr(res, "error") else "Tool execution failed."
                return False
        except Exception as e:
            step.status = "failed"
            step.error = str(e)
            return False

    def execute_plan(self, plan: ActionPlan) -> str:
        if plan.status != "approved":
            return f"Plan cannot be executed. Status is {plan.status}."

        plan.status = "running"
        start_time = time.time()
        
        for step in plan.steps:
            if step.risk_level == RiskLevel.HIGH and step.status != "approved":
                step.status = "failed"
                step.error = "Explicit approval required for high-risk actions."
                plan.status = "failed"
                break
                
            success = self.execute_step(step)
            if not success:
                plan.status = "failed"
                self.rollback_coordinator.rollback_step(step)
                break
        else:
            plan.status = "completed"
            
        return self.report_generator.generate(plan, start_time)
