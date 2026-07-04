from unittest.mock import MagicMock

from aios.services.agent import (
    AgentCompletedEvent,
    AgentFailedEvent,
    AgentStartedEvent,
)
from aios.services.agent_impl import DeveloperAgent, LocalAgentRuntime
from aios.services.context import WorkspaceContext
from aios.services.event_bus_impl import LocalEventBus
from aios.services.intent import Intent, IntentType
from aios.services.memory import Memory, MemoryMetadata, MemoryType
from aios.services.model import LLMResponse
from aios.services.tool import ToolMetadata, ToolResult


def test_developer_agent_analyze_repository():
    # Mock services
    memory_service = MagicMock()
    context_service = MagicMock()
    tool_service = MagicMock()
    model_service = MagicMock()

    dummy_context = WorkspaceContext(
        working_directory="/test",
        git_repo_path="/test",
        git_branch="main",
        project_root="/test",
        project_name="test-project",
    )
    context_service.get_current_context.return_value = dummy_context

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
    memory_service.load_workspace_memory.return_value = [dummy_memory]

    tool_service.list_tools.return_value = [
        ToolMetadata(
            name="filesystem",
            description="fs",
            input_schema={},
            output_schema={},
        )
    ]
    tool_service.execute_tool.return_value = ToolResult(
        success=True, output="core\nconfig\npyproject.toml"
    )

    model_service.execute_request.return_value = LLMResponse(
        content="[MockLLM] Repository analysis details...",
        model_name="claude-3-5-sonnet",
        provider_name="claude",
    )

    event_bus = LocalEventBus()
    runtime = LocalAgentRuntime(
        event_bus, memory_service, context_service, tool_service, model_service
    )
    runtime.initialize()
    runtime.register_agent(DeveloperAgent(memory_service, context_service, tool_service, model_service))

    # Track runtime events
    started = []
    completed = []
    failed = []
    event_bus.subscribe(AgentStartedEvent, lambda e: started.append(e))
    event_bus.subscribe(AgentCompletedEvent, lambda e: completed.append(e))
    event_bus.subscribe(AgentFailedEvent, lambda e: failed.append(e))

    # Trigger developer repository analysis intent
    intent = Intent(
        intent_type=IntentType.DEVELOPER,
        target_service="AgentRuntimeService",
        action="AnalyzeRepository",
        parameters={},
        confidence=1.0,
    )

    res = runtime.execute(intent)

    assert res.success is True
    assert "[MockLLM]" in res.response
    model_service.execute_request.assert_called()

    # Check events
    assert len(started) == 1
    assert len(completed) == 1
    assert len(failed) == 0


def test_developer_agent_explain_file():
    memory_service = MagicMock()
    context_service = MagicMock()
    tool_service = MagicMock()
    model_service = MagicMock()

    tool_service.execute_tool.return_value = ToolResult(
        success=True, output="class Kernel:\n    pass"
    )
    model_service.execute_request.return_value = LLMResponse(
        content="[MockLLM] File explains...",
        model_name="claude-3-5-sonnet",
        provider_name="claude",
    )

    event_bus = LocalEventBus()
    runtime = LocalAgentRuntime(
        event_bus, memory_service, context_service, tool_service, model_service
    )
    runtime.initialize()
    runtime.register_agent(DeveloperAgent(memory_service, context_service, tool_service, model_service))

    intent = Intent(
        intent_type=IntentType.DEVELOPER,
        target_service="AgentRuntimeService",
        action="ExplainFile",
        parameters={"path": "core/src/aios/kernel.py"},
        confidence=1.0,
    )

    res = runtime.execute(intent)

    assert res.success is True
    assert "[MockLLM]" in res.response
    tool_service.execute_tool.assert_called_with(
        "filesystem", {"action": "read", "path": "core/src/aios/kernel.py"}
    )


def test_developer_agent_git_review():
    memory_service = MagicMock()
    context_service = MagicMock()
    tool_service = MagicMock()
    model_service = MagicMock()

    # Stub git status and git log responses
    def mock_execute_tool(name, args):
        if name == "git" and args.get("action") == "status":
            return ToolResult(success=True, output="modified: kernel.py")
        elif name == "git" and args.get("action") == "log":
            return ToolResult(success=True, output="feat: initial bootstrap")
        return ToolResult(success=False, output="")

    tool_service.execute_tool.side_effect = mock_execute_tool
    model_service.execute_request.return_value = LLMResponse(
        content="[MockLLM] Git review complete.",
        model_name="claude-3-5-sonnet",
        provider_name="claude",
    )

    event_bus = LocalEventBus()
    runtime = LocalAgentRuntime(
        event_bus, memory_service, context_service, tool_service, model_service
    )
    runtime.initialize()
    runtime.register_agent(DeveloperAgent(memory_service, context_service, tool_service, model_service))

    intent = Intent(
        intent_type=IntentType.DEVELOPER,
        target_service="AgentRuntimeService",
        action="GitReview",
        parameters={},
        confidence=1.0,
    )

    res = runtime.execute(intent)

    assert res.success is True
    assert "[MockLLM]" in res.response
