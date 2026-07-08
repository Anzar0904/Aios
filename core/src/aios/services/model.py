
import abc
from dataclasses import dataclass, field
from typing import Any, Dict, Iterator, List, Optional

from aios.services.base import ServiceLifecycle


@dataclass
class LLMRequest:
    prompt: str
    system_instruction: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    model_name: Optional[str] = None
    task_category: Optional[str] = None
    preferences: Dict[str, Any] = field(default_factory=dict)

@dataclass
class LLMResponse:
    content: str
    model_name: str
    provider_name: str
    usage: Dict[str, int] = field(default_factory=dict)
    finish_reason: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

class ModelService(ServiceLifecycle, abc.ABC):
    @abc.abstractmethod
    def execute_prompt(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        pass

    @abc.abstractmethod
    def execute_request(self, request: LLMRequest) -> LLMResponse:
        pass

    @abc.abstractmethod
    def execute_stream(self, request: LLMRequest) -> Iterator[LLMResponse]:
        pass
