from aios.services.task.models import Task, TaskStep


class ProgressTracker:
    def __init__(self) -> None:
        pass

    def start_task(self, task: Task) -> None:
        print(f"\nStarting Task: {task.title}")
        print(f"Objective: {task.objective}")
        print("-" * 40)
        self.print_progress(task)

    def start_step(self, idx: int, step: TaskStep) -> None:
        pass

    def complete_step(self, idx: int, step: TaskStep) -> None:
        self._print_step_result(idx, step, "✓")

    def fail_step(self, idx: int, step: TaskStep) -> None:
        self._print_step_result(idx, step, "✗")

    def _print_step_result(self, idx: int, step: TaskStep, marker: str) -> None:
        total = idx + 1
        print(f"[{total}] {step.command} {marker}")
        if step.output:
            lines = step.output.strip().split("\n")
            preview = "\n".join([f"    | {line}" for line in lines[:5]])
            print(preview)
            if len(lines) > 5:
                print(f"    | ... ({len(lines) - 5} more lines)")
            print()

    def print_progress(self, task: Task) -> None:
        for idx, step in enumerate(task.steps, 1):
            marker = "..."
            if step.status == "completed":
                marker = "✓"
            elif step.status == "failed":
                marker = "✗"
            print(f"[{idx}/{len(task.steps)}] {step.command} {marker}")
        print()
