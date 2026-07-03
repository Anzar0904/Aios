import abc

from aios.services.base import ServiceLifecycle


class SessionService(ServiceLifecycle, abc.ABC):
    """Interface for managing the lifecycle and persistence of interactive sessions."""

    @abc.abstractmethod
    def create_session(self, workspace_path: str) -> str:
        """Launches a new session and returns the session ID."""
        pass

    @abc.abstractmethod
    def save_session(self, session_id: str) -> None:
        """Persists the active session state."""
        pass

    @abc.abstractmethod
    def get_active_session_id(self) -> str | None:
        """Returns the current active session ID, if any."""
        pass
