import abc
from dataclasses import dataclass
from typing import Optional

from aios.services.base import ServiceLifecycle
from aios.services.event_bus import Event


@dataclass
class Session:
    """Strongly typed representation of a user session."""

    session_id: str
    workspace_id: str
    start_time: float
    end_time: Optional[float] = None
    runtime_state: str = "active"


@dataclass(frozen=True, kw_only=True)
class SessionStartedEvent(Event):
    """Published immediately after a session is successfully started."""

    session_id: str
    session: Session


@dataclass(frozen=True, kw_only=True)
class SessionEndedEvent(Event):
    """Published immediately after a session is successfully ended."""

    session_id: str
    session: Session


class SessionService(ServiceLifecycle, abc.ABC):
    """Interface for managing the lifecycle and persistence of interactive sessions."""

    @abc.abstractmethod
    def start_session(self, workspace_path: str, session_id: Optional[str] = None) -> Session:
        """Starts a new session for the given workspace path and publishes SessionStartedEvent."""
        pass

    @abc.abstractmethod
    def end_session(self) -> None:
        """Ends the active session and publishes SessionEndedEvent."""
        pass

    @abc.abstractmethod
    def get_current_session(self) -> Optional[Session]:
        """Returns the currently active session, if any."""
        pass

    @abc.abstractmethod
    def create_session(self, workspace_path: str) -> str:
        """Launches a new session and returns the session ID."""
        pass

    @abc.abstractmethod
    def save_session(self, session_id: str) -> None:
        """Persists the active session state."""
        pass

    @abc.abstractmethod
    def get_active_session_id(self) -> Optional[str]:
        """Returns the current active session ID, if any."""
        pass
