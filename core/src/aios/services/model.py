import abc

from aios.services.base import ServiceLifecycle


class ModelService(ServiceLifecycle, abc.ABC):
    """Interface for executing prompts against LLM providers via adapters."""

    @abc.abstractmethod
    def execute_prompt(self, prompt: str, system_instruction: str | None = None) -> str:
        """Executes a text prompt and returns the generated content."""
        pass
