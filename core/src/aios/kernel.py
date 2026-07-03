import sys
import time
from enum import Enum, auto
from pathlib import Path

from aios.config import OSConfig, load_config
from aios.registry import ServiceRegistry
from aios.services.agent import (
    AgentCompletedEvent,
    AgentFailedEvent,
    AgentRuntimeService,
    AgentStartedEvent,
)
from aios.services.agent_impl import LocalAgentRuntime
from aios.services.context import ContextLoadedEvent, ContextService
from aios.services.context_impl import LocalContextService
from aios.services.event_bus import EventBusService, KernelStartedEvent
from aios.services.event_bus_impl import LocalEventBus
from aios.services.intent import Intent, IntentResolverService, IntentResult, IntentType
from aios.services.intent_impl import LocalIntentResolver
from aios.services.memory import MemoryService
from aios.services.memory_impl import LocalMemoryService
from aios.services.model import ModelService
from aios.services.model_impl import LocalModelService
from aios.services.session import (
    SessionEndedEvent,
    SessionService,
    SessionStartedEvent,
)
from aios.services.session_impl import LocalSessionService

# Import stubs for bootstrap registration
from aios.services.tool import (
    ToolCompletedEvent,
    ToolFailedEvent,
    ToolService,
    ToolStartedEvent,
)
from aios.services.tool_impl import LocalToolManager


class RuntimeState(Enum):
    """Represents the operating state of the AI OS runtime lifecycle."""

    HALTED = auto()
    BOOTING = auto()
    READY = auto()
    BUSY = auto()
    SHUTTING_DOWN = auto()


