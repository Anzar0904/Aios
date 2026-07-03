from typing import Callable, Optional, Type, TypeVar

from aios.services.agent import Agent, AgentResult, AgentRuntimeService
from aios.services.context import ContextService, WorkspaceContext
from aios.services.event_bus import Event, EventBusService
from aios.services.intent import Intent, IntentResolverService, IntentType
from aios.services.memory import Memory, MemoryMetadata, MemoryService, MemoryType
from aios.services.model import ModelService
from aios.services.session import Session, SessionService
from aios.services.tool import Tool, ToolMetadata, ToolResult, ToolService

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

    def add_memory(
        self,
        content: str,
        memory_type: MemoryType,
        tags: list[str] = None,
        importance: int = 1,
        metadata_additional: dict = None,
    ) -> Memory:
        if metadata_additional is None:
            metadata_additional = {}
        if tags is None:
            tags = []
        return Memory(
            memory_id="stub-memory",
            content=content,
            memory_type=memory_type,
            metadata=MemoryMetadata(
                workspace_id="stub-workspace",
                session_id="stub-session",
                tags=tags,
                importance=importance,
                additional=metadata_additional,
            ),
            created_at=0.0,
            updated_at=0.0,
        )

    def update_memory(
        self,
        memory_id: str,
        content: Optional[str] = None,
        tags: Optional[list[str]] = None,
        importance: Optional[int] = None,
        metadata_additional: Optional[dict] = None,
    ) -> Memory:
        return Memory(
            memory_id=memory_id,
            content=content or "stub-content",
            memory_type=MemoryType.NOTE,
            metadata=MemoryMetadata(
                workspace_id="stub-workspace",
                session_id="stub-session",
                tags=tags or [],
                importance=importance or 1,
                additional=metadata_additional or {},
            ),
            created_at=0.0,
            updated_at=0.0,
        )

    def delete_memory(self, memory_id: str) -> None:
        pass

    def search_memory(
        self,
        query: str,
        memory_type: Optional[MemoryType] = None,
        tags: Optional[list[str]] = None,
    ) -> list[Memory]:
        return []

    def get_memory(self, memory_id: str) -> Optional[Memory]:
        return None

    def load_workspace_memory(self, workspace_id: str) -> list[Memory]:
        return []

    def commit(self) -> None:
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
    def __init__(self) -> None:
        self._session: Optional[Session] = None

    def initialize(self) -> None:
        pass

    def on_ready(self) -> None:
        pass

    def on_active(self) -> None:
        pass

    def teardown(self) -> None:
        pass

    def start_session(self, workspace_path: str, session_id: Optional[str] = None) -> Session:
        self._session = Session(
            session_id=session_id if session_id is not None else "stub-session",
            workspace_id=workspace_path,
            start_time=0.0,
            runtime_state="active",
        )
        return self._session

    def end_session(self) -> None:
        if self._session is not None:
            self._session.runtime_state = "ended"
            self._session.end_time = 0.0
        self._session = None

    def get_current_session(self) -> Optional[Session]:
        return self._session

    def create_session(self, workspace_path: str) -> str:
        session = self.start_session(workspace_path)
        return session.session_id

    def save_session(self, session_id: str) -> None:
        pass

    def get_active_session_id(self) -> Optional[str]:
        if self._session is not None:
            return self._session.session_id
        return None


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

    def register_tool(self, tool: Tool) -> None:
        pass

    def unregister_tool(self, name: str) -> None:
        pass

    def list_tools(self) -> list[ToolMetadata]:
        return []

    def execute_tool(self, name: str, arguments: dict) -> ToolResult:
        return ToolResult(success=True, output="stub-execution")

    def validate_tool(self, name: str, arguments: dict) -> bool:
        return True

    def invoke_tool(self, name: str, arguments: dict) -> dict:
        return {"output": "stub-execution"}


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


class StubIntentResolverService(IntentResolverService):
    def initialize(self) -> None:
        pass

    def on_ready(self) -> None:
        pass

    def on_active(self) -> None:
        pass

    def teardown(self) -> None:
        pass

    def resolve(self, text: str) -> Intent:
        return Intent(
            intent_type=IntentType.UNKNOWN,
            target_service="None",
            action="Unknown",
            parameters={},
            confidence=0.0,
        )

    def validate(self, intent: Intent) -> bool:
        return False

    def classify(self, text: str) -> IntentType:
        return IntentType.UNKNOWN


class StubAgentRuntimeService(AgentRuntimeService):
    def initialize(self) -> None:
        pass

    def on_ready(self) -> None:
        pass

    def on_active(self) -> None:
        pass

    def teardown(self) -> None:
        pass

    def register_agent(self, agent: Agent) -> None:
        pass

    def unregister_agent(self, name: str) -> None:
        pass

    def execute(self, intent: Intent) -> AgentResult:
        return AgentResult(success=True, response="stub-agent-response")

    def interrupt(self) -> None:
        pass

    def cancel(self) -> None:
        pass
