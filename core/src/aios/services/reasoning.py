import abc
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Any, Optional

from aios.services.base import ServiceLifecycle


class ReasoningStrategy(Enum):
    ANALYTICAL = auto()
    CREATIVE = auto()
    ENGINEERING = auto()
    RESEARCH = auto()
    CAREER = auto()
    AUTOMATION = auto()
    LEARNING = auto()
    HYBRID = auto()


@dataclass
class ReasoningStep:
    step_id: str
    thought: str
    action: Optional[str] = None
    critique: Optional[str] = None


@dataclass
class ReasoningChain:
    chain_id: str
    steps: List[ReasoningStep] = field(default_factory=list)


@dataclass
class ReasoningContext:
    variables: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ReasoningMemory:
    insights: List[str] = field(default_factory=list)


@dataclass
class ReasoningResult:
    success: bool
    plan: Dict[str, Any] = field(default_factory=dict)
    strategy: ReasoningStrategy = ReasoningStrategy.HYBRID
    self_critique: Dict[str, Any] = field(default_factory=dict)
    chain: Optional[ReasoningChain] = None


@dataclass
class ReasoningSession:
    session_id: str
    objective: str
    created_at: float


class ReasoningEvaluator(abc.ABC):
    @abc.abstractmethod
    def evaluate(self, plan: Dict[str, Any], strategy: ReasoningStrategy) -> Dict[str, Any]:
        """Evaluates completeness, safety, complexity, and maintainability of the plan."""
        pass


class ReasoningCritic(abc.ABC):
    @abc.abstractmethod
    def critique(self, step: ReasoningStep, context: ReasoningContext) -> str:
        """Evaluates a single reasoning step thought and suggests criticisms or flags risks."""
        pass


class ReasoningService(ServiceLifecycle, abc.ABC):
    @abc.abstractmethod
    def reason(self, objective: str, context: ReasoningContext) -> ReasoningResult:
        """Processes the objective through the goal analysis, strategy matching, and self critique loop."""
        pass

    @abc.abstractmethod
    def create_session(self, objective: str) -> ReasoningSession:
        """Initializes a reasoning session."""
        pass
