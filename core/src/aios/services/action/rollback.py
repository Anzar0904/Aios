from typing import Any

from aios.services.action.models import ActionStep


class RollbackCoordinator:
    def __init__(self, tool_service: Any) -> None:
        self.tool_service = tool_service

    def rollback_step(self, step: ActionStep) -> bool:
        if not step.is_reversible:
            return False

        if step.action_type.value in ("MODIFY", "DELETE") and step.backup_content:
            path = step.tool_args.get("path")
            if path:
                res = self.tool_service.execute_tool(
                    "filesystem", {"action": "write", "path": path, "content": step.backup_content}
                )
                if res.success:
                    step.status = "rolled_back"
                    return True

        if step.undo_args:
            res = self.tool_service.execute_tool(step.tool_name, step.undo_args)
            if res.success:
                step.status = "rolled_back"
                return True

        return False
