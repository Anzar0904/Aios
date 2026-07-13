import contextlib
import io
import time
from typing import Any

from aios.services.command import match_command
from aios.services.task.models import Task, TaskStep
from aios.services.task.progress import ProgressTracker


class TaskExecutor:
    def __init__(self, registry: Any, progress_tracker: ProgressTracker) -> None:
        self.registry = registry
        self.progress_tracker = progress_tracker

    def execute_step(self, step: TaskStep) -> bool:
        matched = match_command(step.command, self.registry)
        if not matched:
            step.status = "failed"
            step.output = f"Command '{step.command}' not found in registry."
            return False

        cmd_metadata, args = matched
        handler = self.registry.get_handler(cmd_metadata.name)
        if not handler:
            step.status = "failed"
            step.output = f"No handler registered for command '{cmd_metadata.name}'."
            return False

        f = io.StringIO()
        step.status = "running"
        try:
            with contextlib.redirect_stdout(f):
                handler(args)
            step.status = "completed"
            step.output = f.getvalue()
            return True
        except Exception as e:
            step.status = "failed"
            step.output = f.getvalue() + f"\nExecution failed with error: {e}"
            return False

    def execute_task(self, task: Task) -> None:
        task.status = "running"
        task.updated_at = time.time()
        self.progress_tracker.start_task(task)

        for idx, step in enumerate(task.steps):
            self.progress_tracker.start_step(idx, step)
            success = self.execute_step(step)
            task.updated_at = time.time()
            if success:
                self.progress_tracker.complete_step(idx, step)
            else:
                self.progress_tracker.fail_step(idx, step)
                if not step.optional:
                    task.status = "failed"
                    task.execution_log.append(f"Task failed at step: {step.command}")
                    break
        else:
            task.status = "completed"
            task.execution_log.append("Task completed successfully.")
            task.updated_at = time.time()
