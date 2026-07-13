import json
from unittest.mock import MagicMock, patch

import pytest
from aios.services.career import CareerOSService, JobApplication
from aios.services.daily import (
    DailyOSService,
    DailySchedule,
    DailyTask,
    ScheduleItem,
    WorkSession,
)
from aios.services.daily_impl import (
    LocalDailyOSService,
    LocalDailyPlanner,
    LocalDailyReview,
    LocalPriorityCalculator,
    LocalProductivityAnalyzer,
    LocalProgressTracker,
    LocalScheduleOptimizer,
    LocalSessionRecorder,
    LocalWorkloadEstimator,
)
from aios.services.github import GitHubService
from aios.services.mission import Mission, MissionEngine
from aios.services.model import LLMResponse, ModelService
from aios.services.personal import Contact, Goal, PersonalProfile, PersonalService
from aios.services.project_intelligence import ProjectContext, ProjectIntelligenceService


@pytest.fixture
def mock_model_service():
    service = MagicMock(spec=ModelService)
    service.execute_request.return_value = LLMResponse(
        content="{}",
        model_name="mock-model",
        provider_name="mock-provider",
    )
    return service


@pytest.fixture
def mock_personal_service():
    service = MagicMock(spec=PersonalService)
    profile = PersonalProfile(
        id="professional",
        name="John Doe",
        contact=Contact(email="john@doe.com"),
        goals=[Goal(id="g_1", title="Transition to Management", target_date="2026-12-31")],
        knowledge=[],
    )
    service.get_active_profile.return_value = profile
    return service


@pytest.fixture
def mock_github_service():
    return MagicMock(spec=GitHubService)


@pytest.fixture
def mock_project_intel():
    service = MagicMock(spec=ProjectIntelligenceService)
    context = ProjectContext(
        project_root="/workspace",
        todo_markers=[{"file": "main.py", "line": 10, "text": "TODO: fix this"}],
        git_commits=["Init commit"],
    )
    service.analyze_workspace.return_value = context
    return service


@pytest.fixture
def mock_career_os():
    service = MagicMock(spec=CareerOSService)
    app = JobApplication(
        id="app_1", company="Google", role="SWE", status="applied", applied_date="2026-07-04"
    )
    service.application_tracker.list_applications.return_value = [app]
    return service


@pytest.fixture
def mock_registry():
    registry = MagicMock()
    mission_engine = MagicMock(spec=MissionEngine)

    mock_repo = MagicMock()
    mission = Mission(mission_id="m_1", title="Scale distributed databases", objective="scale db")
    mock_repo.list_missions.return_value = [mission]
    mission_engine._repository = mock_repo

    # Mock progress tracker for DailyOSService
    daily_os = MagicMock(spec=DailyOSService)
    mock_tracker = MagicMock()
    mock_tracker.list_tasks.return_value = [
        DailyTask(task_id="t1", title="Task 1", priority="High", effort_hours=2.0, completed=True)
    ]
    daily_os.progress_tracker = mock_tracker

    def lookup(cls):
        if cls == MissionEngine:
            return mission_engine
        if cls == DailyOSService:
            return daily_os
        return None

    registry.get.side_effect = lookup
    return registry


def test_priority_calculator(
    mock_model_service,
    mock_personal_service,
    mock_career_os,
    mock_registry,
    mock_project_intel,
):
    calc = LocalPriorityCalculator(
        mock_model_service,
        mock_personal_service,
        mock_career_os,
        mock_registry,
        mock_project_intel,
    )

    mock_model_service.execute_request.return_value = LLMResponse(
        content=json.dumps({"priority": "High"}),
        model_name="mock-model",
        provider_name="mock-provider",
    )

    task = DailyTask(
        task_id="t1",
        title="Prep interview coding challenges",
        priority="Medium",
        effort_hours=2.0,
        career_impact="High",
    )

    priority = calc.calculate_priority(task)
    assert priority == "High"


def test_workload_estimator():
    estimator = LocalWorkloadEstimator()

    tasks = [
        DailyTask(task_id="t1", title="Task 1", priority="High", effort_hours=3.0),
        DailyTask(task_id="t2", title="Task 2", priority="Medium", effort_hours=6.0),
    ]

    metrics = estimator.estimate_workload(tasks)
    assert metrics["total_work_hours"] == 9.0
    assert metrics["overloaded_schedule_detected"] is True
    assert metrics["free_capacity_hours"] == 0.0


def test_schedule_optimizer(mock_model_service):
    optimizer = LocalScheduleOptimizer(mock_model_service)

    mock_model_service.execute_request.return_value = LLMResponse(
        content=json.dumps(
            [
                {
                    "time_slot": "09:00 - 10:30",
                    "task_id": "t1",
                    "task_title": "Fix DB",
                    "item_type": "focus",
                },
                {
                    "time_slot": "10:30 - 10:45",
                    "task_id": "break",
                    "task_title": "Break",
                    "item_type": "break",
                },
            ]
        ),
        model_name="mock-model",
        provider_name="mock-provider",
    )

    tasks = [
        DailyTask(task_id="t1", title="Fix DB", priority="Critical", effort_hours=1.5),
    ]

    schedule = optimizer.optimize_schedule(tasks)
    assert len(schedule.items) == 2
    assert schedule.items[0].item_type == "focus"


