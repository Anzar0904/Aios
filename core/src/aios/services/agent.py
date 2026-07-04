import abc
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional

from aios.services.base import ServiceLifecycle
from aios.services.context import WorkspaceContext
from aios.services.event_bus import Event
from aios.services.intent import Intent
from aios.services.memory import Memory
from aios.services.tool import ToolMetadata


class AgentLifecycle(Enum):
    INITIALIZING = auto()
    EXECUTING = auto()
    COMPLETED = auto()
    FAILED = auto()


@dataclass
class AgentCapability:
    name: str
    description: str


@dataclass
class AgentTask:
    task_id: str
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentExecutionPlan:
    plan_id: str
    steps: List[str] = field(default_factory=list)


@dataclass
class AgentContext:
    """The execution context provided to an Agent during invocation."""

    intent: Intent
    context: Optional[WorkspaceContext]
    memories: List[Memory]
    tools: List[ToolMetadata]
    extra: Dict[str, Any] = field(default_factory=dict)


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


class AgentRegistry(ServiceLifecycle):
    def __init__(self) -> None:
        self._agents: Dict[str, Agent] = {}

    def initialize(self) -> None:
        pass

    def register(self, agent: Agent) -> None:
        self._agents[agent.name.lower()] = agent

    def unregister(self, name: str) -> None:
        name_lower = name.lower()
        if name_lower in self._agents:
            del self._agents[name_lower]

    def get_agent(self, name: str) -> Optional[Agent]:
        return self._agents.get(name.lower())

    def list_agents(self) -> List[Agent]:
        return list(self._agents.values())


class AgentFactory:
    """Factory to instantiate core agents."""

    @staticmethod
    def create_agent(agent_type: str, *args, **kwargs) -> Agent:
        from aios.services.agent_impl import CareerAgent, DeveloperAgent, MockAgent
        if agent_type == "career":
            return CareerAgent(*args, **kwargs)
        elif agent_type == "developer":
            return DeveloperAgent(*args, **kwargs)
        else:
            return MockAgent(*args, **kwargs)


class LocalAgentManager(ServiceLifecycle):
    """Coordinates agents, workflows, and multi-skill orchestrator plans."""

    def __init__(self, registry: AgentRegistry, orchestrator: Any) -> None:
        self.registry = registry
        self.orchestrator = orchestrator

    def initialize(self) -> None:
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


