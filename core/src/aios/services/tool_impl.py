import logging
import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List

from aios.services.event_bus import EventBusService
from aios.services.tool import (
    Tool,
    ToolCompletedEvent,
    ToolFailedEvent,
    ToolMetadata,
    ToolResult,
    ToolService,
    ToolStartedEvent,
)

logger = logging.getLogger(__name__)


class FilesystemTool(Tool):
    """Tool for safe local filesystem operations."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="filesystem",
            description="Perform read, write, or list operations on the filesystem.",
            input_schema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["read", "write", "list"],
                        "description": "The filesystem action to perform.",
                    },
                    "path": {
                        "type": "string",
                        "description": "The target path of the file or directory.",
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write (required for action='write').",
                    },
                },
                "required": ["action", "path"],
            },
            output_schema={
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "output": {"type": "string"},
                    "error": {"type": "string", "nullable": True},
                },
            },
        )

    def __init__(self, workspace_root_provider=None) -> None:
        self._workspace_root_provider = workspace_root_provider

    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        from aios.services.security import validate_workspace_path

        action = arguments.get("action")
        path_str = arguments.get("path", ".")

        if self._workspace_root_provider:
            workspace_root = self._workspace_root_provider()
        else:
            workspace_root = str(Path.cwd().resolve())

        try:
            path = validate_workspace_path(path_str, workspace_root)
        except PermissionError:
            return ToolResult(
                success=False,
                output="",
                error="Access denied: path escapes workspace.",
            )
        except Exception:
            return ToolResult(success=False, output="", error="Invalid path format.")

        if action == "read":
            if not path.is_file():
                return ToolResult(success=False, output="", error="Path is not a file.")
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                return ToolResult(success=True, output=content)
            except Exception:
                return ToolResult(success=False, output="", error="Failed to read file.")

        elif action == "write":
            content = arguments.get("content")
            if content is None:
                return ToolResult(
                    success=False,
                    output="",
                    error="Argument 'content' is required for write action.",
                )
            try:
                path.parent.mkdir(parents=True, exist_ok=True)
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
                return ToolResult(success=True, output="Successfully wrote to file.")
            except Exception:
                return ToolResult(success=False, output="", error="Failed to write file.")

        elif action == "list":
            if not path.exists():
                return ToolResult(success=False, output="", error="Path does not exist.")
            if not path.is_dir():
                return ToolResult(success=False, output="", error="Path is not a directory.")
            try:
                items = sorted(os.listdir(path))
                output = "\n".join(items)
                return ToolResult(success=True, output=output)
            except Exception:
                return ToolResult(success=False, output="", error="Failed to list directory.")
        return ToolResult(success=False, output="", error=f"Unknown filesystem action: {action}")


class GitTool(Tool):
    """Tool for running local git commands safely."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="git",
            description="Run git status, branch, or log.",
            input_schema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["status", "branch", "log"],
                        "description": "The git subcommand to execute.",
                    }
                },
                "required": ["action"],
            },
            output_schema={
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "output": {"type": "string"},
                    "error": {"type": "string", "nullable": True},
                },
            },
        )

    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        action = arguments.get("action")
        if action == "status":
            cmd = ["git", "status"]
        elif action == "branch":
            cmd = ["git", "branch"]
        elif action == "log":
            cmd = ["git", "log", "-n", "5"]
        else:
            return ToolResult(success=False, output="", error=f"Unsupported git action: {action}")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=10)
            if result.returncode == 0:
                return ToolResult(success=True, output=result.stdout)
            else:
                return ToolResult(success=False, output=result.stdout, error=result.stderr)
        except Exception as e:
            return ToolResult(success=False, output="", error=f"Failed to run git command: {e}")


