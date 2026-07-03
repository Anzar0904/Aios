import abc
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from aios.services.base import ServiceLifecycle
from aios.services.context import WorkspaceContext
from aios.services.event_bus import Event
from aios.services.intent import Intent
from aios.services.memory import Memory
from aios.services.tool import ToolMetadata


@dataclass
class AgentContext:
    """The execution context provided to an Agent during invocation."""

    intent: Intent
    context: Optional[WorkspaceContext]
    memories: List[Memory]
    tools: List[ToolMetadata]


@dataclass
class AgentResult:
    """The structured result returned from an Agent execution."""

    success: bool
    response: str
    data: Dict[str, Any] = field(default_factory=dict)


class Agent(abc.ABC):
    """Base class for all Agents in the system."""

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Returns the name of the agent."""
        pass

    @property
    @abc.abstractmethod
    def description(self) -> str:
        """Returns the description of the agent."""
        pass

    @abc.abstractmethod
    def execute(self, agent_context: AgentContext) -> AgentResult:
        """Executes the agent logic with the provided context."""
        pass


@dataclass(frozen=True, kw_only=True)
class AgentStartedEvent(Event):
    """Published when an agent runtime execution starts."""

    intent: Intent


@dataclass(frozen=True, kw_only=True)
class AgentCompletedEvent(Event):
    """Published when an agent execution completes successfully."""

    result: AgentResult


@dataclass(frozen=True, kw_only=True)
class AgentFailedEvent(Event):
    """Published when an agent execution fails."""

    error: str


class AgentRuntimeService(ServiceLifecycle, abc.ABC):
    """Interface for managing agents and dispatching intent executions."""

    @abc.abstractmethod
    def register_agent(self, agent: Agent) -> None:
        """Registers an agent with the runtime registry."""
        pass

    @abc.abstractmethod
    def unregister_agent(self, name: str) -> None:
        """Unregisters an agent by name."""
        pass

    @abc.abstractmethod
    def execute(self, intent: Intent) -> AgentResult:
        """Runs the active agent against the given Intent, resolving dependencies."""
        pass

    @abc.abstractmethod
    def interrupt(self) -> None:
        """Interrupts the active agent execution."""
        pass

    @abc.abstractmethod
    def cancel(self) -> None:
        """Cancels the active agent execution."""
        pass
