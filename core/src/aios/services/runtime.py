import abc
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Any, Optional, Callable
from aios.services.base import ServiceLifecycle



class RuntimeState(Enum):
    HALTED = auto()
    BOOTING = auto()
    READY = auto()
    SHUTTING_DOWN = auto()


@dataclass
class RuntimeSession:
    session_id: str
    workspace_root: str
    created_at: float


@dataclass
class RuntimeConfiguration:
    debug: bool = True
    max_background_tasks: int = 10
    config_path: str = ""


@dataclass
class BackgroundTask:
    task_id: str
    name: str
    func: Callable[[], Any]
    interval: float = 0.0  # 0 means one-shot
    next_run: float = 0.0
    status: str = "pending"  # pending, running, completed, failed
    retries: int = 0
    max_retries: int = 3


class Watcher(abc.ABC):
    @abc.abstractmethod
    def start(self) -> None:
        """Starts monitoring the target resource."""
        pass

    @abc.abstractmethod
    def stop(self) -> None:
        """Stops monitoring the target resource."""
        pass

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Returns the name of the watcher."""
        pass


class EventDispatcher(abc.ABC):
    @abc.abstractmethod
    def dispatch(self, event_name: str, payload: Dict[str, Any]) -> None:
        """Publishes strongly typed runtime events to listeners."""
        pass

    @abc.abstractmethod
    def subscribe(self, event_name: str, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Subscribes a callback listener to specific event types."""
        pass


class HealthMonitor(abc.ABC):
    @abc.abstractmethod
    def check_health(self) -> Dict[str, Any]:
        """Audits status checks across all registered core services."""
        pass


class RuntimeService(ServiceLifecycle, abc.ABC):
    @property
    @abc.abstractmethod
    def state(self) -> RuntimeState:
        """Returns the active state of the runtime engine."""
        pass

    @abc.abstractmethod
    def start(self) -> None:
        """Executes startup sequence, loading configurations and loading services."""
        pass

    @abc.abstractmethod
    def stop(self) -> None:
        """Gracefully shuts down running watchers and background threads."""
        pass

    @abc.abstractmethod
    def register_watcher(self, watcher: Watcher) -> None:
        """Adds and starts a system watcher."""
        pass

    @abc.abstractmethod
    def submit_task(self, task: BackgroundTask) -> None:
        """Submits a delayed or recurring task to the background pool."""
        pass

    @abc.abstractmethod
    def get_session(self) -> Optional[RuntimeSession]:
        """Returns the current active session."""
        pass
