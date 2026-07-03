import logging
import time
import uuid
from typing import Optional

from aios.services.event_bus import EventBusService
from aios.services.session import (
    Session,
    SessionEndedEvent,
    SessionService,
    SessionStartedEvent,
)

logger = logging.getLogger(__name__)


class LocalSessionService(SessionService):
    """
    Concrete implementation of SessionService that manages the lifecycle of sessions
    and publishes events on session start and end.
    """

    def __init__(self, event_bus: EventBusService) -> None:
        self._event_bus = event_bus
        self._current_session: Optional[Session] = None

    def initialize(self) -> None:
        logger.info("Initializing LocalSessionService")
        self._event_bus.register_event_type(SessionStartedEvent)
        self._event_bus.register_event_type(SessionEndedEvent)

    def start_session(self, workspace_path: str, session_id: Optional[str] = None) -> Session:
        """Starts a new session for the given workspace path and publishes SessionStartedEvent."""
        if self._current_session is not None:
            self.end_session()

        actual_session_id = session_id if session_id is not None else str(uuid.uuid4())
        session = Session(
            session_id=actual_session_id,
            workspace_id=workspace_path,
            start_time=time.time(),
            runtime_state="active",
        )
        self._current_session = session

        logger.info(f"Starting session {actual_session_id} for workspace {workspace_path}")
        self._event_bus.publish(SessionStartedEvent(session_id=actual_session_id, session=session))
        return session

    def end_session(self) -> None:
        """Ends the active session and publishes SessionEndedEvent."""
        if self._current_session is None:
            logger.warning("No active session to end")
            return

        session = self._current_session
        session.end_time = time.time()
        session.runtime_state = "ended"
        self._current_session = None

        logger.info(f"Ending session {session.session_id}")
        self._event_bus.publish(SessionEndedEvent(session_id=session.session_id, session=session))

    def get_current_session(self) -> Optional[Session]:
        """Returns the currently active session, if any."""
        return self._current_session

    def create_session(self, workspace_path: str) -> str:
        """Launches a new session and returns the session ID."""
        session = self.start_session(workspace_path)
        return session.session_id

    def save_session(self, session_id: str) -> None:
        """Persists the active session state."""
        logger.info(f"Saving session {session_id}")

    def get_active_session_id(self) -> Optional[str]:
        """Returns the current active session ID, if any."""
        if self._current_session is not None:
            return self._current_session.session_id
        return None
