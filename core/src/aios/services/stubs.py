from typing import Callable, Type, TypeVar

from aios.services.context import ContextService, WorkspaceContext
from aios.services.event_bus import Event, EventBusService
from aios.services.memory import MemoryService
from aios.services.model import ModelService
from aios.services.session import SessionService
from aios.services.tool import ToolService

E = TypeVar("E", bound=Event)


class StubContextService(ContextService):
    def initialize(self) -> None:
        pass

    def on_ready(self) -> None:
        pass

    def on_active(self) -> None:
        pass

    def teardown(self) -> None:
        pass

    def detect_context(self) -> WorkspaceContext:
        return WorkspaceContext(
            working_directory="",
            git_repo_path=None,
            git_branch=None,
            project_root="",
            project_name="",
        )

    def get_current_context(self) -> WorkspaceContext | None:
        return None


class StubMemoryService(MemoryService):
    def initialize(self) -> None:
        pass

    def on_ready(self) -> None:
        pass

    def on_active(self) -> None:
        pass

    def teardown(self) -> None:
        pass

    def restore_memory(self, context: dict) -> None:
        pass

    def observe_event(self, event: dict) -> None:
        pass

    def commit_memory(self) -> None:
        pass

    def prune_memory(self) -> None:
        pass


class StubSessionService(SessionService):
    def initialize(self) -> None:
        pass

    def on_ready(self) -> None:
        pass

    def on_active(self) -> None:
        pass

    def teardown(self) -> None:
        pass

    def create_session(self, workspace_path: str) -> str:
        return "stub-session"

    def save_session(self, session_id: str) -> None:
        pass

    def get_active_session_id(self) -> str | None:
        return "stub-session"


class StubModelService(ModelService):
    def initialize(self) -> None:
        pass

    def on_ready(self) -> None:
        pass

    def on_active(self) -> None:
        pass

    def teardown(self) -> None:
        pass

    def execute_prompt(self, prompt: str, system_instruction: str | None = None) -> str:
        return "stub-response"


class StubToolService(ToolService):
    def initialize(self) -> None:
        pass

    def on_ready(self) -> None:
        pass

    def on_active(self) -> None:
        pass

    def teardown(self) -> None:
        pass

    def register_tool(self, name: str, contract: dict) -> None:
        pass

    def invoke_tool(self, name: str, arguments: dict) -> dict:
        return {}


class StubEventBusService(EventBusService):
    def initialize(self) -> None:
        pass

    def on_ready(self) -> None:
        pass

    def on_active(self) -> None:
        pass

    def teardown(self) -> None:
        pass

    def register_event_type(self, event_type: Type[Event]) -> None:
        pass

    def subscribe(self, event_type: Type[E], handler: Callable[[E], None]) -> None:
        pass

    def unsubscribe(self, event_type: Type[E], handler: Callable[[E], None]) -> None:
        pass

    def publish(self, event: Event) -> None:
        pass
