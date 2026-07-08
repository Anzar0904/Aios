from unittest.mock import MagicMock, patch

import pytest
from aios.kernel import Kernel, RuntimeState
from aios.registry import ServiceRegistry
from aios.services.base import ServiceLifecycle


class DummyService(ServiceLifecycle):
    def __init__(self):
        self.init_count = 0
        self.ready_count = 0
        self.teardown_count = 0

    def initialize(self):
        self.init_count += 1

    def start(self):
        self.ready_count += 1

    def shutdown(self):
        self.teardown_count += 1


def test_single_initialization():
    """Verify that calling initialize, on_ready, and teardown multiple times only executes once."""
    service = DummyService()

    # Call initialize multiple times
    service.initialize()
    service.initialize()
    service.initialize()
    assert service.init_count == 1

    # Call start multiple times
    service.start()
    service.start()
    assert service.ready_count == 1

    # Call shutdown multiple times
    service.shutdown()
    service.shutdown()
    assert service.teardown_count == 1


def test_service_registration_uniqueness():
    """Verify that registering the same service type more than once raises a ValueError."""
    registry = ServiceRegistry()
    service1 = DummyService()
    service2 = DummyService()

    registry.register(DummyService, service1)

    with pytest.raises(ValueError, match="already registered"):
        registry.register(DummyService, service2)


def test_duplicate_kernel_bootstrap_calls():
    """Verify that duplicate bootstrap/initialization calls on the Kernel

    do not trigger duplicate calls on services.
    """
    registry = ServiceRegistry()
    service = DummyService()
    registry.register(DummyService, service)

    config_path = MagicMock()
    kernel = Kernel(config_path=config_path, registry=registry)
    kernel.config = MagicMock()
    kernel.config.runtime.version = "1.0.0"

    # Mock EventBusService and SessionService to avoid registry missing service errors
    mock_session_service = MagicMock()
    mock_session_service.get_current_session.return_value = None
    mock_event_bus = MagicMock()

    def mock_get(service_type):
        from aios.services.event_bus import EventBusService
        from aios.services.session import SessionService

        if service_type == SessionService:
            return mock_session_service
        if service_type == EventBusService:
            return mock_event_bus
        return registry.get(service_type)

    with patch.object(registry, "get", side_effect=mock_get):
        # 1. First initialization cycle
        kernel._initialize_services()
        kernel._transition_to_ready()

        assert service.init_count == 1
        assert service.ready_count == 1

        # 2. Second (duplicate) initialization cycle
        kernel._initialize_services()
        kernel._transition_to_ready()

        # Should still only be initialized and readied once
        assert service.init_count == 1
        assert service.ready_count == 1

        # 3. Clean shutdown teardown execution
        kernel._state = RuntimeState.READY
        kernel.shutdown()

    assert service.teardown_count == 1
