"""
core/tests/test_local_core_intelligence_phase4.py

Production-quality tests for Phase 4: Core Intelligence Layer.
Tests:
- Task Engine
- Decision Engine
- Context Engine
- Event Bus
- Notification Center
- Goal Engine
- Priority Engine
- Scheduler
- Plugin Registry
- Skill Registry
- Universal Action Engine
- Memory Index
- AI Planner
- AI Supervisor
- CLI Integration & Dashboard Renders
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from aios.local.cli_workspace_commands import (
    cmd_context,
    cmd_dashboard,
    cmd_events,
    cmd_goals,
    cmd_notifications,
    cmd_planner,
    cmd_plugins,
    cmd_scheduler,
    cmd_skills,
    cmd_tasks,
)
from aios.local.core_intelligence import (
    ActionEngine,
    AIPlanner,
    AISupervisor,
    ContextEngine,
    CoreContext,
    DecisionEngine,
    Event,
    EventBus,
    Goal,
    GoalEngine,
    MemoryIndex,
    NotificationCenter,
    Plugin,
    PluginRegistry,
    PriorityEngine,
    Scheduler,
    Skill,
    SkillRegistry,
    Task,
    TaskEngine,
)
from aios.registry import ServiceRegistry


@pytest.fixture(autouse=True)
def cleanup_temp_files():
    """Cleanup temporary files created by Phase 4 engines."""
    temp_files = [
        Path(".agent/tasks.json"),
        Path(".agent/goals.json"),
        Path(".agent/context.json"),
        Path(".agent/plugins.json"),
        Path(".agent/skills.json"),
        Path(".agent/notifications.json"),
        Path(".agent/memory_index.json"),
        Path(".agent/scheduler.json"),
    ]
    for p in temp_files:
        if p.is_file():
            try:
                p.unlink()
            except Exception:
                pass
    yield
    for p in temp_files:
        if p.is_file():
            try:
                p.unlink()
            except Exception:
                pass


def test_task_engine():
    """Verifies that the Task Engine stores, updates, and deletes tasks correctly."""
    engine = TaskEngine(storage_path=Path(".agent/tasks.json"))
    task = Task(
        "t_001", "Build CLI", "Implement Phase 4 CLI", "Critical", "Aios", "AI OS", "Pending"
    )

    engine.create_task(task)
    assert len(engine.list_tasks()) == 1
    assert engine.get_task("t_001").status == "Pending"

    engine.update_task("t_001", {"status": "Completed"})
    assert engine.get_task("t_001").status == "Completed"
    assert engine.get_task("t_001").completed_time is not None

    engine.delete_task("t_001")
    assert len(engine.list_tasks()) == 0


def test_decision_engine():
    """Tests model, tool, and retry strategy routing by the Decision Engine."""
    engine = DecisionEngine()

    # Priority deepseek-r1 check
    assert engine.choose_model("Critical", "generate_code") == "deepseek-r1"
    assert engine.choose_model("Low", "summarize") == "gemma3:4b"

    # Tool choice routing
    assert engine.choose_tool("write python code") == "DeveloperWorkspaceTool"
    assert engine.choose_tool("create meeting") == "AgencyCRMTool"

    # Retry strategy check
    strat = engine.choose_retry_strategy("Failed")
    assert strat["max_retries"] == 3


def test_context_engine():
    """Verifies Context Engine state persistence."""
    engine = ContextEngine(storage_path=Path(".agent/context.json"))
    ctx = engine.get_current()
    assert ctx.current_project == "Aios"

    engine.update_context({"current_project": "AgencyCRM", "current_sprint": "Sprint 32"})
    assert engine.get_current().current_project == "AgencyCRM"
    assert engine.get_current().current_sprint == "Sprint 32"

    # Re-instantiate should reload from disk
    engine2 = ContextEngine(storage_path=Path(".agent/context.json"))
    assert engine2.get_current().current_project == "AgencyCRM"


def test_event_bus():
    """Verifies publish-subscribe pattern on the EventBus."""
    bus = EventBus()
    received_data = []

    def on_event(ev: Event):
        received_data.append(ev.data["value"])

    bus.subscribe("TaskCreated", on_event)
    bus.publish(Event("TaskCreated", {"value": "t_002"}))

    assert len(received_data) == 1
    assert received_data[0] == "t_002"


def test_notification_center():
    """Tests Notification Center logging and levels filtering."""
    center = NotificationCenter(storage_path=Path(".agent/notifications.json"))
    center.create_notification("HDD Alert", "External HDD disconnected", "Error")
    center.create_notification("Service Online", "Kernel loaded", "Info")

    assert len(center.list_notifications()) == 2

    # Filter critical errors
    errs = center.list_notifications(min_severity="Error")
    assert len(errs) == 1
    assert errs[0].title == "HDD Alert"


def test_goal_engine():
    """Tests Goal Engine achievements lifecycle."""
    engine = GoalEngine(storage_path=Path(".agent/goals.json"))
    goal = Goal("g_001", "Launch Phase 4", "Sprint", "2026-07-20", "Pending")

    engine.create_goal(goal)
    assert len(engine.list_goals(category="Sprint")) == 1

    engine.update_goal("g_001", {"status": "Achieved", "progress": 100.0})
    assert engine.get_goal("g_001").status == "Achieved"


def test_priority_engine():
    """Tests priority calculations."""
    engine = PriorityEngine()
    context = CoreContext(current_project="Aios")

    t1 = Task("t1", "Task 1", "desc", "Critical", "Aios", "AI OS", "Pending")
    t2 = Task("t2", "Task 2", "desc", "Low", "OtherProj", "OtherWS", "Pending")

    score1 = engine.calculate_priority_score(t1, context)
    score2 = engine.calculate_priority_score(t2, context)
    assert score1 > score2


def test_scheduler():
    """Verifies that Scheduler registers and updates job execution times."""
    sch = Scheduler(storage_path=Path(".agent/scheduler.json"))
    sch.register_job("health_checks", 60.0)

    jobs = sch.list_jobs()
    assert "health_checks" in jobs
    assert jobs["health_checks"]["last_run"] == 0.0

    sch.trigger_job("health_checks")
    assert sch.list_jobs()["health_checks"]["last_run"] > 0.0


def test_plugin_and_skill_registries():
    """Tests PluginRegistry and SkillRegistry seeding and lookup."""
    p_reg = PluginRegistry(storage_path=Path(".agent/plugins.json"))
    s_reg = SkillRegistry(storage_path=Path(".agent/skills.json"))

    assert len(p_reg.list_plugins()) >= 4
    assert len(s_reg.list_skills()) >= 9

    # Add custom plugin/skill
    p_reg.register_plugin(Plugin("CustomPlugin", "1.0.0", [], [], "Healthy", "Active"))
    s_reg.register_skill(Skill("CustomSkill", "desc", "type", "Low"))

    assert any(p.name == "CustomPlugin" for p in p_reg.list_plugins())
    assert any(s.name == "CustomSkill" for s in s_reg.list_skills())


def test_action_engine():
    """Verifies Action Engine execution routing."""
    engine = ActionEngine()
    mock_func = MagicMock(return_value="Issue-101")

    engine.register_action("GitHub", "CreateIssue", mock_func)
    res = engine.execute_action("GitHub", "CreateIssue", title="Bug 1")

    assert res == "Issue-101"
    mock_func.assert_called_once_with(title="Bug 1")


def test_memory_index():
    """Tests tagging and fetching indexed memory documents."""
    idx = MemoryIndex(storage_path=Path(".agent/memory_index.json"))
    idx.index_item("Benchmarks", "bench_001", {"score": 98.5})

    res = idx.search_category("Benchmarks")
    assert len(res) == 1
    assert res[0]["item_id"] == "bench_001"


def test_ai_planner_and_supervisor():
    """Verifies Planner breakdowns and Supervisor recovery strategy checks."""
    planner = AIPlanner()
    tasks = planner.plan_objective("Build CRM")
    assert len(tasks) == 4
    assert tasks[0].dependencies == []
    assert "plan_1" in tasks[1].dependencies

    supervisor = AISupervisor()
    assert supervisor.run_recovery_strategy("TaskEngine") is True

    # Test monitoring status report
    registry = MagicMock(spec=ServiceRegistry)
    svc1 = MagicMock()
    svc1._state = "HALTED"
    registry.get_all.return_value = [svc1]

    report = supervisor.monitor_services(registry)
    assert report["status"] == "Degraded"
    assert report["failed_count"] == 1


def test_cli_subcommands_render():
    """Tests execution flow of Core CLI commands."""
    registry = MagicMock(spec=ServiceRegistry)

    # Configure mock registry to return default Core Intelligence Engines
    task_engine = TaskEngine(storage_path=Path(".agent/tasks.json"))
    goal_engine = GoalEngine(storage_path=Path(".agent/goals.json"))
    plugin_reg = PluginRegistry(storage_path=Path(".agent/plugins.json"))
    skill_reg = SkillRegistry(storage_path=Path(".agent/skills.json"))
    scheduler = Scheduler(storage_path=Path(".agent/scheduler.json"))
    notif_center = NotificationCenter(storage_path=Path(".agent/notifications.json"))
    context_engine = ContextEngine(storage_path=Path(".agent/context.json"))
    ai_planner = AIPlanner()

    def side_effect(service_type):
        if service_type.__name__ == "TaskEngine":
            return task_engine
        elif service_type.__name__ == "GoalEngine":
            return goal_engine
        elif service_type.__name__ == "PluginRegistry":
            return plugin_reg
        elif service_type.__name__ == "SkillRegistry":
            return skill_reg
        elif service_type.__name__ == "Scheduler":
            return scheduler
        elif service_type.__name__ == "NotificationCenter":
            return notif_center
        elif service_type.__name__ == "ContextEngine":
            return context_engine
        elif service_type.__name__ == "AIPlanner":
            return ai_planner
        return MagicMock()

    registry.get.side_effect = side_effect

    with patch("rich.console.Console.print"):
        cmd_tasks(["create", "Task 1", "Desc 1", "High"], registry)
        cmd_tasks([], registry)
        cmd_tasks(["complete", "task_123"], registry)

        cmd_goals(["create", "Goal 1", "Sprint", "2026-07-20"], registry)
        cmd_goals([], registry)
        cmd_goals(["achieve", "goal_123"], registry)

        cmd_planner(["Build", "CRM"], registry)
        cmd_plugins([], registry)
        cmd_skills([], registry)

        cmd_notifications(["create", "T1", "M1", "Info"], registry)
        cmd_notifications([], registry)

        cmd_events([], registry)
        cmd_context([], registry)
        cmd_scheduler([], registry)
        cmd_dashboard([], registry)
