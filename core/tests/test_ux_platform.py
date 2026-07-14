from unittest.mock import patch

import pytest
from aios.cli import execute_builtin_cli_command
from aios.registry import ServiceRegistry
from aios.services.context import ContextService
from aios.services.context_impl import LocalContextService
from aios.services.event_bus_impl import LocalEventBus
from aios.services.graph import GraphService
from aios.services.graph_impl import GraphServiceImpl
from aios.services.ux_platform import UXPlatform
from aios.ux import BootExperience


@pytest.fixture
def setup_ux_services(tmp_path):
    event_bus = LocalEventBus()

    # Context
    context_svc = LocalContextService(event_bus)
    context_svc._context_path = tmp_path / "context.json"
    context_svc.initialize()

    # Graph
    graph_svc = GraphServiceImpl(db_path=str(tmp_path / "test_graph.db"))
    graph_svc.initialize()

    # UX Platform
    ux = UXPlatform(workspace_root=str(tmp_path))

    # Register globally
    registry = ServiceRegistry()
    ServiceRegistry._global_registry = registry
    registry.register(ContextService, context_svc)
    registry.register(GraphService, graph_svc)
    registry.register(UXPlatform, ux)

    ux.initialize()

    yield context_svc, graph_svc, ux

    ux.shutdown()
    ServiceRegistry._global_registry = None


def test_boot_experience():
    with patch("time.sleep", return_value=None):
        duration = BootExperience.boot()
        assert duration >= 0.0


def test_ux_platform_initialization(setup_ux_services):
    _, _, ux = setup_ux_services

    # Seeding checks
    assert len(ux.notifications) == 4
    categories = [n.category for n in ux.notifications]
    assert "workflow" in categories
    assert "agent" in categories
    assert "github" in categories
    assert "meeting" in categories


def test_theme_system(setup_ux_services):
    _, _, ux = setup_ux_services

    # Default Theme
    colors = ux.get_theme_colors()
    assert colors["primary"] == "cyan"

    # Switch to Minimal
    ux.current_theme = "minimal"
    colors_min = ux.get_theme_colors()
    assert colors_min["primary"] == "white"

    # Switch to Professional
    ux.current_theme = "professional"
    colors_prof = ux.get_theme_colors()
    assert colors_prof["primary"] == "blue"


def test_notification_center_operations(setup_ux_services):
    _, _, ux = setup_ux_services

    # Adding alert
    ux.add_notification(
        title="Proposal Generated",
        message="Outreach proposal generated for cyberdyne.",
        category="proposal",
        priority="high",
    )
    assert len(ux.notifications) == 5
    assert ux.notifications[-1].category == "proposal"

    # Filtering alerts
    workflow_alerts = ux.filter_notifications("workflow")
    assert len(workflow_alerts) == 1

    # Marking all as read
    ux.mark_all_read()
    unread = [n for n in ux.notifications if not n.read]
    assert len(unread) == 0


def test_universal_search(setup_ux_services):
    _, _, ux = setup_ux_services

    # Searching
    res = ux.universal_search("Wayne")
    assert len(res) > 0
    assert any("Wayne" in item["name"] or "Wayne" in item["desc"] for item in res)

    res_empty = ux.universal_search("NonExistentTermXYZ")
    assert len(res_empty) == 0


def test_status_bar_rendering(setup_ux_services):
    _, _, ux = setup_ux_services

    panel = ux.render_status_bar()
    assert panel is not None
    assert "Project:" in panel.renderable


def test_workspace_renderers(setup_ux_services):
    _, _, ux = setup_ux_services

    # Test all workspaces render without exceptions
    workspaces = [
        "dashboard",
        "project",
        "agency",
        "research",
        "github",
        "workflow",
        "agent",
        "notifications",
    ]
    for w in workspaces:
        ux.current_workspace = w
        ux.render_command_center()


def test_cli_ux_commands(setup_ux_services):
    _, _, ux = setup_ux_services

    with patch("aios.cli.execute_builtin_cli_command", return_value=True):
        res = execute_builtin_cli_command(["status"], exit_on_complete=False)
        assert res is True

        res = execute_builtin_cli_command(["notifications"], exit_on_complete=False)
        assert res is True

        res = execute_builtin_cli_command(["search", "Wayne"], exit_on_complete=False)
        assert res is True
