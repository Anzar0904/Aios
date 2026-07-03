import pytest
from aios.kernel import Kernel, RuntimeState
from aios.services.context import ContextService
from aios.services.event_bus import EventBusService
from aios.services.memory import MemoryService
from aios.services.model import ModelService
from aios.services.session import SessionService
from aios.services.tool import ToolService


def test_kernel_state_transitions(tmp_path):
    config_file = tmp_path / "config.toml"
    config_file.write_text("""
[runtime]
name = "Test AI OS"
version = "0.1.0"
debug = true
""")

    kernel = Kernel(config_file)
    assert kernel.state == RuntimeState.HALTED
    assert kernel.uptime == 0.0
    assert kernel.active_session_id is None

    # Verify invalid transitions from HALTED state
    with pytest.raises(RuntimeError):
        kernel.start_session("session-123")
    with pytest.raises(RuntimeError):
        kernel.mark_busy(True)

    kernel.boot()
    assert kernel.state == RuntimeState.READY
    assert kernel.uptime > 0.0
    assert kernel.config is not None
    assert kernel.config.runtime.name == "Test AI OS"

    # Assert services are registered
    assert kernel.registry.get(ContextService) is not None
    assert kernel.registry.get(MemoryService) is not None
    assert kernel.registry.get(SessionService) is not None
    assert kernel.registry.get(ModelService) is not None
    assert kernel.registry.get(ToolService) is not None
    assert kernel.registry.get(EventBusService) is not None

    # Test starting and ending session
    kernel.start_session("session-123")
    assert kernel.active_session_id == "session-123"

    # Test busy state transition
    kernel.mark_busy(True)
    assert kernel.state == RuntimeState.BUSY
    kernel.mark_busy(False)
    assert kernel.state == RuntimeState.READY

    kernel.end_session()
    assert kernel.active_session_id is None

    # Test booting when already booted raises error
    with pytest.raises(RuntimeError):
        kernel.boot()

    # Test shutdown transitions back to HALTED
    kernel.shutdown()
    assert kernel.state == RuntimeState.HALTED
    assert kernel.uptime == 0.0
    assert kernel.active_session_id is None
