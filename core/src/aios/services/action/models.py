import time
import uuid
from enum import Enum
from typing import Any, Dict, List, Optional


class ActionType(Enum):
    READ = "READ"
    WRITE = "WRITE"
    MODIFY = "MODIFY"
    DELETE = "DELETE"
    NETWORK = "NETWORK"

class RiskLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class ActionStep:
    def __init__(
        self,
        description: str,
        action_type: ActionType,
        risk_level: RiskLevel,
        tool_name: str,
        tool_args: Dict[str, Any],
        is_reversible: bool = True,
        undo_args: Optional[Dict[str, Any]] = None
    ) -> None:
        self.id = str(uuid.uuid4())
        self.description = description
        self.action_type = action_type
        self.risk_level = risk_level
        self.tool_name = tool_name
        self.tool_args = tool_args
        self.is_reversible = is_reversible
        self.undo_args = undo_args
        # pending, approved, rejected, running, completed, failed, rolled_back
        self.status = "pending"
        self.output = ""
        self.error = ""
        self.backup_content = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "description": self.description,
            "action_type": self.action_type.value,
            "risk_level": self.risk_level.value,
            "tool_name": self.tool_name,
            "tool_args": self.tool_args,
            "is_reversible": self.is_reversible,
            "undo_args": self.undo_args,
            "status": self.status,
            "output": self.output,
            "error": self.error,
            "backup_content": self.backup_content
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ActionStep":
        step = cls(
            description=data["description"],
            action_type=ActionType(data["action_type"]),
            risk_level=RiskLevel(data["risk_level"]),
            tool_name=data["tool_name"],
            tool_args=data["tool_args"],
            is_reversible=data.get("is_reversible", True),
            undo_args=data.get("undo_args")
        )
        step.id = data["id"]
        step.status = data.get("status", "pending")
        step.output = data.get("output", "")
        step.error = data.get("error", "")
        step.backup_content = data.get("backup_content", "")
        return step

class ActionPlan:
    def __init__(
        self,
        objective: str,
        steps: Optional[List[ActionStep]] = None,
        id: Optional[str] = None,
        status: str = "pending",
        created_at: Optional[float] = None,
        updated_at: Optional[float] = None
    ) -> None:
        self.id = id if id is not None else str(uuid.uuid4())
        self.objective = objective
        self.steps = steps if steps is not None else []
        self.status = status
        self.created_at = created_at if created_at is not None else time.time()
        self.updated_at = updated_at if updated_at is not None else self.created_at

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "objective": self.objective,
            "steps": [s.to_dict() for s in self.steps],
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ActionPlan":
        steps = [ActionStep.from_dict(s) for s in data.get("steps", [])]
        return cls(
            objective=data["objective"],
            steps=steps,
            id=data["id"],
            status=data.get("status", "pending"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )
