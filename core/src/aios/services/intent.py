import abc
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Dict, Optional

from aios.services.base import ServiceLifecycle


class IntentType(Enum):
    MEMORY = auto()
    CONTEXT = auto()
    SESSION = auto()
    SYSTEM = auto()
    DEVELOPER = auto()
    UNKNOWN = auto()


@dataclass
class Intent:
    """Strongly typed model representing resolved user intent."""

    intent_type: IntentType
    target_service: str
    action: str
    parameters: Dict[str, Any]
    confidence: float


@dataclass
class IntentResult:
    """Strongly typed model representing the outcome of executing an intent."""

    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


class IntentResolverService(ServiceLifecycle, abc.ABC):
    """Interface for translating natural language into structured executing intents."""

    @abc.abstractmethod
    def resolve(self, text: str) -> Intent:
        """Translates natural language text into a structured Intent."""
        pass

    @abc.abstractmethod
    def validate(self, intent: Intent) -> bool:
        """Validates that a resolved Intent is well-formed and executable."""
        pass

    @abc.abstractmethod
    def classify(self, text: str) -> IntentType:
        """Classifies natural language text into an IntentType."""
        pass
