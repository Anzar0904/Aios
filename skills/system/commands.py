from pathlib import Path

from aios.services.command.discovery import (
    execute_system_status,
    handle_action_approve,
    handle_action_execute,
    handle_action_history,
    handle_action_plan,
    handle_action_reject,
    handle_action_rollback,
    handle_run_task,
    handle_task_history,
    handle_task_resume,
    handle_task_status,
)
from aios.services.command.metadata import CommandCategory, CommandMetadata


def register_commands(registry, kernel, conv_manager) -> None:
    # Determine workspace root
    workspace_root = "."
    if kernel:
        try:
            from aios.services.context import ContextService
            ctx_svc = kernel.registry.get(ContextService)
            ctx = ctx_svc.get_current_context()
            if ctx:
                workspace_root = ctx.project_root
        except Exception:
            pass

    from aios.services.task import ProgressTracker, TaskHistory
    task_store_dir = Path(workspace_root) / ".aios_tasks"
    task_history = TaskHistory(task_store_dir)
    progress_tracker = ProgressTracker()

    from aios.services.action.history import ActionHistory
    action_store_dir = Path(workspace_root) / ".aios_actions"
    action_history = ActionHistory(action_store_dir)

    registry.register_command(
        CommandMetadata(
            name="system status",
            description="Displays current kernel state and OS uptime.",
            category=CommandCategory.SYSTEM,
            required_agent="None",
            required_tools=[],
            example_usage="system status",
        ),
        lambda args: execute_system_status(kernel),
    )

    registry.register_command(
        CommandMetadata(
            name="run task",
            description=(
                "Executes a multi-step engineering objective by planning and "
                "orchestrating commands."
            ),
            category=CommandCategory.AUTOMATION,
            required_agent="None",
            required_tools=[],
            example_usage="run task Review my repository and generate release notes",
        ),
        lambda args: handle_run_task(
            registry, kernel, task_history, progress_tracker, args
        ),
    )

    registry.register_command(
        CommandMetadata(
            name="task status",
            description="Displays the status of the last executed task.",
            category=CommandCategory.AUTOMATION,
            required_agent="None",
            required_tools=[],
            example_usage="task status",
        ),
        lambda args: handle_task_status(task_history),
    )

    registry.register_command(
        CommandMetadata(
            name="task history",
            description="Lists all persisted task executions.",
            category=CommandCategory.AUTOMATION,
            required_agent="None",
            required_tools=[],
            example_usage="task history",
        ),
        lambda args: handle_task_history(task_history),
    )

    registry.register_command(
        CommandMetadata(
            name="task resume",
            description="Resumes the execution of a pending or failed task by ID.",
            category=CommandCategory.AUTOMATION,
            required_agent="None",
            required_tools=[],
            example_usage="task resume <task_id>",
        ),
        lambda args: handle_task_resume(
            registry, kernel, task_history, progress_tracker, args
        ),
    )

    registry.register_command(
        CommandMetadata(
            name="plan",
            description="Generates an execution plan for a multi-step action objective.",
            category=CommandCategory.AUTOMATION,
            required_agent="None",
            required_tools=[],
            example_usage="plan write file test.txt content Hello",
        ),
        lambda args: handle_action_plan(kernel, action_history, args),
    )

    registry.register_command(
        CommandMetadata(
            name="approve",
            description="Approves the currently active action execution plan.",
            category=CommandCategory.AUTOMATION,
            required_agent="None",
            required_tools=[],
            example_usage="approve",
        ),
        lambda args: handle_action_approve(action_history),
    )

    registry.register_command(
        CommandMetadata(
            name="reject",
            description="Rejects and clears the currently active action execution plan.",
            category=CommandCategory.AUTOMATION,
            required_agent="None",
            required_tools=[],
            example_usage="reject",
        ),
        lambda args: handle_action_reject(action_history),
    )

    registry.register_command(
        CommandMetadata(
            name="execute",
            description="Executes the approved steps in the active action execution plan.",
            category=CommandCategory.AUTOMATION,
            required_agent="None",
            required_tools=[],
            example_usage="execute",
        ),
        lambda args: handle_action_execute(kernel, action_history),
    )

    registry.register_command(
        CommandMetadata(
            name="rollback",
            description="Rolls back/reverts executed changes of a plan by ID.",
            category=CommandCategory.AUTOMATION,
            required_agent="None",
            required_tools=[],
            example_usage="rollback <plan_id>",
        ),
        lambda args: handle_action_rollback(kernel, action_history, args),
    )

    registry.register_command(
        CommandMetadata(
            name="execution history",
            description="Lists all persisted action execution plans.",
            category=CommandCategory.AUTOMATION,
            required_agent="None",
            required_tools=[],
            example_usage="execution history",
        ),
        lambda args: handle_action_history(action_history),
    )
