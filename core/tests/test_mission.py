import tempfile
from pathlib import Path
from unittest.mock import MagicMock

from aios.services.agent import AgentResult
from aios.services.mission import MissionStatus, MissionGoal, MissionContext
from aios.services.mission_impl import (
    LocalMissionPlanner,
    LocalMissionExecutor,
    LocalMissionRepository,
    LocalMissionEngine,
)


def test_mission_planner_and_task_decomposition():
    planner = LocalMissionPlanner()
    ctx = MissionContext()

    # 1. Career objective
    mission_career = planner.plan_mission("I want to find a Python AI internship", ctx)
    assert mission_career.title == "Career Internship Acquisition"
    assert len(mission_career.milestones) == 3
    assert mission_career.milestones[0].tasks[0].assigned_agent == "career_agent"

    # 2. Learning objective
    mission_learn = planner.plan_mission("I want to study Kubernetes production clusters", ctx)
    assert mission_learn.title == "Production Kubernetes Certification"
    assert len(mission_learn.milestones) == 2
    assert mission_learn.milestones[0].tasks[0].assigned_agent == "career_agent"

    # 3. Default objective
    mission_default = planner.plan_mission("Optimize AI OS workspace", ctx)
    assert mission_default.title == "Personal AI OS Core Roadmap"
    assert len(mission_default.milestones) == 2
    assert mission_default.milestones[0].tasks[0].assigned_agent == "developer_agent"


def test_mission_repository_persistence():
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = LocalMissionRepository(cache_filename="missions_cache.json", workspace_root=tmpdir)
        repo.initialize()

        planner = LocalMissionPlanner()
        ctx = MissionContext()
        mission = planner.plan_mission("study Kubernetes course", ctx)
        mission.mission_id = "test-mission-123"

        repo.save_mission(mission)

        # Reload
        repo2 = LocalMissionRepository(cache_filename="missions_cache.json", workspace_root=tmpdir)
        repo2.initialize()
        loaded = repo2.load_mission("test-mission-123")
        assert loaded is not None
        assert loaded.title == "Production Kubernetes Certification"
        assert loaded.status == MissionStatus.PENDING


def test_mission_execution_success():
    runtime = MagicMock()
    # Mock successful agent execution
    mock_res = MagicMock()
    mock_res.success = True
    mock_res.response = "Done!"
    runtime.execute.return_value = mock_res

    executor = LocalMissionExecutor(runtime)
    planner = LocalMissionPlanner()
    ctx = MissionContext()
    mission = planner.plan_mission("I want an AI internship", ctx)

    success = executor.execute_mission(mission, ctx)
    assert success is True
    assert mission.status == MissionStatus.COMPLETED
    assert mission.milestones[0].status == MissionStatus.COMPLETED
    assert mission.milestones[0].tasks[0].status == MissionStatus.COMPLETED
    assert mission.milestones[0].tasks[0].result == "Done!"


def test_mission_execution_cancellation():
    runtime = MagicMock()
    mock_res = MagicMock()
    mock_res.success = True
    mock_res.response = "Done!"
    runtime.execute.return_value = mock_res

    executor = LocalMissionExecutor(runtime)
    planner = LocalMissionPlanner()
    ctx = MissionContext()
    mission = planner.plan_mission("I want an AI internship", ctx)
    mission.mission_id = "cancellable-1"

    # Cancel before execution starts
    executor.cancel("cancellable-1")
    success = executor.execute_mission(mission, ctx)

    assert success is False
    assert mission.status == MissionStatus.CANCELLED


def test_resume_after_interruption():
    runtime = MagicMock()
    # Mock success
    mock_res = MagicMock()
    mock_res.success = True
    mock_res.response = "Success output"
    runtime.execute.return_value = mock_res

    executor = LocalMissionExecutor(runtime)
    planner = LocalMissionPlanner()
    ctx = MissionContext()
    mission = planner.plan_mission("I want an AI internship", ctx)

    # Let's say milestone 0 is already completed, and index is set to 1
    mission.current_milestone_index = 1
    mission.milestones[0].status = MissionStatus.COMPLETED
    mission.milestones[0].tasks[0].status = MissionStatus.COMPLETED

    # Execute from index 1
    success = executor.execute_mission(mission, ctx)
    assert success is True
    assert mission.status == MissionStatus.COMPLETED
    assert mission.current_milestone_index == 2
    # Verify runtime was called for the remaining steps (ATS score + Tailoring letters)
    assert runtime.execute.call_count == 2
