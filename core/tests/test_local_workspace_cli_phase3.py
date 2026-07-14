"""
core/tests/test_local_workspace_cli_phase3.py

Production-quality tests for Phase 3: Daily Intelligence & Autonomous Workspace.
Tests:
- Morning Briefing
- Daily Planner and Priorities Sorting
- Workspace Intelligence Context Detection
- Session Continuation & Resuming
- Notion and GitHub Synchronization
- CRM Agency & Hackathons dashboards
- Notifications alerting engine
- Storing/Retrieving session memory
- CLI command routers
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from aios.local.cli_workspace_commands import (
    SESSION_METADATA_PATH,
    check_notifications,
    cmd_agency,
    cmd_agenda,
    cmd_github,
    cmd_hackathons,
    cmd_notion,
    cmd_projects,
    cmd_resume,
    detect_active_workspace,
    generate_daily_planner,
    run_morning_briefing,
    run_startup_automation,
    seed_data_files,
    sync_agency_info,
    sync_github_info,
)
from aios.registry import ServiceRegistry
from aios.services.context import ContextService, WorkspaceContext
from aios.services.daily import DailyOSService
from aios.services.developer_workspace import DeveloperWorkspaceInfo, DeveloperWorkspaceService
from aios.services.github import GitHubService
from aios.services.notion import NotionService
from aios.services.runtime import RuntimeService, RuntimeSession
from aios.services.supabase import SupabaseService


@pytest.fixture(autouse=True)
def cleanup_temp_files():
    """Cleanup test created file states."""
    # Ensure they are clean before test starts as well
    for p in (
        SESSION_METADATA_PATH,
        Path(".agent/hackathons.json"),
        Path(".agent/college.json"),
        Path(".agent/notifications.json"),
        Path(".agent/roadmap.json"),
    ):
        if p.is_file():
            try:
                p.unlink()
            except Exception:
                pass
    yield
    for p in (
        SESSION_METADATA_PATH,
        Path(".agent/hackathons.json"),
        Path(".agent/college.json"),
        Path(".agent/notifications.json"),
        Path(".agent/roadmap.json"),
    ):
        if p.is_file():
            try:
                p.unlink()
            except Exception:
                pass


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
    runtime_svc.watcher_manager._watchers = [MagicMock()]

    # Mock NotionService
    notion_svc = MagicMock(spec=NotionService)
    notion_svc.get_status.return_value = {"status": "connected", "workspaces": ["Test Workspace"]}

    # Mock GitHubService
    github_svc = MagicMock(spec=GitHubService)
    github_svc._token = "mock-token"
    github_svc._base_url = "https://api.github.com"
    github_svc.get_workflow_status.return_value = []
    github_svc.get_commit_history.return_value = []
    github_svc.get_milestones.return_value = []

    # Mock DailyOSService
    daily_svc = MagicMock(spec=DailyOSService)
    daily_svc.progress_tracker.list_tasks.return_value = []

    # Mock DeveloperWorkspaceService
    dev_ws_svc = MagicMock(spec=DeveloperWorkspaceService)
    ws_info = DeveloperWorkspaceInfo(
        git_status="Clean",
        git_diff_summary="",
        staged_files=[],
        unstaged_files=[],
        untracked_files=[],
        detected_tests=[],
        build_systems=[],
        linters=[],
        diagnostics={"uncommitted_files_count": 0},
        extra={"git_branch": "main"},
    )
    dev_ws_svc.get_workspace_info.return_value = ws_info

    # Mock ContextService
    context_svc = MagicMock(spec=ContextService)
    ctx = WorkspaceContext(
        working_directory=".",
        git_repo_path="/repo",
        git_branch="main",
        project_root=".",
        project_name="Aios",
    )
    context_svc.get_current_context.return_value = ctx

    # Mock SupabaseService
    supabase_svc = MagicMock(spec=SupabaseService)
    supabase_svc._url = "https://mock.supabase.co"

    def side_effect(service_type):
        if service_type == RuntimeService:
            return runtime_svc
        elif service_type == NotionService:
            return notion_svc
        elif service_type == GitHubService:
            return github_svc
        elif service_type == DailyOSService:
            return daily_svc
        elif service_type == DeveloperWorkspaceService:
            return dev_ws_svc
        elif service_type == ContextService:
            return context_svc
        elif service_type == SupabaseService:
            return supabase_svc
        return MagicMock()

    registry.get.side_effect = side_effect
    return registry


def test_seed_data_files():
    """Verifies that seed_data_files successfully creates the necessary files."""
    seed_data_files()
    assert SESSION_METADATA_PATH.is_file()
    assert Path(".agent/hackathons.json").is_file()
    assert Path(".agent/college.json").is_file()
    assert Path(".agent/notifications.json").is_file()
    assert Path(".agent/roadmap.json").is_file()


def test_detect_active_workspace():
    """Tests that active workspace context is resolved correctly."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="hackathon/ai-sprint\n")
        ws = detect_active_workspace()
        assert ws == "Hackathon"

        mock_run.return_value = MagicMock(returncode=0, stdout="agency/crm-leads\n")
        ws = detect_active_workspace()
        assert ws == "Agency"

        mock_run.return_value = MagicMock(returncode=0, stdout="main\n")
        ws = detect_active_workspace()
        assert ws in ("AI OS", "Agency", "Hackathon", "Portfolio", "College", "Research")