class TerminalTool(Tool):
    """Tool for safe local command execution in the shell."""

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="terminal",
            description="Execute safe shell commands.",
            input_schema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The shell command string to execute.",
                    }
                },
                "required": ["command"],
            },
            output_schema={
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "output": {"type": "string"},
                    "error": {"type": "string", "nullable": True},
                },
            },
        )

    def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        import shlex

        command = arguments.get("command", "").strip()
        if not command:
            return ToolResult(success=False, output="", error="Empty command.")

        # Reject chained commands, pipes, redirects, command substitution, and shell metacharacters.
        forbidden_metachars = [
            ";",
            "&",
            "|",
            "<",
            ">",
            "$",
            "(",
            ")",
            "`",
            "\\",
            "*",
            "?",
            "[",
            "]",
            "!",
            "{",
            "}",
            "\n",
            "\r",
        ]
        for char in forbidden_metachars:
            if char in command:
                return ToolResult(
                    success=False,
                    output="",
                    error=f"Command execution rejected: command contains forbidden shell metacharacter '{char}'.",
                )

        dangerous = ["sudo", "rm -rf", "chmod", "chown", "dd", "mkfs", "shred"]
        for keyword in dangerous:
            if keyword in command:
                return ToolResult(
                    success=False,
                    output="",
                    error=f"Command execution rejected: contains forbidden keyword '{keyword}'.",
                )

        try:
            cmd_parts = shlex.split(command)
        except Exception as e:
            return ToolResult(success=False, output="", error=f"Command parsing failed: {e}")

        if not cmd_parts:
            return ToolResult(success=False, output="", error="Empty command.")

        whitelist = {"echo", "pwd", "whoami", "git"}
        executable = cmd_parts[0]
        if executable not in whitelist:
            return ToolResult(
                success=False,
                output="",
                error=f"Command execution rejected: executable '{executable}' is not in the whitelist.",
            )

        if executable == "pwd":
            if len(cmd_parts) > 1:
                return ToolResult(
                    success=False, output="", error="pwd command does not accept arguments."
                )
        elif executable == "whoami":
            if len(cmd_parts) > 1:
                return ToolResult(
                    success=False, output="", error="whoami command does not accept arguments."
                )
        elif executable == "git":
            if len(cmd_parts) > 1:
                subcommand = cmd_parts[1]
                allowed_git_subcommands = {
                    "status",
                    "branch",
                    "log",
                    "diff",
                    "show",
                    "rev-parse",
                    "version",
                    "help",
                }
                if subcommand not in allowed_git_subcommands:
                    return ToolResult(
                        success=False,
                        output="",
                        error=f"Command execution rejected: git subcommand '{subcommand}' is not allowed.",
                    )

        try:
            result = subprocess.run(
                cmd_parts,
                shell=False,
                capture_output=True,
                text=True,
                check=False,
                timeout=15,
            )
            if result.returncode == 0:
                return ToolResult(success=True, output=result.stdout)
            else:
                return ToolResult(
                    success=False,
                    output=result.stdout,
                    error=result.stderr or f"Exit code {result.returncode}",
                )
        except subprocess.TimeoutExpired:
            return ToolResult(success=False, output="", error="Command execution timed out.")
        except Exception as e:
            return ToolResult(success=False, output="", error=f"Failed to run command: {e}")


