import json
from typing import Optional

from aios.services.action.models import ActionPlan, ActionStep, ActionType, RiskLevel
from aios.services.model import LLMRequest, ModelService


class ActionPlanner:
    def __init__(self, model_service: Optional[ModelService] = None) -> None:
        self.model_service = model_service

    def plan(self, objective: str) -> ActionPlan:
        obj_lower = objective.lower()
        steps = []
        
        # Rule-based heuristics for testing/simple flows
        if "write file" in obj_lower:
            parts = objective.split("write file ")
            if len(parts) > 1:
                filename = parts[1].split()[0]
                content = parts[1][len(filename):].strip()
                steps.append(ActionStep(
                    description=f"Create file {filename}",
                    action_type=ActionType.WRITE,
                    risk_level=RiskLevel.LOW,
                    tool_name="filesystem",
                    tool_args={"action": "write", "path": filename, "content": content},
                    is_reversible=True,
                    undo_args={"action": "delete", "path": filename}
                ))
        elif "delete file" in obj_lower:
            parts = objective.split("delete file ")
            if len(parts) > 1:
                filename = parts[1].split()[0]
                steps.append(ActionStep(
                    description=f"Delete file {filename}",
                    action_type=ActionType.DELETE,
                    risk_level=RiskLevel.HIGH,
                    tool_name="filesystem",
                    tool_args={"action": "delete", "path": filename},
                    is_reversible=True,  # will attempt backup
                    undo_args=None
                ))
                
        # LLM fallback
        if not steps and self.model_service:
            prompt = (
                "You are the Action Planner for Personal AI OS.\n"
                f'Decompose the objective "{objective}" into action steps.\n\n'
                "For each step, specify:\n"
                "- description\n"
                "- action_type (READ, WRITE, MODIFY, DELETE, NETWORK)\n"
                "- risk_level (LOW, MEDIUM, HIGH)\n"
                "- tool_name (filesystem, git)\n"
                "- tool_args (json)\n"
                "- is_reversible (boolean)\n"
                "- undo_args (json or null)\n\n"
                "Return strictly a JSON list of step definitions. Example:\n"
                "[\n"
                "  {\n"
                '    "description": "Write config file",\n'
                '    "action_type": "WRITE",\n'
                '    "risk_level": "LOW",\n'
                '    "tool_name": "filesystem",\n'
                '    "tool_args": {\n'
                '      "action": "write",\n'
                '      "path": "config.txt",\n'
                '      "content": "setting=true"\n'
                "    },\n"
                '    "is_reversible": true,\n'
                '    "undo_args": {\n'
                '      "action": "delete",\n'
                '      "path": "config.txt"\n'
                "    }\n"
                "  }\n"
                "]\n"
            )
            try:
                res = self.model_service.execute_request(
                    LLMRequest(
                        prompt=prompt,
                        system_instruction=(
                            "You are a strict action planning agent. "
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
                
                raw_steps = json.loads(text)
                for rs in raw_steps:
                    steps.append(ActionStep(
                        description=rs["description"],
                        action_type=ActionType(rs["action_type"]),
                        risk_level=RiskLevel(rs["risk_level"]),
                        tool_name=rs["tool_name"],
                        tool_args=rs["tool_args"],
                        is_reversible=rs.get("is_reversible", True),
                        undo_args=rs.get("undo_args")
                    ))
            except Exception:
                pass
                
        if not steps:
            steps.append(ActionStep(
                description="List files in workspace",
                action_type=ActionType.READ,
                risk_level=RiskLevel.LOW,
                tool_name="filesystem",
                tool_args={"action": "list", "path": "."},
                is_reversible=True,
                undo_args=None
            ))
            
        return ActionPlan(objective=objective, steps=steps)
