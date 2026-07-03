import abc

from aios.services.base import ServiceLifecycle


class ToolService(ServiceLifecycle, abc.ABC):
    """Interface for registering and executing safe command-line or API capabilities."""

    @abc.abstractmethod
    def register_tool(self, name: str, contract: dict) -> None:
        """Registers a tool with the engine, specifying its execution contract."""
        pass

    @abc.abstractmethod
    def invoke_tool(self, name: str, arguments: dict) -> dict:
        """Invokes a registered tool by name with the given arguments."""
        pass
