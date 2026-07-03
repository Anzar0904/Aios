from unittest.mock import MagicMock

from aios.services.agent import (
    AgentCompletedEvent,
    AgentFailedEvent,
    AgentStartedEvent,
)
from aios.services.agent_impl import LocalAgentRuntime, MockAgent
from aios.services.context import WorkspaceContext
from aios.services.event_bus_impl import LocalEventBus
from aios.services.intent import Intent, IntentType
from aios.services.memory import Memory, MemoryType


def test_agent_registration():
    event_bus = LocalEventBus()
    memory_service = MagicMock()
    context_service = MagicMock()
    tool_service = MagicMock()

    runtime = LocalAgentRuntime(event_bus, memory_service, context_service, tool_service)
    runtime.initialize()

    # Verify MockAgent is registered by default
    agents = runtime._agents
    assert "mock_agent" in agents
    assert isinstance(agents["mock_agent"], MockAgent)

    # Custom Agent
    custom_agent = MagicMock()
    custom_agent.name = "custom"
    runtime.register_agent(custom_agent)
    assert "custom" in agents

    runtime.unregister_agent("custom")
    assert "custom" not in agents


def test_mock_agent_execution_pipeline():
    event_bus = LocalEventBus()

    # Mock Services
    from aios.services.memory import MemoryMetadata

    memory_service = MagicMock()
    dummy_metadata = MemoryMetadata(
        workspace_id="ws-123",
        session_id="session-123",
        tags=[],
        importance=1,
    )
    dummy_memory = Memory(
        memory_id="test-mem-id",
        content="Stubbed saved note",
        memory_type=MemoryType.NOTE,
        metadata=dummy_metadata,
        created_at=0.0,
        updated_at=0.0,
    )
    memory_service.add_memory.return_value = dummy_memory
    memory_service.load_workspace_memory.return_value = [dummy_memory]

    context_service = MagicMock()
    dummy_context = WorkspaceContext(
        working_directory="/test",
        git_repo_path="/test",
        git_branch="main",
        project_root="/test",
        project_name="test-project",
    )
    context_service.get_current_context.return_value = dummy_context

    tool_service = MagicMock()
    tool_service.list_tools.return_value = []

    runtime = LocalAgentRuntime(event_bus, memory_service, context_service, tool_service)
    runtime.initialize()

    # Track events
    started_events = []
    completed_events = []
    failed_events = []

    event_bus.subscribe(AgentStartedEvent, lambda e: started_events.append(e))
    event_bus.subscribe(AgentCompletedEvent, lambda e: completed_events.append(e))
    event_bus.subscribe(AgentFailedEvent, lambda e: failed_events.append(e))

    # Test Memory Addition execute
    intent_mem = Intent(
        intent_type=IntentType.MEMORY,
        target_service="MemoryService",
        action="Add",
        parameters={"content": "Agent logic test"},
        confidence=1.0,
    )
    res_mem = runtime.execute(intent_mem)

    assert res_mem.success is True
    assert "Memory stored successfully" in res_mem.response
    assert res_mem.data["memory"] == dummy_memory
    memory_service.add_memory.assert_called_with("Agent logic test", MemoryType.NOTE)

    assert len(started_events) == 1
    assert started_events[0].intent == intent_mem
    assert len(completed_events) == 1
    assert completed_events[0].result == res_mem
    assert len(failed_events) == 0


def test_agent_runtime_failure_handling():
    event_bus = LocalEventBus()
    memory_service = MagicMock()
    context_service = MagicMock()
    tool_service = MagicMock()

    # Force context_service to raise exception to trigger failure path
    context_service.get_current_context.side_effect = Exception("Database crash")

    runtime = LocalAgentRuntime(event_bus, memory_service, context_service, tool_service)
    runtime.initialize()

    failed_events = []
    event_bus.subscribe(AgentFailedEvent, lambda e: failed_events.append(e))

    intent = Intent(
        intent_type=IntentType.SYSTEM,
        target_service="Kernel",
        action="Status",
        parameters={},
        confidence=1.0,
    )
    res = runtime.execute(intent)

    assert res.success is False
    assert "Database crash" in res.response
    assert len(failed_events) == 1
    assert "Database crash" in failed_events[0].error
