import tempfile
from pathlib import Path

from aios.services.command.metadata import CommandCategory, CommandMetadata
from aios.services.command.registry import CommandRegistry
from aios.services.task.executor import TaskExecutor
from aios.services.task.history import TaskHistory
from aios.services.task.models import Task, TaskStep
from aios.services.task.planner import TaskPlanner
from aios.services.task.progress import ProgressTracker


def test_task_models():
    step = TaskStep("review repository")
    assert step.command == "review repository"
    assert step.status == "pending"

    task = Task("Review repository and generate release notes", steps=[step])
    assert task.objective == "Review repository and generate release notes"
    assert len(task.steps) == 1

    d = task.to_dict()
    assert d["objective"] == task.objective

    loaded = Task.from_dict(d)
    assert loaded.id == task.id
    assert len(loaded.steps) == 1
    assert loaded.steps[0].command == "review repository"


def test_task_planning():
    registry = CommandRegistry()
    registry.register_command(
        CommandMetadata("review repository", "desc", CommandCategory.DEVELOPER, "None", [], "use"),
        lambda args: None,
    )
    registry.register_command(
        CommandMetadata("review git changes", "desc", CommandCategory.DEVELOPER, "None", [], "use"),
        lambda args: None,
    )
    registry.register_command(
        CommandMetadata(
            "generate release notes", "desc", CommandCategory.DEVELOPER, "None", [], "use"
        ),
        lambda args: None,
    )

    planner = TaskPlanner(registry)
    steps = planner.plan("Review my repository and generate release notes")
    assert len(steps) == 3
    assert steps[0].command == "review repository"
    assert steps[1].command == "review git changes"
    assert steps[2].command == "generate release notes"


def test_task_execution_success():
    registry = CommandRegistry()
    called = []

    def handler1(args):
        called.append("h1")
        print("output of command 1")

    registry.register_command(
        CommandMetadata("review repository", "desc", CommandCategory.DEVELOPER, "None", [], "use"),
        handler1,
    )

    progress = ProgressTracker()
    executor = TaskExecutor(registry, progress)

    task = Task("Review repository", steps=[TaskStep("review repository")])
    executor.execute_task(task)

    assert task.status == "completed"
    assert called == ["h1"]
    assert "output of command 1" in task.steps[0].output
    assert task.steps[0].status == "completed"


def test_task_execution_failure():
    registry = CommandRegistry()

    def handler_fail(args):
        raise ValueError("simulated error")

    registry.register_command(
        CommandMetadata("review repository", "desc", CommandCategory.DEVELOPER, "None", [], "use"),
        handler_fail,
    )
    registry.register_command(
        CommandMetadata("review git changes", "desc", CommandCategory.DEVELOPER, "None", [], "use"),
        lambda args: None,
    )

    progress = ProgressTracker()
    executor = TaskExecutor(registry, progress)

    task1 = Task(
        "Review repository and changes",
        steps=[TaskStep("review repository"), TaskStep("review git changes")],
    )
    executor.execute_task(task1)

    assert task1.status == "failed"
    assert task1.steps[0].status == "failed"
    assert "simulated error" in task1.steps[0].output
    assert task1.steps[1].status == "pending"

    task2 = Task(
        "Review repository and changes",
        steps=[TaskStep("review repository", optional=True), TaskStep("review git changes")],
    )
    executor.execute_task(task2)

    assert task2.status == "completed"
    assert task2.steps[0].status == "failed"
    assert task2.steps[1].status == "completed"


def test_task_history_persistence():
    with tempfile.TemporaryDirectory() as tmpdir:
        history = TaskHistory(Path(tmpdir))

        task = Task("Review repository", steps=[TaskStep("review repository")])
        history.save_task(task)

        loaded = history.load_task(task.id)
        assert loaded is not None
        assert loaded.id == task.id
        assert loaded.objective == "Review repository"

        tasks = history.list_tasks()
        assert len(tasks) == 1
        assert tasks[0].id == task.id

        history.delete_task(task.id)
        assert len(history.list_tasks()) == 0