def test_sync_github_info(mock_registry):
    """Verifies that GitHub synchronizer successfully queries the service."""
    gh_svc = MagicMock(spec=GitHubService)
    gh_svc._token = "some-token"
    gh_svc._base_url = "https://api.github.com"
    mock_registry.get.side_effect = lambda x: gh_svc if x == GitHubService else MagicMock()

    res = sync_github_info(mock_registry)
    assert "repo_health" in res
    assert "current_milestone" in res
    assert "recent_commits" in res


def test_sync_agency_info():
    """Verifies that CRM Agency details are fetched properly."""
    res = sync_agency_info(None)
    assert "leads" in res
    assert len(res["leads"]) > 0
    assert "meetings" in res


def test_check_notifications(mock_registry):
    """Tests notification alert detection rules."""
    gh_info = {"failed_workflows": ["CI Pipeline"]}
    agency_info = {"meetings": [{"client": "Miller Retail", "time": "14:00", "topic": "proposals"}]}

    alerts = check_notifications(mock_registry, gh_info, agency_info)
    assert len(alerts) >= 2
    assert any(alert["title"] == "Failed GitHub Action" for alert in alerts)
    assert any(alert["title"] == "Upcoming Meeting" for alert in alerts)


def test_generate_daily_planner(mock_registry):
    """Tests consolidated daily planner generation."""
    gh_info = {"open_issues": ["Issue 1"]}
    agency_info = {"proposals": [{"title": "Chatbot Integration", "status": "Draft"}]}

    planner = generate_daily_planner(mock_registry, gh_info, agency_info)
    assert len(planner) > 0
    assert any(item["source"] == "GitHub Issue" for item in planner)


def test_morning_briefing_dashboard_run(mock_registry):
    """Verifies running Morning Briefing and Unified Dashboard without exceptions."""
    with patch("rich.console.Console.print"):
        run_morning_briefing(mock_registry)
        run_startup_automation(mock_registry)


def test_workspace_subcommands(mock_registry):
    """Verifies CLI subcommands print execution."""
    with patch("rich.console.Console.print"):
        cmd_agenda([], mock_registry)
        cmd_projects([], mock_registry)
        cmd_agency([], mock_registry)
        cmd_hackathons([], mock_registry)
        cmd_github([], mock_registry)
        cmd_notion([], mock_registry)
        cmd_resume([], mock_registry)
