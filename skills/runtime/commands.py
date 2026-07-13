import time

from aios.services.command.metadata import CommandCategory, CommandMetadata
from aios.services.runtime import RuntimeService


def execute_runtime_start(args: str, kernel, conv_manager) -> None:
    try:
        runtime = kernel.registry.get(RuntimeService)
        runtime.start()
        print("AI OS Runtime started successfully.")
    except Exception as e:
        print(f"Failed to start runtime: {str(e)}")


def execute_runtime_stop(args: str, kernel, conv_manager) -> None:
    try:
        runtime = kernel.registry.get(RuntimeService)
        runtime.stop()
        print("AI OS Runtime stopped successfully.")
    except Exception as e:
        print(f"Failed to stop runtime: {str(e)}")


def execute_runtime_restart(args: str, kernel, conv_manager) -> None:
    try:
        runtime = kernel.registry.get(RuntimeService)
        runtime.stop()
        runtime.start()
        print("AI OS Runtime restarted successfully.")
    except Exception as e:
        print(f"Failed to restart runtime: {str(e)}")


def execute_runtime_status(args: str, kernel, conv_manager) -> None:
    try:
        runtime = kernel.registry.get(RuntimeService)
        session = runtime.get_session()
        print(f"\n=== Runtime Status: {runtime.state.name} ===")
        if session:
            print(f" - Session ID: {session.session_id}")
            print(f" - Workspace Root: {session.workspace_root}")
            print(f" - Created At: {time.ctime(session.created_at)}")
        else:
            print(" - Active Session: None")
    except Exception as e:
        print(f"Failed to get status: {str(e)}")


def execute_runtime_health(args: str, kernel, conv_manager) -> None:
    try:
        runtime = kernel.registry.get(RuntimeService)
        report = runtime.health_monitor.check_health()
        print(f"\n=== System Health Check: {report['status']} ===")
        print(f" - Uptime: {report['uptime']:.2f} seconds")
        print(" - Core Services Status Check:")
        for svc_name, svc_status in report["services"].items():
            print(f"   * {svc_name}: {svc_status}")
    except Exception as e:
        print(f"Failed health check: {str(e)}")


def execute_runtime_events(args: str, kernel, conv_manager) -> None:
    try:
        runtime = kernel.registry.get(RuntimeService)
        print("\n=== Event Subscriptions & Listeners ===")
        for ev, listn in runtime.dispatcher._listeners.items():
            print(f" - {ev}: {len(listn)} callback(s) registered.")
    except Exception as e:
        print(f"Failed: {str(e)}")


def execute_runtime_watchers(args: str, kernel, conv_manager) -> None:
    try:
        runtime = kernel.registry.get(RuntimeService)
        print("\n=== Active Watchers ===")
        for w in runtime.watcher_manager._watchers:
            status = "ACTIVE" if w.active else "STOPPED"
            print(f" - {w.name}: {status}")
    except Exception as e:
        print(f"Failed: {str(e)}")


def execute_runtime_tasks(args: str, kernel, conv_manager) -> None:
    try:
        runtime = kernel.registry.get(RuntimeService)
        print("\n=== Background Tasks Pool ===")
        if not runtime.task_manager._tasks:
            print(" No background tasks registered.")
            return
        for t in runtime.task_manager._tasks:
            print(
                f" - Task: {t.name} (ID: {t.task_id}) | Interval: {t.interval}s | Next run: {time.ctime(t.next_run)} | Status: {t.status}"
            )
    except Exception as e:
        print(f"Failed: {str(e)}")


def register_commands(registry, kernel, conv_manager) -> None:
    commands_map = {
        "runtime start": execute_runtime_start,
        "runtime stop": execute_runtime_stop,
        "runtime restart": execute_runtime_restart,
        "runtime status": execute_runtime_status,
        "runtime health": execute_runtime_health,
        "runtime events": execute_runtime_events,
        "runtime watchers": execute_runtime_watchers,
        "runtime tasks": execute_runtime_tasks,
    }

    for name, handler in commands_map.items():
        registry.register_command(
            CommandMetadata(
                name=name,
                description=f"Command to perform {name} action on system runtime.",
                category=CommandCategory.CLI,
                required_agent="None",
                required_tools=[],
                example_usage=f"{name} arguments",
            ),
            lambda args, h=handler: h(args, kernel, conv_manager),
        )
