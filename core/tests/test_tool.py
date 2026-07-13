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
    tool = FilesystemTool(workspace_root_provider=lambda: str(tmp_path))

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


def test_filesystem_tool_traversal_attempts(tmp_path):
    tool = FilesystemTool(workspace_root_provider=lambda: str(tmp_path))

    # Nested directory creation (Valid workspace path)
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    nested_file = subdir / "nested.txt"

    # Valid write and read inside nested directory
    res_write = tool.execute(
        {"action": "write", "path": str(nested_file), "content": "nested content"}
    )
    assert res_write.success is True

    res_read = tool.execute({"action": "read", "path": str(nested_file)})
    assert res_read.success is True
    assert res_read.output == "nested content"

    # Attempt relative traversal out of workspace
    escaped_file = tmp_path.parent / "escaped.txt"
    res_esc = tool.execute({"action": "write", "path": str(escaped_file), "content": "malicious"})
    assert res_esc.success is False
    assert "escapes workspace" in res_esc.error

    escaped_relative = tmp_path / "subdir" / ".." / ".." / "escaped.txt"
    res_esc_rel = tool.execute(
        {"action": "write", "path": str(escaped_relative), "content": "malicious"}
    )
    assert res_esc_rel.success is False
    assert "escapes workspace" in res_esc_rel.error

    # Attempt absolute path out of workspace
    res_abs = tool.execute({"action": "read", "path": "/etc/passwd"})
    assert res_abs.success is False
    assert "escapes workspace" in res_abs.error

    # Symlink traversal test
    external_secret = tmp_path.parent / "external_secret.txt"
    external_secret.write_text("top secret")

    link_path = tmp_path / "symlink_test.txt"
    try:
        link_path.symlink_to(external_secret)
        # Attempt to read the symlink
        res_sym = tool.execute({"action": "read", "path": str(link_path)})
        assert res_sym.success is False
        assert "escapes workspace" in res_sym.error
    except OSError:
        pass


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
            ["echo", "hello", "test"],
            shell=False,
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


def test_terminal_tool_security_safeguards():
    tool = TerminalTool()

    # Reject chained commands
    assert tool.execute({"command": "echo hello; rm -rf /"}).success is False
    assert tool.execute({"command": "echo hello && whoami"}).success is False
    assert tool.execute({"command": "echo hello || pwd"}).success is False

    # Reject pipes and redirects
    assert tool.execute({"command": "echo hello | grep h"}).success is False
    assert tool.execute({"command": "echo hello > out.txt"}).success is False
    assert tool.execute({"command": "cat < /etc/passwd"}).success is False

    # Reject command substitution
    assert tool.execute({"command": "echo $(whoami)"}).success is False
    assert tool.execute({"command": "echo `whoami`"}).success is False

    # Reject shell metacharacters
    assert tool.execute({"command": "echo *"}).success is False
    assert tool.execute({"command": "echo ?"}).success is False
    assert tool.execute({"command": "echo \\"}).success is False

    # Reject non-whitelisted commands
    assert tool.execute({"command": "cat /etc/passwd"}).success is False
    assert tool.execute({"command": "ls -la"}).success is False

    # Reject invalid git subcommands
    assert tool.execute({"command": "git clone https://github.com/some/repo"}).success is False
    assert tool.execute({"command": "git push origin main"}).success is False

    # Accept whitelisted git subcommands
    mock_run = MagicMock()
    mock_run.returncode = 0
    mock_run.stdout = "On branch main"
    with patch("subprocess.run", return_value=mock_run):
        assert tool.execute({"command": "git status"}).success is True

    # Reject arguments for pwd / whoami
    assert tool.execute({"command": "pwd extra_arg"}).success is False
    assert tool.execute({"command": "whoami extra_arg"}).success is False


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