class LocalToolManager(ToolService):
    """Concrete implementation of ToolService.

    Manages the tool registry, performs schema validation, executes tools,
    and publishes status events to the event bus.
    """

    def __init__(self, event_bus: EventBusService) -> None:
        self._event_bus = event_bus
        self._tools: Dict[str, Tool] = {}
        self._workspace_root = str(Path.cwd().resolve())

    def initialize(self) -> None:
        logger.info("Initializing LocalToolManager")
        self._event_bus.register_event_type(ToolStartedEvent)
        self._event_bus.register_event_type(ToolCompletedEvent)
        self._event_bus.register_event_type(ToolFailedEvent)

        from aios.services.context import ContextLoadedEvent
        from aios.services.session import SessionStartedEvent

        self._event_bus.register_event_type(ContextLoadedEvent)
        self._event_bus.register_event_type(SessionStartedEvent)
        self._event_bus.subscribe(ContextLoadedEvent, self._on_context_loaded)
        self._event_bus.subscribe(SessionStartedEvent, self._on_session_started)

        self.register_tool(FilesystemTool(workspace_root_provider=lambda: self._workspace_root))
        self.register_tool(GitTool())
        self.register_tool(TerminalTool())

    def _on_context_loaded(self, event) -> None:
        self._workspace_root = event.context.project_root

    def _on_session_started(self, event) -> None:
        self._workspace_root = event.session.workspace_id

    def register_tool(self, tool: Tool) -> None:
        """Registers a tool with the engine."""
        name = tool.metadata.name
        self._tools[name] = tool
        logger.info(f"Registered tool: {name}")

    def unregister_tool(self, name: str) -> None:
        """Unregisters a tool by name."""
        if name in self._tools:
            del self._tools[name]
            logger.info(f"Unregistered tool: {name}")

    def list_tools(self) -> List[ToolMetadata]:
        """Lists metadata of all registered tools."""
        return [tool.metadata for tool in self._tools.values()]

    def validate_tool(self, name: str, arguments: Dict[str, Any]) -> bool:
        """Validates tool arguments against its input schema."""
        tool = self._tools.get(name)
        if not tool:
            return False

        schema = tool.metadata.input_schema
        required = schema.get("required", [])

        for field in required:
            if field not in arguments:
                logger.warning(
                    f"Validation failed: missing required field '{field}' for tool '{name}'"
                )
                return False

        properties = schema.get("properties", {})
        for key, val in arguments.items():
            prop = properties.get(key)
            if not prop:
                continue

            expected_type = prop.get("type")
            if expected_type == "string" and not isinstance(val, str):
                return False
            if expected_type == "integer" and not isinstance(val, int):
                return False
            if expected_type == "boolean" and not isinstance(val, bool):
                return False
            if expected_type == "array" and not isinstance(val, list):
                return False
            if expected_type == "object" and not isinstance(val, dict):
                return False

            enum_vals = prop.get("enum")
            if enum_vals and val not in enum_vals:
                logger.warning(
                    f"Validation failed: value '{val}' not in enum {enum_vals} for key '{key}'"
                )
                return False

        return True

    def execute_tool(self, name: str, arguments: Dict[str, Any]) -> ToolResult:
        """Executes a registered tool by name with the given arguments."""
        tool = self._tools.get(name)
        if not tool:
            err_msg = f"Tool '{name}' is not registered."
            self._event_bus.publish(ToolFailedEvent(tool_name=name, error=err_msg))
            return ToolResult(success=False, output="", error=err_msg)

        if not self.validate_tool(name, arguments):
            err_msg = f"Validation failed for tool '{name}' with arguments {arguments}."
            self._event_bus.publish(ToolFailedEvent(tool_name=name, error=err_msg))
            return ToolResult(success=False, output="", error=err_msg)

        logger.info(f"Executing tool '{name}' with arguments {arguments}")
        self._event_bus.publish(ToolStartedEvent(tool_name=name, arguments=arguments))

        try:
            result = tool.execute(arguments)
            if result.success:
                self._event_bus.publish(ToolCompletedEvent(tool_name=name, result=result))
            else:
                self._event_bus.publish(
                    ToolFailedEvent(tool_name=name, error=result.error or "Unknown failure")
                )
            return result
        except Exception as e:
            err_msg = f"Exception during execution of tool '{name}': {e}"
            logger.error(err_msg, exc_info=True)
            self._event_bus.publish(ToolFailedEvent(tool_name=name, error=err_msg))
            return ToolResult(success=False, output="", error=err_msg)

    def invoke_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Invokes a registered tool by name and returns output dict (backward compatibility)."""
        res = self.execute_tool(name, arguments)
        return {
            "success": res.success,
            "output": res.output,
            "error": res.error,
        }
