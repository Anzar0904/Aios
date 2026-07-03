from unittest.mock import MagicMock, patch

from aios.services.event_bus_impl import LocalEventBus
from aios.services.tool import (
    ToolCompletedEvent,
    ToolFailedEvent,
    ToolResult,
    ToolStartedEvent,
)
from aios.services.tool_impl import (
    FilesystemTool,
    GitTool,
    LocalToolManager,
    TerminalTool,
)


def test_filesystem_tool(tmp_path):
    tool = FilesystemTool()

    # Write
    file_path = tmp_path / "test.txt"
    res_write = tool.execute(
        {"action": "write", "path": str(file_path), "content": "Hello Filesystem"}
    )
    assert res_write.success is True
    assert file_path.read_text() == "Hello Filesystem"

    # Read
    res_read = tool.execute({"action": "read", "path": str(file_path)})
    assert res_read.success is True
    assert res_read.output == "Hello Filesystem"

    # List
    res_list = tool.execute({"action": "list", "path": str(tmp_path)})
    assert res_list.success is True
    assert "test.txt" in res_list.output


def test_git_tool():
    tool = GitTool()

    # Mock git subprocess run
    mock_run = MagicMock()
    mock_run.returncode = 0
    mock_run.stdout = "On branch main\nYour branch is up to date"

    with patch("subprocess.run", return_value=mock_run) as patched_run:
        res = tool.execute({"action": "status"})
        patched_run.assert_called_with(
            ["git", "status"], capture_output=True, text=True, check=False, timeout=10
        )
        assert res.success is True
        assert "On branch main" in res.output


def test_terminal_tool():
    tool = TerminalTool()

    # Safe execution
    mock_run = MagicMock()
    mock_run.returncode = 0
    mock_run.stdout = "hello test"

    with patch("subprocess.run", return_value=mock_run) as patched_run:
        res = tool.execute({"command": "echo hello test"})
        patched_run.assert_called_with(
            "echo hello test",
            shell=True,
            capture_output=True,
            text=True,
            check=False,
            timeout=15,
        )
        assert res.success is True
        assert res.output == "hello test"

    # Dangerous command rejection
    res_dangerous = tool.execute({"command": "sudo rm -rf /"})
    assert res_dangerous.success is False
    assert "rejected" in res_dangerous.error


def test_tool_manager_and_events():
    event_bus = LocalEventBus()
    manager = LocalToolManager(event_bus)
    manager.initialize()

    # List tools
    tools = manager.list_tools()
    names = [t.name for t in tools]
    assert "filesystem" in names
    assert "git" in names
    assert "terminal" in names

    # Subscribe to events
    started = []
    completed = []
    failed = []

    event_bus.subscribe(ToolStartedEvent, lambda e: started.append(e))
    event_bus.subscribe(ToolCompletedEvent, lambda e: completed.append(e))
    event_bus.subscribe(ToolFailedEvent, lambda e: failed.append(e))

    # Successful invocation
    mock_tool = MagicMock()
    mock_tool.metadata.name = "mock_tool"
    mock_tool.metadata.input_schema = {
        "type": "object",
        "properties": {"arg1": {"type": "string"}},
        "required": ["arg1"],
    }
    mock_tool.execute.return_value = ToolResult(success=True, output="mock-ok")

    manager.register_tool(mock_tool)

    res = manager.execute_tool("mock_tool", {"arg1": "value1"})
    assert res.success is True
    assert len(started) == 1
    assert started[0].tool_name == "mock_tool"
    assert len(completed) == 1
    assert completed[0].tool_name == "mock_tool"
    assert len(failed) == 0

    # Failed validation invocation
    res_invalid = manager.execute_tool("mock_tool", {})
    assert res_invalid.success is False
    assert len(failed) == 1
    assert failed[0].tool_name == "mock_tool"
    assert "Validation failed" in failed[0].error
