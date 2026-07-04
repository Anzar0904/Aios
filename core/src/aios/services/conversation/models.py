import time
import uuid
from typing import Any, Dict, List, Optional


class ConversationMessage:
    def __init__(self, role: str, content: str, timestamp: Optional[float] = None) -> None:
        self.role = role
        self.content = content
        self.timestamp = timestamp if timestamp is not None else time.time()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConversationMessage":
        return cls(
            role=data["role"],
            content=data["content"],
            timestamp=data.get("timestamp")
        )

class ConversationSummary:
    def __init__(
        self,
        summary: str,
        decisions: List[str],
        action_items: List[str],
        unresolved_questions: List[str],
        timestamp: Optional[float] = None
    ) -> None:
        self.summary = summary
        self.decisions = decisions
        self.action_items = action_items
        self.unresolved_questions = unresolved_questions
        self.timestamp = timestamp if timestamp is not None else time.time()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "summary": self.summary,
            "decisions": self.decisions,
            "action_items": self.action_items,
            "unresolved_questions": self.unresolved_questions,
            "timestamp": self.timestamp
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConversationSummary":
        return cls(
            summary=data["summary"],
            decisions=data.get("decisions", []),
            action_items=data.get("action_items", []),
            unresolved_questions=data.get("unresolved_questions", []),
            timestamp=data.get("timestamp")
        )

class Conversation:
    def __init__(
        self,
        id: Optional[str] = None,
        title: Optional[str] = None,
        created_time: Optional[float] = None,
        updated_time: Optional[float] = None,
        active_agent: Optional[str] = None,
        messages: Optional[List[ConversationMessage]] = None,
        summary: Optional[ConversationSummary] = None,
        archived: bool = False
    ) -> None:
        self.id = id if id is not None else str(uuid.uuid4())
        self.title = title if title is not None else f"Conversation {self.id[:8]}"
        self.created_time = created_time if created_time is not None else time.time()
        self.updated_time = updated_time if updated_time is not None else self.created_time
        self.active_agent = active_agent
        self.messages = messages if messages is not None else []
        self.summary = summary
        self.archived = archived

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "created_time": self.created_time,
            "updated_time": self.updated_time,
            "active_agent": self.active_agent,
            "messages": [m.to_dict() for m in self.messages],
            "summary": self.summary.to_dict() if self.summary else None,
            "archived": self.archived
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Conversation":
        summary_data = data.get("summary")
        summary = ConversationSummary.from_dict(summary_data) if summary_data else None
        messages = [ConversationMessage.from_dict(m) for m in data.get("messages", [])]
        return cls(
            id=data["id"],
            title=data.get("title"),
            created_time=data.get("created_time"),
            updated_time=data.get("updated_time"),
            active_agent=data.get("active_agent"),
            messages=messages,
            summary=summary,
            archived=data.get("archived", False)
        )

class ConversationContext:
    def __init__(self, conversation: Conversation, workspace_root: str) -> None:
        self.conversation = conversation
        self.workspace_root = workspace_root
