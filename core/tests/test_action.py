import tempfile
from pathlib import Path
from unittest.mock import MagicMock

from aios.services.action.approval import ApprovalManager
from aios.services.action.executor import ActionExecutor
from aios.services.action.history import ActionHistory
from aios.services.action.models import ActionPlan, ActionStep, ActionType, RiskLevel
from aios.services.action.planner import ActionPlanner
from aios.services.tool import ToolResult


def test_action_models():
    step = ActionStep(
        description="write mock config",
        action_type=ActionType.WRITE,
        risk_level=RiskLevel.LOW,
        tool_name="filesystem",
        tool_args={"action": "write", "path": "mock.txt", "content": "hello"},
    )
    assert step.is_reversible is True
    assert step.status == "pending"

    plan = ActionPlan("Write mock file", steps=[step])
    assert plan.objective == "Write mock file"
    assert len(plan.steps) == 1

    d = plan.to_dict()
    assert d["objective"] == plan.objective

    loaded = ActionPlan.from_dict(d)
    assert loaded.id == plan.id
    assert len(loaded.steps) == 1
    assert loaded.steps[0].description == "write mock config"


def test_action_planning():
    planner = ActionPlanner()
    plan = planner.plan("write file config.json content settings")
    assert len(plan.steps) == 1
    assert plan.steps[0].action_type == ActionType.WRITE
    assert plan.steps[0].tool_args["path"] == "config.json"


def test_action_approval():
    plan = ActionPlan(
        "Test", steps=[ActionStep("step 1", ActionType.READ, RiskLevel.LOW, "filesystem", {})]
    )

    mgr = ApprovalManager()
    assert plan.status == "pending"
    mgr.approve_plan(plan)
    assert plan.status == "approved"
    assert plan.steps[0].status == "approved"

    mgr.reject_plan(plan)
    assert plan.status == "rejected"
    assert plan.steps[0].status == "rejected"


def test_action_execution_success():
    tool_svc = MagicMock()
    tool_svc.execute_tool.return_value = ToolResult(success=True, output="File content")

    step = ActionStep(
        description="write mock config",
        action_type=ActionType.WRITE,
        risk_level=RiskLevel.LOW,
        tool_name="filesystem",
        tool_args={"action": "write", "path": "mock.txt", "content": "hello"},
    )
    step.status = "approved"

    plan = ActionPlan("Write file", steps=[step])
    plan.status = "approved"

    executor = ActionExecutor(tool_svc)
    report = executor.execute_plan(plan)

    assert plan.status == "completed"
    assert step.status == "completed"
    assert "Execution Report" in report
    assert "Files Changed" in report


def test_action_execution_failure_and_rollback():
    tool_svc = MagicMock()
    tool_svc.execute_tool.side_effect = [
        ToolResult(success=True, output=""),
        ToolResult(success=False, output="", error="Write simulated error"),
        ToolResult(success=True, output=""),
    ]

    step = ActionStep(
        description="write mock config",
        action_type=ActionType.WRITE,
        risk_level=RiskLevel.LOW,
        tool_name="filesystem",
        tool_args={"action": "write", "path": "mock.txt", "content": "hello"},
        undo_args={"action": "delete", "path": "mock.txt"},
    )
    step.status = "approved"

    plan = ActionPlan("Write file", steps=[step])
    plan.status = "approved"

    executor = ActionExecutor(tool_svc)
    executor.execute_plan(plan)

    assert plan.status == "failed"
    assert step.status == "rolled_back"


def test_action_history():
    with tempfile.TemporaryDirectory() as tmpdir:
        history = ActionHistory(Path(tmpdir))

        plan = ActionPlan("Write file", steps=[])
        history.save_plan(plan)
        history.set_active_plan(plan)

        loaded_active = history.get_active_plan()
        assert loaded_active is not None
        assert loaded_active.id == plan.id

        loaded = history.load_plan(plan.id)
        assert loaded is not None
        assert loaded.id == plan.id

        plans = history.list_plans()
        assert len(plans) == 1

        history.clear_active_plan()
        assert history.get_active_plan() is None