class Kernel:
    """
    The orchestrator and runtime engine of the Personal AI OS.
    Owns configuration loading, service lifecycle transitions, and the service registry.
    Exposes only lifecycle and runtime state methods.
    """

    def __init__(self, config_path: Path) -> None:
        self.config_path = config_path
        self.config: OSConfig | None = None
        self.registry = ServiceRegistry()
        self._state = RuntimeState.HALTED
        self._boot_time: float | None = None
        self._active_session_id: str | None = None

    @property
    def state(self) -> RuntimeState:
        """Returns the current state of the runtime."""
        return self._state

    @property
    def active_session_id(self) -> str | None:
        """Returns the ID of the active session, if any."""
        return self._active_session_id

    @property
    def uptime(self) -> float:
        """Returns the uptime in seconds since the boot sequence started."""
        if self._boot_time is None:
            return 0.0
        return time.time() - self._boot_time

    def boot(self) -> None:
        """Executes the Kernel startup lifecycle sequence."""
        if self._state != RuntimeState.HALTED:
            raise RuntimeError(f"Cannot boot Kernel when current state is {self._state.name}")

        self._boot_time = time.time()
        self._state = RuntimeState.BOOTING

        try:
            print("Loading configuration...")
            self.config = load_config(self.config_path)

            print("Registering services...")
            self._register_core_services()

            print("Starting Kernel...")
            self._initialize_services()

            # Set up demonstration subscribers before workspace detection
            event_bus = self.registry.get(EventBusService)
            event_bus.register_event_type(KernelStartedEvent)

            def log_startup(event: KernelStartedEvent) -> None:
                print(f"[EventBus] Handled KernelStartedEvent for version: {event.version}")

            def log_context(event: ContextLoadedEvent) -> None:
                branch_str = (
                    f"branch: {event.context.git_branch}" if event.context.git_branch else "non-git"
                )
                print(
                    "[EventBus] Handled ContextLoadedEvent for project: "
                    f"{event.context.project_name} ({branch_str})"
                )

            def log_session_started(event: SessionStartedEvent) -> None:
                print(
                    "[EventBus] Handled SessionStartedEvent for session: "
                    f"{event.session_id} (workspace: {event.session.workspace_id})"
                )

            def log_session_ended(event: SessionEndedEvent) -> None:
                print(f"[EventBus] Handled SessionEndedEvent for session: {event.session_id}")

            def log_tool_started(event: ToolStartedEvent) -> None:
                print(f"[EventBus] Handled ToolStartedEvent for tool: {event.tool_name}")

            def log_tool_completed(event: ToolCompletedEvent) -> None:
                print(
                    f"[EventBus] Handled ToolCompletedEvent for tool: {event.tool_name} "
                    f"(Success: {event.result.success})"
                )

            def log_tool_failed(event: ToolFailedEvent) -> None:
                print(
                    f"[EventBus] Handled ToolFailedEvent for tool: {event.tool_name} "
                    f"(Error: {event.error})"
                )

            def log_agent_started(event: AgentStartedEvent) -> None:
                print(
                    f"[EventBus] Handled AgentStartedEvent for intent: "
                    f"{event.intent.intent_type.name}.{event.intent.action}"
                )

            def log_agent_completed(event: AgentCompletedEvent) -> None:
                print(f"[EventBus] Handled AgentCompletedEvent (Success: {event.result.success})")

            def log_agent_failed(event: AgentFailedEvent) -> None:
                print(f"[EventBus] Handled AgentFailedEvent (Error: {event.error})")

            event_bus.subscribe(KernelStartedEvent, log_startup)
            event_bus.subscribe(ContextLoadedEvent, log_context)
            event_bus.subscribe(SessionStartedEvent, log_session_started)
            event_bus.subscribe(SessionEndedEvent, log_session_ended)
            event_bus.subscribe(ToolStartedEvent, log_tool_started)
            event_bus.subscribe(ToolCompletedEvent, log_tool_completed)
            event_bus.subscribe(ToolFailedEvent, log_tool_failed)
            event_bus.subscribe(AgentStartedEvent, log_agent_started)
            event_bus.subscribe(AgentCompletedEvent, log_agent_completed)
            event_bus.subscribe(AgentFailedEvent, log_agent_failed)

            # Automatically detect workspace context
            context_service = self.registry.get(ContextService)
            context = context_service.detect_context()

            # Start a new session
            session_service = self.registry.get(SessionService)
            session = session_service.start_session(context.project_root)
            self._active_session_id = session.session_id

            self._transition_to_ready()

            self._state = RuntimeState.READY
        except Exception as e:
            self._state = RuntimeState.HALTED
            self._boot_time = None
            raise RuntimeError("Kernel boot sequence failed") from e

    def start_session(self, session_id: str) -> None:
        """Transitions the runtime state to associate with an active session."""
        if self._state != RuntimeState.READY:
            raise RuntimeError(f"Cannot start session when Kernel state is {self._state.name}")
        self._active_session_id = session_id

        # Sync with SessionService
        session_service = self.registry.get(SessionService)
        context_service = self.registry.get(ContextService)
        context = context_service.get_current_context()
        workspace_path = context.project_root if context else str(Path.cwd().resolve())

        curr = session_service.get_current_session()
        if curr is None or curr.session_id != session_id:
            session_service.start_session(workspace_path, session_id=session_id)

    def end_session(self) -> None:
        """Disassociates the active session from the runtime."""
        self._active_session_id = None

        # Sync with SessionService
        session_service = self.registry.get(SessionService)
        if session_service.get_current_session() is not None:
            session_service.end_session()

    def execute_intent(self, intent: Intent) -> IntentResult:
        """Executes a structured Intent by delegating to the Agent Runtime."""
        if not self.registry.get(IntentResolverService).validate(intent):
            return IntentResult(success=False, message="Invalid intent: validation failed.")

        try:
            # Kernel handles session lifecycle transitions directly
            if intent.intent_type == IntentType.SESSION and intent.action == "End":
                self.end_session()

            agent_runtime = self.registry.get(AgentRuntimeService)
            agent_res = agent_runtime.execute(intent)

            return IntentResult(
                success=agent_res.success,
                message=agent_res.response,
                data=agent_res.data,
            )

        except Exception as e:
            return IntentResult(success=False, message=f"Failed to execute intent: {str(e)}")

    def mark_busy(self, busy: bool) -> None:
        """Transitions the runtime state between READY and BUSY."""
        if self._state not in (RuntimeState.READY, RuntimeState.BUSY):
            raise RuntimeError(f"Cannot change busy status when Kernel state is {self._state.name}")
        self._state = RuntimeState.BUSY if busy else RuntimeState.READY

    def _register_core_services(self) -> None:
        """Instantiates and registers the core services."""
        event_bus = LocalEventBus()
        self.registry.register(EventBusService, event_bus)

        session_service = LocalSessionService(event_bus)
        context_service = LocalContextService(event_bus)
        memory_service = LocalMemoryService(event_bus)
        tool_service = LocalToolManager(event_bus)

        self.registry.register(SessionService, session_service)
        self.registry.register(ContextService, context_service)
        self.registry.register(MemoryService, memory_service)
        self.registry.register(IntentResolverService, LocalIntentResolver())
        model_service = LocalModelService()
        self.registry.register(ModelService, model_service)
        self.registry.register(ToolService, tool_service)
        self.registry.register(
            AgentRuntimeService,
            LocalAgentRuntime(
                event_bus, memory_service, context_service, tool_service, model_service
            ),
        )

    def _initialize_services(self) -> None:
        """Invokes the initialize stage on all registered services."""
        for service in self.registry.get_all():
            service.initialize()

    def _transition_to_ready(self) -> None:
        """Invokes the on_ready stage on all registered services and publishes startup event."""
        event_bus = self.registry.get(EventBusService)

        for service in self.registry.get_all():
            service.on_ready()

        event_bus.publish(KernelStartedEvent(version=self.config.runtime.version))

    def shutdown(self) -> None:
        """Executes a graceful shutdown, tearing down all registered services in reverse order."""
        if self._state == RuntimeState.HALTED:
            return

        self._state = RuntimeState.SHUTTING_DOWN

        try:
            # End the active session if one exists
            session_service = self.registry.get(SessionService)
            if session_service.get_current_session() is not None:
                session_service.end_session()

            self._active_session_id = None

            # Teardown in reverse order of registration
            for service in reversed(self.registry.get_all()):
                try:
                    service.teardown()
                except Exception as e:
                    # Engineering Constitution: fail loudly in development, safely in production
                    print(f"Error during service teardown: {e}", file=sys.stderr)
        finally:
            self._state = RuntimeState.HALTED
            self._boot_time = None
