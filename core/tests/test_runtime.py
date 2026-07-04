import time
from unittest.mock import MagicMock

from aios.services.runtime import RuntimeState, BackgroundTask, Watcher
from aios.services.runtime_impl import (
    LocalEventDispatcher,
    LocalHealthMonitor,
    LocalRuntime,
    WorkspaceWatcher,
    GitWatcher,
)


class MockSystemWatcher(Watcher):
    def __init__(self, name: str) -> None:
        self._name = name
        self.started = False

    def start(self) -> None:
        self.started = True

    def stop(self) -> None:
        self.started = False

    @property
    def name(self) -> str:
        return self._name


def test_runtime_startup_and_shutdown():
    kernel = MagicMock()
    runtime = LocalRuntime(kernel)
    assert runtime.state == RuntimeState.HALTED

    # Startup
    runtime.start()
    assert runtime.state == RuntimeState.READY
    assert runtime.get_session() is not None
    assert runtime.get_session().workspace_root == "."

    # Check registered default watchers are started
    for w in runtime.watcher_manager._watchers:
        assert w.active is True

    # Shutdown
    runtime.stop()
    assert runtime.state == RuntimeState.HALTED
    for w in runtime.watcher_manager._watchers:
        assert w.active is False


def test_event_propagation():
    dispatcher = LocalEventDispatcher()
    
    received_payload = {}
    def callback(payload):
        nonlocal received_payload
        received_payload = payload

    dispatcher.subscribe("GitChanged", callback)
    
    payload = {"branch": "feature-ats", "changed_files": 2}
    dispatcher.dispatch("GitChanged", payload)
    
    assert received_payload == payload


def test_background_task_scheduling():
    kernel = MagicMock()
    runtime = LocalRuntime(kernel)
    
    task_run_count = 0
    def dummy_func():
        nonlocal task_run_count
        task_run_count += 1

    task = BackgroundTask(
        task_id="task-1",
        name="Study Alert Cron",
        func=dummy_func,
        interval=0.5
    )

    runtime.submit_task(task)
    assert task.status == "pending"

    # Tick 1: runs task immediately
    runtime.task_manager.tick()
    assert task_run_count == 1
    assert task.status == "completed"

    # Tick 2: doesn't run yet because interval has not expired
    runtime.task_manager.tick()
    assert task_run_count == 1

    # Simulate time progression for interval
    task.next_run = time.time() - 1.0
    runtime.task_manager.tick()
    assert task_run_count == 2
    assert task.status == "completed"


def test_health_monitor():
    kernel = MagicMock()
    kernel.uptime = 120.0
    kernel.registry._services = {
        RuntimeState: MagicMock(),
        LocalEventDispatcher: MagicMock()
    }

    runtime = MagicMock()
    runtime._kernel = kernel

    monitor = LocalHealthMonitor(runtime)
    report = monitor.check_health()

    assert report["status"] == "HEALTHY"
    assert report["uptime"] == 120.0
    assert "RuntimeState" in report["services"]
    assert "LocalEventDispatcher" in report["services"]
