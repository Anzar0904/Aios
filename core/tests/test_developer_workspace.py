import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from aios.brain.context_manager import ContextManager
from aios.services.context import WorkspaceContext
from aios.services.developer_workspace import DeveloperWorkspaceInfo
from aios.services.developer_workspace_impl import LocalDeveloperWorkspace


def test_git_status_parsing():
    service = LocalDeveloperWorkspace()
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace_root = Path(tmpdir)

        # Mock subprocess run to simulate git status --porcelain
        mock_stdout = "M  core/src/aios/cli.py\n M core/tests/test_cli.py\n?? untracked.txt\n"

        def mock_run(cmd, **kwargs):
            mock_res = MagicMock()
            if "status" in cmd:
                mock_res.returncode = 0
                mock_res.stdout = mock_stdout
            elif "diff" in cmd:
                mock_res.returncode = 0
                mock_res.stdout = " 2 files changed, 10 insertions(+)"
            elif "rev-parse" in cmd:
                mock_res.returncode = 0
                mock_res.stdout = "main\n"
            else:
                mock_res.returncode = 1
                mock_res.stdout = ""
            return mock_res

        with patch("subprocess.run", side_effect=mock_run):
            info = service.get_workspace_info(str(workspace_root))

            assert info.git_status == mock_stdout.strip()
            assert info.git_diff_summary == "2 files changed, 10 insertions(+)"
            assert info.staged_files == ["core/src/aios/cli.py"]
            assert info.unstaged_files == ["core/tests/test_cli.py"]
            assert info.untracked_files == ["untracked.txt"]
            assert info.extra.get("git_branch") == "main"


def test_test_discovery_and_build_detection():
    service = LocalDeveloperWorkspace()
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace_root = Path(tmpdir)

        # Create tests
        (workspace_root / "tests").mkdir()
        (workspace_root / "tests" / "test_dummy.py").write_text(
            "def test(): pass", encoding="utf-8"
        )
        (workspace_root / "tests" / "dummy_test.py").write_text(
            "def test(): pass", encoding="utf-8"
        )

        # Create pyproject.toml with ruff configuration
        pyproject = workspace_root / "pyproject.toml"
        pyproject.write_text("[tool.poetry]\n[tool.ruff]\n", encoding="utf-8")

        info = service.get_workspace_info(str(workspace_root))

        assert "poetry" in info.build_systems
        assert "ruff" in info.linters
        assert len(info.detected_tests) == 2
        assert "tests/test_dummy.py" in info.detected_tests
        assert "tests/dummy_test.py" in info.detected_tests


def test_safe_command_execution():
    service = LocalDeveloperWorkspace()
    with tempfile.TemporaryDirectory() as tmpdir:
        # Whitelisted commands should pass safety check (will run and mock stdout)
        with patch("subprocess.run") as mock_run:
            mock_res = MagicMock()
            mock_res.returncode = 0
            mock_res.stdout = "All clear"
            mock_res.stderr = ""
            mock_run.return_value = mock_res

            res = service.execute_safe_command("pytest", ["-v", "tests/"], tmpdir)
            assert res["success"] is True
            assert res["stdout"] == "All clear"

        # Non-whitelisted command should be blocked
        res_blocked = service.execute_safe_command("rm", ["-rf", "/"], tmpdir)
        assert res_blocked["success"] is False
        assert "not whitelisted" in res_blocked["error"]

        # Command injection attempt (metacharacters) should be blocked
        res_inject = service.execute_safe_command("pytest", ["tests/; rm -rf /"], tmpdir)
        assert res_inject["success"] is False
        assert "Safety check failed" in res_inject["error"]


def test_context_manager_developer_workspace_integration():
    context_service = MagicMock()
    memory_service = MagicMock()
    project_intel = MagicMock()
    dev_workspace = MagicMock()

    workspace_ctx = WorkspaceContext(
        working_directory="/tmp/test_workspace",
        git_repo_path="/tmp/test_workspace/.git",
        git_branch="main",
        project_root="/tmp/test_workspace",
        project_name="test_proj",
    )
    context_service.get_current_context.return_value = workspace_ctx
    memory_service.search_memory.return_value = []
    project_intel.analyze_workspace.return_value = None

    mock_workspace_info = DeveloperWorkspaceInfo(
        git_status="M file.py",
        git_diff_summary="1 file changed",
        staged_files=[],
        unstaged_files=["file.py"],
    )
    dev_workspace.get_workspace_info.return_value = mock_workspace_info

    manager = ContextManager(context_service, memory_service, project_intel, dev_workspace)
    assembled = manager.assemble_context("explain changes")

    assert assembled.extra.get("developer_workspace") == mock_workspace_info
    dev_workspace.get_workspace_info.assert_called_once_with("/tmp/test_workspace")
