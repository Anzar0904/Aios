"""
core/tests/test_local_workspace_cli.py

Production-quality tests for Phase 2: AI Workspace & Unified CLI.
Tests:
- Session metadata loading/saving
- Diagnostics / Health Checks
- Command handlers (dashboard, work, today, status, doctor, restart, shutdown)
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from aios.local.cli_workspace_commands import (
    cmd_dashboard,
    cmd_doctor,
    cmd_restart,
    cmd_shutdown,
    cmd_status,
    cmd_today,
    cmd_work,
    cmd_workspace_main,
    load_workspace_session,
    run_diagnostics,
    save_workspace_session,
)
from aios.registry import ServiceRegistry
from aios.services.context import ContextService, WorkspaceContext
from aios.services.daily import DailyOSService, DailyTask
from aios.services.developer_workspace import DeveloperWorkspaceInfo, DeveloperWorkspaceService
from aios.services.github import GitHubService
from aios.services.notion import NotionService
from aios.services.runtime import RuntimeService, RuntimeSession
from aios.services.supabase import SupabaseService


@pytest.fixture
def mock_registry():
    """Returns a ServiceRegistry with mock services."""
    registry = MagicMock(spec=ServiceRegistry)

    # Mock RuntimeService
    runtime_svc = MagicMock(spec=RuntimeService)
    sess = RuntimeSession(
        session_id="test_sess_123",
        workspace_root=".",
        created_at=123456789.0,
    )
    runtime_svc.get_session.return_value = sess
    runtime_svc.watcher_manager = MagicMock()
    runtime_svc.watcher_manager._watchers = [MagicMock(), MagicMock()]

    # Mock DeveloperWorkspaceService
    dev_ws_svc = MagicMock(spec=DeveloperWorkspaceService)
    ws_info = DeveloperWorkspaceInfo(
        git_status="M file.py",
        git_diff_summary="1 file changed, 1 insertion(+)",
        staged_files=["staged.py"],
        unstaged_files=["unstaged.py"],
        untracked_files=["untracked.py"],
        detected_tests=["test_file.py"],
        build_systems=["poetry"],
        linters=["ruff"],
        diagnostics={"uncommitted_files_count": 2},
        extra={"git_branch": "feature-branch"},
    )
    dev_ws_svc.get_workspace_info.return_value = ws_info

    # Mock ContextService
    context_svc = MagicMock(spec=ContextService)
    ctx = WorkspaceContext(
        working_directory=".",
        git_repo_path="/repo",
        git_branch="feature-branch",
        project_root=".",
        project_name="Aios",
    )
    context_svc.get_current_context.return_value = ctx

    # Mock DailyOSService
    daily_svc = MagicMock(spec=DailyOSService)
    task1 = DailyTask(
        task_id="T1",
        title="Implement Phase 2",
        priority="High",
        effort_hours=4.0,
        completed=True,
        status="Completed",
    )
    task2 = DailyTask(
        task_id="T2",
        title="Write tests",
        priority="Medium",
        effort_hours=2.0,
        completed=False,
        status="In Progress",
    )
    daily_svc.progress_tracker.list_tasks.return_value = [task1, task2]

    # Mock NotionService
    notion_svc = MagicMock(spec=NotionService)
    notion_svc.get_status.return_value = {
        "status": "connected",
        "workspaces": ["MyNotionWorkspace"],
    }

    # Mock GitHubService
    github_svc = MagicMock(spec=GitHubService)
    github_svc._token = "mock-token"
    github_svc._base_url = "https://api.github.com"

    # Mock SupabaseService
    supabase_svc = MagicMock(spec=SupabaseService)
    supabase_svc._url = "https://supabase.co"

    # Setup get side-effect mapping
    def get_service(cls):
        mapping = {
            RuntimeService: runtime_svc,
            DeveloperWorkspaceService: dev_ws_svc,
            ContextService: context_svc,
            DailyOSService: daily_svc,
            NotionService: notion_svc,
            GitHubService: github_svc,
            SupabaseService: supabase_svc,
        }
        if cls in mapping:
            return mapping[cls]
        raise KeyError(f"Service {cls} not mock-registered")

    registry.get.side_effect = get_service
    return registry


# ---------------------------------------------------------------------------
# Tests: Session Persistence
# ---------------------------------------------------------------------------


class TestSessionPersistence:
    def test_load_session_returns_default_when_no_file(self, tmp_path):
        with patch(
            "aios.local.cli_workspace_commands.SESSION_METADATA_PATH", tmp_path / "missing.json"
        ):
            data = load_workspace_session()
            assert data["current_project"] == "Aios"
            assert data["active_sprint"] == "Sprint 31"

    def test_save_and_load_session(self, tmp_path):
        sess_file = tmp_path / "session.json"
        with patch("aios.local.cli_workspace_commands.SESSION_METADATA_PATH", sess_file):
            custom_data = {
                "current_project": "CustomProject",
                "active_sprint": "Sprint 99",
                "previous_workspace_root": "/custom/path",
                "recent_commands": ["status"],
                "session_memory": "Memory details",
            }
            save_workspace_session(custom_data)
            loaded = load_workspace_session()
            assert loaded["current_project"] == "CustomProject"
            assert loaded["active_sprint"] == "Sprint 99"
            assert loaded["previous_workspace_root"] == "/custom/path"


# ---------------------------------------------------------------------------
# Tests: Health Checks
# ---------------------------------------------------------------------------


class TestDiagnostics:
    def test_run_diagnostics_python_check(self):
        res = run_diagnostics()
        assert "Python" in res
        assert res["Python"]["status"] == "Healthy"
        assert "v" in res["Python"]["details"]

    def test_run_diagnostics_git_check_in_repo(self):
        with (
            patch("shutil.which", return_value="/usr/bin/git"),
            patch("subprocess.run") as mock_run,
        ):
            # Mock repo validation
            mock_res1 = MagicMock()
            mock_res1.returncode = 0
            mock_res1.stdout = "true"

            mock_res2 = MagicMock()
            mock_res2.returncode = 0
            mock_res2.stdout = "main"

            mock_run.side_effect = [mock_res1, mock_res2]

            res = run_diagnostics()
            assert res["Git"]["status"] == "Healthy"
            assert "Branch: main" in res["Git"]["details"]

    def test_run_diagnostics_external_hdd_check(self, tmp_path):
        # When path exists (mocked as existing)
        with patch("pathlib.Path.exists", return_value=True):
            res = run_diagnostics()
            assert res["External HDD"]["status"] == "Healthy"

        # When path does not exist
        with patch("pathlib.Path.exists", return_value=False):
            res = run_diagnostics()
            assert res["External HDD"]["status"] == "Warning"


# ---------------------------------------------------------------------------
# Tests: Command Handlers
# ---------------------------------------------------------------------------


class TestCommandHandlers:
    def test_cmd_status_runs(self, mock_registry):
        # Simply verifying it completes without raising
        cmd_status([], mock_registry)

    def test_cmd_doctor_runs(self, mock_registry):
        cmd_doctor([], mock_registry)

    def test_cmd_today_runs(self, mock_registry):
        cmd_today([], mock_registry)

    def test_cmd_work_runs(self, mock_registry):
        cmd_work([], mock_registry)

    def test_cmd_dashboard_runs(self, mock_registry):
        cmd_dashboard([], mock_registry)

    def test_cmd_restart_runs(self, mock_registry):
        # Mock global registry or check services loop
        srv1 = MagicMock()
        srv1._lifecycle_ready = True
        mock_registry.get_all.return_value = [srv1]

        cmd_restart([], mock_registry)
        assert srv1.shutdown.called
        assert srv1.initialize.called
        assert srv1.start.called

    def test_cmd_shutdown_exits_gracefully(self, mock_registry):
        srv1 = MagicMock()
        srv1._lifecycle_ready = True
        mock_registry.get_all.return_value = [srv1]

        with pytest.raises(SystemExit):
            cmd_shutdown([], mock_registry)
        assert srv1.shutdown.called

    def test_cmd_workspace_main_dispatches_subcommand(self, mock_registry):
        with patch("aios.local.cli_workspace_commands.cmd_status") as mock_status:
            cmd_workspace_main(["status"], mock_registry)
            mock_status.assert_called_once_with([], mock_registry)
