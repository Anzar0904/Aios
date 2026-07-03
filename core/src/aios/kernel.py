import sys
import time
from enum import Enum, auto
from pathlib import Path

from aios.config import OSConfig, load_config
from aios.registry import ServiceRegistry
from aios.services.context import ContextLoadedEvent, ContextService
from aios.services.context_impl import LocalContextService
from aios.services.event_bus import EventBusService, KernelStartedEvent
from aios.services.event_bus_impl import LocalEventBus
from aios.services.memory import MemoryService
from aios.services.model import ModelService
from aios.services.session import SessionService

# Import stubs for bootstrap registration
from aios.services.stubs import (
    StubMemoryService,
    StubModelService,
    StubSessionService,
    StubToolService,
)
from aios.services.tool import ToolService


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

            event_bus.subscribe(KernelStartedEvent, log_startup)
            event_bus.subscribe(ContextLoadedEvent, log_context)

            # Automatically detect workspace context
            context_service = self.registry.get(ContextService)
            context_service.detect_context()

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

    def end_session(self) -> None:
        """Disassociates the active session from the runtime."""
        self._active_session_id = None

    def mark_busy(self, busy: bool) -> None:
        """Transitions the runtime state between READY and BUSY."""
        if self._state not in (RuntimeState.READY, RuntimeState.BUSY):
            raise RuntimeError(f"Cannot change busy status when Kernel state is {self._state.name}")
        self._state = RuntimeState.BUSY if busy else RuntimeState.READY

    def _register_core_services(self) -> None:
        """Instantiates and registers the core services."""
        event_bus = LocalEventBus()
        self.registry.register(EventBusService, event_bus)

        self.registry.register(ContextService, LocalContextService(event_bus))
        self.registry.register(MemoryService, StubMemoryService())
        self.registry.register(SessionService, StubSessionService())
        self.registry.register(ModelService, StubModelService())
        self.registry.register(ToolService, StubToolService())

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
