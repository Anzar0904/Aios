from unittest.mock import MagicMock

import pytest
from aios.brain.models import Workflow, WorkflowStep
from aios.brain.workflow import (
    WorkflowExecutor,
    group_steps_into_levels,
    visualize_workflow_graph,
)


def test_linear_workflow_grouping():
    # Linear: s1 -> s2 -> s3
    s1 = WorkflowStep(step_id="s1", description="Step 1", skill_id="sys", command="cmd", args="")
    s2 = WorkflowStep(
        step_id="s2",
        description="Step 2",
        skill_id="sys",
        command="cmd",
        args="",
        depends_on=["s1"],
    )
    s3 = WorkflowStep(
        step_id="s3",
        description="Step 3",
        skill_id="sys",
        command="cmd",
        args="",
        depends_on=["s2"],
    )

    grouped = group_steps_into_levels([s1, s2, s3])
    assert len(grouped) == 3
    assert grouped[0] == [s1]
    assert grouped[1] == [s2]
    assert grouped[2] == [s3]


def test_parallel_workflow_grouping():
    # Parallel paths:
    # s1 -> s2
    # s3 -> s4
    s1 = WorkflowStep(step_id="s1", description="Step 1", skill_id="sys", command="cmd", args="")
    s2 = WorkflowStep(
        step_id="s2",
        description="Step 2",
        skill_id="sys",
        command="cmd",
        args="",
        depends_on=["s1"],
    )
    s3 = WorkflowStep(step_id="s3", description="Step 3", skill_id="sys", command="cmd", args="")
    s4 = WorkflowStep(
        step_id="s4",
        description="Step 4",
        skill_id="sys",
        command="cmd",
        args="",
        depends_on=["s3"],
    )

    grouped = group_steps_into_levels([s1, s2, s3, s4])
    assert len(grouped) == 2
    # Level 0 contains s1 and s3
    assert len(grouped[0]) == 2
    assert s1 in grouped[0]
    assert s3 in grouped[0]
    # Level 1 contains s2 and s4
    assert len(grouped[1]) == 2
    assert s2 in grouped[1]
    assert s4 in grouped[1]


def test_invalid_dependency_error():
    s1 = WorkflowStep(
        step_id="s1",
        description="Step 1",
        skill_id="sys",
        command="cmd",
        args="",
        depends_on=["nonexistent"],
    )
    with pytest.raises(ValueError) as exc:
        group_steps_into_levels([s1])
    assert "depends on non-existent step" in str(exc.value)


def test_circular_dependency_error():
    # s1 -> s2 -> s1
    s1 = WorkflowStep(step_id="s1", description="Step 1", skill_id="sys", command="cmd", args="")
    s2 = WorkflowStep(
        step_id="s2",
        description="Step 2",
        skill_id="sys",
        command="cmd",
        args="",
        depends_on=["s1"],
    )
    s1.depends_on = ["s2"]

    with pytest.raises(ValueError) as exc:
        group_steps_into_levels([s1, s2])
    assert "Circular dependency detected" in str(exc.value)


def test_visualization_output():
    s1 = WorkflowStep(step_id="s1", description="Step 1", skill_id="sys", command="cmd", args="")
    s2 = WorkflowStep(
        step_id="s2",
        description="Step 2",
        skill_id="sys",
        command="cmd",
        args="",
        depends_on=["s1"],
    )

    viz = visualize_workflow_graph([s1, s2])
    assert "Level 0" in viz
    assert "Level 1" in viz
    assert "s1" in viz
    assert "s2" in viz


def test_executor_executes_by_levels():
    kernel = MagicMock()
    command_registry = MagicMock()
    tool_service = MagicMock()
    kernel.registry.get.return_value = tool_service

    execution_order = []

    def make_handler(name):
        def handler(args):
            execution_order.append(name)
            return f"{name} done"

        return handler

    command_registry.get_handler.side_effect = lambda cmd: {
        "c1": make_handler("c1"),
        "c2": make_handler("c2"),
        "c3": make_handler("c3"),
    }.get(cmd)

    s1 = WorkflowStep(step_id="s1", description="Step 1", skill_id="sys", command="c1", args="")
    # s2 depends on s1
    s2 = WorkflowStep(
        step_id="s2", description="Step 2", skill_id="sys", command="c2", args="", depends_on=["s1"]
    )
    # s3 is independent (Level 0)
    s3 = WorkflowStep(step_id="s3", description="Step 3", skill_id="sys", command="c3", args="")

    wf = Workflow(workflow_id="wf1", objective="run test", steps=[s1, s2, s3])
    executor = WorkflowExecutor(kernel, command_registry)

    success = executor.execute(wf)
    assert success is True
    assert wf.status == "completed"

    # Verify s1 and s3 run before s2 (since s2 depends on s1)
    assert "c2" in execution_order
    c2_index = execution_order.index("c2")
    c1_index = execution_order.index("c1")
    assert c1_index < c2_index
