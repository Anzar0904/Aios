import time
import uuid
from typing import Any, Dict, List, Optional


class TaskStep:
    def __init__(self, command: str, optional: bool = False) -> None:
        self.command = command
        self.optional = optional
        self.status = "pending"  # pending, running, completed, failed
        self.output = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "command": self.command,
            "optional": self.optional,
            "status": self.status,
            "output": self.output
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskStep":
        step = cls(data["command"], data.get("optional", False))
        step.status = data.get("status", "pending")
        step.output = data.get("output", "")
        return step

class Task:
    def __init__(
        self,
        objective: str,
        title: Optional[str] = None,
        id: Optional[str] = None,
        status: str = "pending",
        created_at: Optional[float] = None,
        updated_at: Optional[float] = None,
        steps: Optional[List[TaskStep]] = None,
        execution_log: Optional[List[str]] = None
    ) -> None:
        self.id = id if id is not None else str(uuid.uuid4())
        self.objective = objective
        self.title = title if title is not None else f"Task: {objective[:30]}"
        self.status = status
        self.created_at = created_at if created_at is not None else time.time()
        self.updated_at = updated_at if updated_at is not None else self.created_at
        self.steps = steps if steps is not None else []
        self.execution_log = execution_log if execution_log is not None else []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "objective": self.objective,
            "title": self.title,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "steps": [s.to_dict() for s in self.steps],
            "execution_log": self.execution_log
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        steps = [TaskStep.from_dict(s) for s in data.get("steps", [])]
        return cls(
            objective=data["objective"],
            title=data.get("title"),
            id=data["id"],
            status=data.get("status", "pending"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            steps=steps,
            execution_log=data.get("execution_log", [])
        )
