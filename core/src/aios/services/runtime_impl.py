import logging
import time
from typing import Any, Callable, Dict, List, Optional

from aios.services.runtime import (
    BackgroundTask,
    EventDispatcher,
    HealthMonitor,
    RuntimeConfiguration,
    RuntimeService,
    RuntimeSession,
    RuntimeState,
    Watcher,
)

logger = logging.getLogger(__name__)


class LocalEventDispatcher(EventDispatcher):
    def __init__(self) -> None:
        self._listeners: Dict[str, List[Callable[[Dict[str, Any]], None]]] = {}

    def dispatch(self, event_name: str, payload: Dict[str, Any]) -> None:
        logger.info(f"Dispatching event '{event_name}' with payload: {payload}")
        if event_name in self._listeners:
            for callback in self._listeners[event_name]:
                try:
                    callback(payload)
                except Exception as e:
                    logger.error(f"Listener error on '{event_name}': {e}")

    def subscribe(self, event_name: str, callback: Callable[[Dict[str, Any]], None]) -> None:
        self._listeners.setdefault(event_name, []).append(callback)


class LocalHealthMonitor(HealthMonitor):
    def __init__(self, runtime) -> None:
        self._runtime = runtime

    def check_health(self) -> Dict[str, Any]:
        kernel = self._runtime._kernel
        if not kernel:
            return {"status": "HALTED", "uptime": 0.0, "services": {}}
        services_status = {}
        for service_type in kernel.registry._services.keys():
            name = service_type.__name__
            services_status[name] = "READY"

        return {"status": "HEALTHY", "uptime": kernel.uptime, "services": services_status}


class BackgroundTaskManager:
    def __init__(self) -> None:
        self._tasks: List[BackgroundTask] = []

    def submit(self, task: BackgroundTask) -> None:
        task.next_run = time.time()
        self._tasks.append(task)

    def tick(self) -> None:
        now = time.time()
        for task in self._tasks:
            if task.status in ("pending", "completed") and now >= task.next_run:
                task.status = "running"
                try:
                    task.func()
                    task.status = "completed"
                    if task.interval > 0.0:
                        task.next_run = now + task.interval
                    else:
                        task.status = "completed"
                except Exception:
                    task.retries += 1
                    if task.retries < task.max_retries:
                        task.status = "pending"
                        task.next_run = now + 1.0  # Retry delay
                    else:
                        task.status = "failed"


class WatcherManager:
    def __init__(self) -> None:
        self._watchers: List[Watcher] = []

    def register(self, watcher: Watcher) -> None:
        watcher.start()
        self._watchers.append(watcher)

    def stop_all(self) -> None:
        for w in self._watchers:
            w.stop()


class NotificationManager:
    def __init__(self, dispatcher: EventDispatcher) -> None:
        self._dispatcher = dispatcher

    def notify(self, message: str) -> None:
        self._dispatcher.dispatch(
            "NotificationCreated", {"message": message, "timestamp": time.time()}
        )


# Concrete System Watchers
class BaseSystemWatcher(Watcher):
    def __init__(self, name: str) -> None:
        self._name = name
        self.active = False

    def start(self) -> None:
        self.active = True

    def stop(self) -> None:
        self.active = False

    @property
    def name(self) -> str:
        return self._name


class WorkspaceWatcher(BaseSystemWatcher):
    def __init__(self) -> None:
        super().__init__("WorkspaceWatcher")


class GitWatcher(BaseSystemWatcher):
    def __init__(self) -> None:
        super().__init__("GitWatcher")


class MissionWatcher(BaseSystemWatcher):
    def __init__(self) -> None:
        super().__init__("MissionWatcher")


class WorkflowWatcher(BaseSystemWatcher):
    def __init__(self) -> None:
        super().__init__("WorkflowWatcher")


class ProviderWatcher(BaseSystemWatcher):
    def __init__(self) -> None:
        super().__init__("ProviderWatcher")


class MemoryWatcher(BaseSystemWatcher):
    def __init__(self) -> None:
        super().__init__("MemoryWatcher")


class LocalRuntime(RuntimeService):
    def __init__(self, kernel=None) -> None:
        self._kernel = kernel
        self._state = RuntimeState.HALTED
        self._config = RuntimeConfiguration()
        self._session: Optional[RuntimeSession] = None

        self.dispatcher = LocalEventDispatcher()
        self.health_monitor = LocalHealthMonitor(self)
        self.task_manager = BackgroundTaskManager()
        self.watcher_manager = WatcherManager()
        self.notification_manager = NotificationManager(self.dispatcher)

    @property
    def state(self) -> RuntimeState:
        return self._state

    def initialize(self) -> None:
        self._ticking_thread = None
        self._ticking = False

    def start(self) -> None:
        self._state = RuntimeState.BOOTING
        logger.info("Starting AI OS Runtime...")

        # Build Session
        self._session = RuntimeSession(
            session_id=f"session_{int(time.time())}", workspace_root=".", created_at=time.time()
        )

        # Register default watchers
        self.register_watcher(WorkspaceWatcher())
        self.register_watcher(GitWatcher())
        self.register_watcher(MissionWatcher())
        self.register_watcher(WorkflowWatcher())
        self.register_watcher(ProviderWatcher())
        self.register_watcher(MemoryWatcher())

        # Start background ticking thread
        import threading

        self._ticking = True

        def tick_loop():
            while self._ticking:
                try:
                    self.task_manager.tick()
                except Exception as exc:
                    logger.error("Error in background task tick: %s", exc)
                time.sleep(1.0)

        self._ticking_thread = threading.Thread(target=tick_loop, daemon=True)
        self._ticking_thread.start()

        self._state = RuntimeState.READY
        logger.info("AI OS Runtime READY.")

    def stop(self) -> None:
        self._state = RuntimeState.SHUTTING_DOWN
        logger.info("Shutting down AI OS Runtime...")

        # Stop ticking loop
        self._ticking = False
        if self._ticking_thread:
            self._ticking_thread.join(timeout=2.0)

        # Stop watchers
        self.watcher_manager.stop_all()

        self._state = RuntimeState.HALTED
        logger.info("AI OS Runtime HALTED.")

    def register_watcher(self, watcher: Watcher) -> None:
        self.watcher_manager.register(watcher)

    def submit_task(self, task: BackgroundTask) -> None:
        self.task_manager.submit(task)

    def get_session(self) -> Optional[RuntimeSession]:
        return self._session
