"""Phase 11: Personal Intelligence — Production Test Suite.

Tests cover:
- Personal Goals CRUD & retrieval
- Personal Tasks CRUD & retrieval
- Calendar events & overlap conflict detection
- Habits streaks & consistency scoring
- Reminders creation & listings
- Notes catalog bookmarks
- Learning items progress
- AI Coach insights recommendations
- Knowledge Graph bridging integration assertions
- CLI command dispatcher smoke runs
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from aios.services.personal import (
    CalendarEvent,
    Habit,
    PersonalGoal,
    PersonalLearningItem,
    PersonalReminder,
    PersonalTask,
)
from aios.services.personal_impl import LocalPersonalService

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def tmp_db(tmp_path):
    return str(tmp_path)


@pytest.fixture
def eng(tmp_db):
    from aios.local import personal_commands

    personal_commands._DB_PATH = tmp_db
    svc = LocalPersonalService(workspace_root=tmp_db)
    svc.initialize()
    svc.start()
    yield svc
    svc.shutdown()
    personal_commands._DB_PATH = None


# ---------------------------------------------------------------------------
# Personal Goals Tests
# ---------------------------------------------------------------------------


class TestPersonalGoals:
    def test_seeded_goals(self, eng):
        goals = eng.list_goals()
        assert len(goals) >= 1
        assert goals[0].title == "Master Agentic Programming"

    def test_create_and_get_goal(self, eng):
        g = PersonalGoal(
            goal_id="goal_test_1",
            title="Read 10 Books",
            timeframe="annual",
            category="personal",
        )
        eng.create_goal(g)
        fetched = eng.get_goal("goal_test_1")
        assert fetched is not None
        assert fetched.title == "Read 10 Books"


# ---------------------------------------------------------------------------
# Personal Tasks Tests
# ---------------------------------------------------------------------------


class TestPersonalTasks:
    def test_create_and_get_task(self, eng):
        t = PersonalTask(
            task_id="task_test_1",
            title="Write test suite",
            category="learning",
        )
        eng.create_task(t)
        fetched = eng.get_task("task_test_1")
        assert fetched is not None
        assert fetched.title == "Write test suite"


# ---------------------------------------------------------------------------
# Calendar Events Tests
# ---------------------------------------------------------------------------


class TestCalendarEvents:
    def test_create_and_detect_conflicts(self, eng):
        e1 = CalendarEvent(
            event_id="e1",
            title="Standup",
            start_time=1000.0,
            end_time=2000.0,
            category="meeting",
        )
        e2 = CalendarEvent(
            event_id="e2",
            title="Client Call",
            start_time=1500.0,
            end_time=2500.0,
            category="meeting",
        )
        eng.create_event(e1)
        eng.create_event(e2)

        conflicts = eng.detect_calendar_conflicts()
        assert len(conflicts) == 1
        assert conflicts[0]["event_1"] == "Standup"
        assert conflicts[0]["event_2"] == "Client Call"


# ---------------------------------------------------------------------------
# Habits Tests
# ---------------------------------------------------------------------------


class TestHabits:
    def test_create_and_streak(self, eng):
        h = Habit(
            habit_id="h1",
            name="Exercise",
            frequency="daily",
            streak=2,
        )
        eng.create_habit(h)
        eng.increment_habit_streak("h1")
        fetched = eng.get_habit("h1")
        assert fetched.streak == 3


# ---------------------------------------------------------------------------
# Reminders Tests
# ---------------------------------------------------------------------------


class TestReminders:
    def test_create_reminder(self, eng):
        r = PersonalReminder(
            reminder_id="r1",
            title="Call dad",
            trigger_time=2000.0,
            reminder_type="one_time",
        )
        eng.create_reminder(r)
        reminders = eng.list_reminders()
        assert len(reminders) >= 1


# ---------------------------------------------------------------------------
# Learning Topics Tests
# ---------------------------------------------------------------------------


class TestLearning:
    def test_create_learning_item(self, eng):
        item = PersonalLearningItem(
            item_id="l1",
            title="Vite React Guide",
            item_type="course",
            progress=50.0,
        )
        eng.create_learning_item(item)
        items = eng.list_learning_items()
        assert len(items) >= 1
        assert items[0].title == "Vite React Guide" or items[1].title == "Vite React Guide"


# ---------------------------------------------------------------------------
# AI Coach Tests
# ---------------------------------------------------------------------------


class TestAICoach:
    def test_coach_recommendations(self, eng):
        res = eng.get_coach_recommendations()
        assert "insights" in res
        assert "recommendations" in res
        assert len(res["recommendations"]) >= 1


# ---------------------------------------------------------------------------
# Knowledge Graph Integration
# ---------------------------------------------------------------------------


class TestPersonalGraphBridge:
    def test_sync_goal(self):
        from aios.services.personal_graph_bridge import PersonalGraphBridge

        mock_engine = MagicMock()
        mock_entity = MagicMock()
        mock_entity.entity_id = "mock-goal-id"
        mock_engine.ensure_entity.return_value = mock_entity

        bridge = PersonalGraphBridge(mock_engine)
        g = PersonalGoal("goal-123", "Run 5k", "monthly", "health")
        entity_id = bridge.sync_goal(g)
        assert entity_id == "mock-goal-id"

    def test_sync_task(self):
        from aios.services.personal_graph_bridge import PersonalGraphBridge

        mock_engine = MagicMock()
        mock_entity = MagicMock()
        mock_entity.entity_id = "mock-task-id"
        mock_engine.ensure_entity.return_value = mock_entity

        bridge = PersonalGraphBridge(mock_engine)
        t = PersonalTask("task-123", "Write code", "personal")
        entity_id = bridge.sync_task(t)
        assert entity_id == "mock-task-id"

    def test_sync_habit(self):
        from aios.services.personal_graph_bridge import PersonalGraphBridge

        mock_engine = MagicMock()
        mock_entity = MagicMock()
        mock_entity.entity_id = "mock-habit-id"
        mock_engine.ensure_entity.return_value = mock_entity

        bridge = PersonalGraphBridge(mock_engine)
        h = Habit("habit-123", "Drink water", "daily")
        entity_id = bridge.sync_habit(h)
        assert entity_id == "mock-habit-id"

    def test_sync_event(self):
        from aios.services.personal_graph_bridge import PersonalGraphBridge

        mock_engine = MagicMock()
        mock_entity = MagicMock()
        mock_entity.entity_id = "mock-event-id"
        mock_engine.ensure_entity.return_value = mock_entity

        bridge = PersonalGraphBridge(mock_engine)
        ev = CalendarEvent("event-123", "Standup meeting", 1000.0, 2000.0, "meeting")
        entity_id = bridge.sync_event(ev)
        assert entity_id == "mock-event-id"


# ---------------------------------------------------------------------------
# CLI Command Dispatcher Smoke Tests
# ---------------------------------------------------------------------------


class TestPersonalCLIDispatch:
    def test_cli_dashboard_smoke(self, eng):
        from aios.local.personal_commands import cmd_personal_main

        cmd_personal_main(["dashboard"])

    def test_cli_goals_smoke(self, eng):
        from aios.local.personal_commands import cmd_personal_main

        cmd_personal_main(["goals"])

    def test_cli_tasks_smoke(self, eng):
        from aios.local.personal_commands import cmd_personal_main

        cmd_personal_main(["tasks"])

    def test_cli_calendar_smoke(self, eng):
        from aios.local.personal_commands import cmd_personal_main

        cmd_personal_main(["calendar"])

    def test_cli_habits_smoke(self, eng):
        from aios.local.personal_commands import cmd_personal_main

        cmd_personal_main(["habits"])

    def test_cli_reminders_smoke(self, eng):
        from aios.local.personal_commands import cmd_personal_main

        cmd_personal_main(["reminders"])

    def test_cli_today_smoke(self, eng):
        from aios.local.personal_commands import cmd_personal_main

        cmd_personal_main(["today"])

    def test_cli_morning_smoke(self, eng):
        from aios.local.personal_commands import cmd_personal_main

        cmd_personal_main(["morning"])

    def test_cli_weekly_smoke(self, eng):
        from aios.local.personal_commands import cmd_personal_main

        cmd_personal_main(["weekly"])

    def test_cli_notes_smoke(self, eng):
        from aios.local.personal_commands import cmd_personal_main

        cmd_personal_main(["notes"])

    def test_cli_learning_smoke(self, eng):
        from aios.local.personal_commands import cmd_personal_main

        cmd_personal_main(["learning"])

    def test_cli_coach_smoke(self, eng):
        from aios.local.personal_commands import cmd_personal_main

        cmd_personal_main(["coach"])