def test_progress_tracking(mock_personal_service):
    tracker = LocalProgressTracker(mock_personal_service)

    # Save seed tasks
    tasks = [
        DailyTask(task_id="t1", title="Task 1", priority="Medium", effort_hours=1.0),
    ]
    tracker._save_tasks(tasks)

    # Move task to In Progress
    updated = tracker.update_task_status("t1", "In Progress")
    assert updated.status == "In Progress"
    assert updated.start_time is not None
    assert updated.completed is False

    # Complete task
    completed = tracker.update_task_status("t1", "Completed")
    assert completed.status == "Completed"
    assert completed.completed is True
    assert completed.finish_time is not None
    assert completed.completion_percentage == 100.0


def test_session_recording(mock_personal_service):
    recorder = LocalSessionRecorder(mock_personal_service)
    assert len(recorder.list_sessions()) == 0

    session = recorder.start_session("t1", "m1", "focus", "Coding login module")
    assert session.task_id == "t1"
    assert session.mission_id == "m1"
    assert session.notes == "Coding login module"
    assert session.end_time is None

    ended = recorder.end_session(session.session_id, "Completed login code")
    assert ended.end_time is not None
    assert ended.notes == "Completed login code"
    assert ended.duration_mins >= 0.0


def test_daily_review(
    mock_model_service,
    mock_personal_service,
    mock_career_os,
    mock_registry,
    mock_project_intel,
    mock_github_service,
):
    review_svc = LocalDailyReview(
        mock_model_service,
        mock_personal_service,
        mock_career_os,
        mock_registry,
        mock_project_intel,
        mock_github_service,
    )

    mock_model_service.execute_request.return_value = LLMResponse(
        content=json.dumps(
            {
                "completed_tasks": ["Task 1"],
                "incomplete_tasks": [],
                "mission_progress": ["databases Scaled"],
                "career_progress": ["ATS Resume Optimized"],
                "learning_progress": ["System design prep"],
                "project_activity": ["Git committed workspace changes"],
                "github_activity": [],
                "productivity_summary": "Highly productive day.",
                "tomorrow_priorities": ["Refactoring"],
                "suggested_improvements": ["Increase morning focus block duration"],
            }
        ),
        model_name="mock-model",
        provider_name="mock-provider",
    )

    summary = review_svc.generate_review()
    assert "Task 1" in summary.completed_tasks
    assert summary.productivity_summary == "Highly productive day."
    assert "Refactoring" in summary.tomorrow_priorities
    assert "Increase morning focus block duration" in summary.suggested_improvements

    # Check knowledge profile persistence
    profile = mock_personal_service.get_active_profile()
    history_entry = next(e for e in profile.knowledge if e.id == "daily_reviews_history")
    assert history_entry is not None
    assert "Highly productive day." in history_entry.content


def test_productivity_analyzer(mock_personal_service, mock_registry):
    analyzer = LocalProductivityAnalyzer(mock_personal_service, mock_registry)

    # Configure mock daily OS service registry
    daily_os = MagicMock(spec=DailyOSService)

    # Mock progress tracker and session recorder
    mock_tracker = MagicMock()
    mock_tracker.list_tasks.return_value = [
        DailyTask(
            task_id="t1",
            title="Task 1",
            priority="High",
            effort_hours=2.0,
            estimated_duration_mins=120.0,
            actual_duration_mins=120.0,
            completed=True,
        )
    ]
    mock_recorder = MagicMock()
    mock_recorder.list_sessions.return_value = [
        WorkSession(
            session_id="s1", start_time=0.0, end_time=3600.0, duration_mins=60.0, category="focus"
        )
    ]

    daily_os.progress_tracker = mock_tracker
    daily_os.session_recorder = mock_recorder
    mock_registry.get.side_effect = lambda cls: daily_os

    metrics = analyzer.analyze_productivity()
    assert metrics["completion_rate"] == 100.0
    assert metrics["focus_time_mins"] == 60.0
    assert metrics["planning_accuracy_percentage"] == 100.0
    assert metrics["total_tasks_completed"] == 1


def test_daily_planner(
    mock_model_service,
    mock_personal_service,
    mock_github_service,
    mock_project_intel,
    mock_career_os,
    mock_registry,
):
    planner = LocalDailyPlanner(
        mock_model_service,
        mock_personal_service,
        mock_github_service,
        mock_project_intel,
        mock_career_os,
        mock_registry,
    )

    service = LocalDailyOSService(
        model_service=mock_model_service,
        personal_service=mock_personal_service,
        github_service=mock_github_service,
        project_intel=mock_project_intel,
        career_os=mock_career_os,
        registry=mock_registry,
    )

    def custom_lookup(cls):
        if cls == DailyOSService:
            return service
        from aios.services.mission import MissionEngine

        if cls == MissionEngine:
            mission_engine = MagicMock(spec=MissionEngine)
            mock_repo = MagicMock()
            mission = Mission(mission_id="m_1", title="Scale databases", objective="scale db")
            mock_repo.list_missions.return_value = [mission]
            mission_engine._repository = mock_repo
            return mission_engine
        return None

    mock_registry.get.side_effect = custom_lookup

    mock_model_service.execute_request.return_value = LLMResponse(
        content=json.dumps({"priority": "High"}),
        model_name="mock-model",
        provider_name="mock-provider",
    )

    with patch.object(service.schedule_optimizer, "optimize_schedule") as mock_opt:
        mock_opt.return_value = DailySchedule(
            items=[
                ScheduleItem(
                    time_slot="09:00 - 11:00", task_id="task_1", task_title="Review missions"
                )
            ]
        )
        plan = planner.plan_day()
        assert plan.date == "2026-07-04"
        assert plan.workload_summary["total_work_hours"] == 4.5
        assert len(plan.tasks) == 3
        assert plan.schedule.items[0].task_id == "task_1"
