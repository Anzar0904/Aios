from aios.kernel import Kernel
from aios.services.intent import Intent, IntentType
from aios.services.intent_impl import LocalIntentResolver


def test_intent_classification():
    resolver = LocalIntentResolver()

    # Memory
    assert resolver.classify("remember to write code") == IntentType.MEMORY
    assert resolver.classify("add memory project spec") == IntentType.MEMORY

    # Context
    assert resolver.classify("show context") == IntentType.CONTEXT
    assert resolver.classify("show current project") == IntentType.CONTEXT

    # Session
    assert resolver.classify("end session") == IntentType.SESSION
    assert resolver.classify("exit") == IntentType.SESSION

    # System
    assert resolver.classify("status") == IntentType.SYSTEM
    assert resolver.classify("uptime") == IntentType.SYSTEM

    # Unknown
    assert resolver.classify("hello there") == IntentType.UNKNOWN


def test_intent_resolution():
    resolver = LocalIntentResolver()

    # Memory resolution
    intent_mem = resolver.resolve("remember this: study compiler design")
    assert intent_mem.intent_type == IntentType.MEMORY
    assert intent_mem.action == "Add"
    assert intent_mem.parameters == {"content": "study compiler design"}
    assert intent_mem.confidence == 1.0

    # Empty content fallback
    intent_mem_empty = resolver.resolve("remember")
    assert intent_mem_empty.parameters["content"] == "Remembered interaction"

    # Context resolution
    intent_ctx = resolver.resolve("show context")
    assert intent_ctx.intent_type == IntentType.CONTEXT
    assert intent_ctx.action == "Show"
    assert intent_ctx.parameters == {}

    # System resolution
    intent_sys = resolver.resolve("status")
    assert intent_sys.intent_type == IntentType.SYSTEM
    assert intent_sys.action == "Status"

    # Unknown resolution
    intent_unk = resolver.resolve("exotic command")
    assert intent_unk.intent_type == IntentType.UNKNOWN
    assert intent_unk.confidence == 0.0


def test_intent_validation():
    resolver = LocalIntentResolver()

    # Valid intent
    valid = Intent(
        intent_type=IntentType.SYSTEM,
        target_service="Kernel",
        action="Status",
        parameters={},
        confidence=1.0,
    )
    assert resolver.validate(valid) is True

    # Invalid - unknown type
    invalid_unk = Intent(
        intent_type=IntentType.UNKNOWN,
        target_service="None",
        action="Unknown",
        parameters={},
        confidence=0.0,
    )
    assert resolver.validate(invalid_unk) is False

    # Invalid - missing memory content
    invalid_mem = Intent(
        intent_type=IntentType.MEMORY,
        target_service="MemoryService",
        action="Add",
        parameters={},
        confidence=1.0,
    )
    assert resolver.validate(invalid_mem) is False


def test_kernel_intent_execution(tmp_path):
    config_file = tmp_path / "config.toml"
    config_file.write_text("""
[runtime]
name = "Test AI OS"
version = "0.1.0"
debug = true
""")

    kernel = Kernel(config_file)
    kernel.boot()

    # Test executing system status intent
    intent_sys = Intent(
        intent_type=IntentType.SYSTEM,
        target_service="Kernel",
        action="Status",
        parameters={},
        confidence=1.0,
    )
    res_sys = kernel.execute_intent(intent_sys)
    assert res_sys.success is True
    assert "System Status" in res_sys.message

    # Test executing memory add intent
    intent_mem = Intent(
        intent_type=IntentType.MEMORY,
        target_service="MemoryService",
        action="Add",
        parameters={"content": "Kernel is running fine"},
        confidence=1.0,
    )
    res_mem = kernel.execute_intent(intent_mem)
    assert res_mem.success is True
    assert "Memory stored successfully" in res_mem.message

    # Test executing context show intent
    intent_ctx = Intent(
        intent_type=IntentType.CONTEXT,
        target_service="ContextService",
        action="Show",
        parameters={},
        confidence=1.0,
    )
    res_ctx = kernel.execute_intent(intent_ctx)
    assert res_ctx.success is True
    assert "Current Context" in res_ctx.message

    # Test executing session end intent
    intent_sess = Intent(
        intent_type=IntentType.SESSION,
        target_service="SessionService",
        action="End",
        parameters={},
        confidence=1.0,
    )
    res_sess = kernel.execute_intent(intent_sess)
    assert res_sess.success is True
    assert "Session ended successfully" in res_sess.message

    kernel.shutdown()
