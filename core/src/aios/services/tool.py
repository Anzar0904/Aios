import abc
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from aios.services.base import ServiceLifecycle
from aios.services.event_bus import Event


@dataclass
class ToolMetadata:
    """Metadata describing a tool's capability and interface."""

    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]


@dataclass
class ToolResult:
    """The result returned from executing a tool."""

    success: bool
    output: str
    error: Optional[str] = None


class Tool(abc.ABC):
    """Base class for all tools in the system."""

    @property
    @abc.abstractmethod
    def metadata(self) -> ToolMetadata:
        """Returns the metadata of the tool."""
        pass

    @abc.abstractmethod
    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """Executes the tool with the given arguments."""
        pass


@dataclass(frozen=True, kw_only=True)
class ToolStartedEvent(Event):
    """Published when a tool execution is started."""

    tool_name: str
    arguments: Dict[str, Any]


@dataclass(frozen=True, kw_only=True)
class ToolCompletedEvent(Event):
    """Published when a tool execution completes successfully."""

    tool_name: str
    result: ToolResult


@dataclass(frozen=True, kw_only=True)
class ToolFailedEvent(Event):
    """Published when a tool execution fails."""

    tool_name: str
    error: str


class ToolService(ServiceLifecycle, abc.ABC):
    """Interface for managing the registration and execution of safe tools."""

    @abc.abstractmethod
    def register_tool(self, tool: Tool) -> None:
        """Registers a tool with the engine."""
        pass

    @abc.abstractmethod
    def unregister_tool(self, name: str) -> None:
        """Unregisters a tool by name."""
        pass

    @abc.abstractmethod
    def list_tools(self) -> List[ToolMetadata]:
        """Lists metadata of all registered tools."""
        pass

    @abc.abstractmethod
    def execute_tool(self, name: str, arguments: Dict[str, Any]) -> ToolResult:
        """Executes a registered tool by name with the given arguments."""
        pass

    @abc.abstractmethod
    def validate_tool(self, name: str, arguments: Dict[str, Any]) -> bool:
        """Validates tool arguments against its input schema."""
        pass

    # Backward compatibility
    @abc.abstractmethod
    def invoke_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Invokes a registered tool by name and returns output dict."""
        pass
