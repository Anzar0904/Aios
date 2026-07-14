import abc
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from aios.services.base import ServiceLifecycle
from aios.services.intent import Intent


@dataclass
class ActionStep:
    step_id: str
    action_type: str  # "cli_command" | "graph_update" | "doc_update"
    target: str
    description: str
    status: str = "pending"  # "pending", "running", "completed", "failed"
    dependencies: List[str] = field(default_factory=list)


@dataclass
class ActionPlan:
    plan_id: str
    objective: str
    steps: List[ActionStep]
    status: str = "pending"


class NLOSService(ServiceLifecycle, abc.ABC):
    """Core Service coordinating Natural Language OS functions."""

    @abc.abstractmethod
    def route_query(self, query: str) -> Optional[List[str]]:
        """Translates natural language to CLI arguments, resolving context/pronouns."""
        pass

    @abc.abstractmethod
    def extract_entities(self, query: str) -> Dict[str, List[str]]:
        """Extracts Projects, Clients, Repositories, Workflows, etc. from query."""
        pass

    @abc.abstractmethod
    def generate_plan(self, query: str) -> ActionPlan:
        """Generates a step-by-step action plan for a natural language request."""
        pass

    @abc.abstractmethod
    def execute_plan(self, plan: ActionPlan) -> bool:
        """Executes a generated action plan step-by-step."""
        pass

    @abc.abstractmethod
    def get_last_explanation(self) -> Dict[str, Any]:
        """Gets transparency explanation data for 'why' and 'what' questions."""
        pass

    @abc.abstractmethod
    def record_intent_history(self, query: str, intent: Intent, success: bool) -> None:
        """Appends intent to history log."""
        pass

    @abc.abstractmethod
    def get_learning_patterns(self) -> Dict[str, Any]:
        """Gets successful/failed intent patterns and user preferences."""
        pass
