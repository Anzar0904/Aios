from unittest.mock import MagicMock

from aios.services.agent import (
    AgentCompletedEvent,
    AgentFailedEvent,
    AgentStartedEvent,
)
from aios.services.agent_impl import CareerAgent, LocalAgentRuntime
from aios.services.context import WorkspaceContext
from aios.services.event_bus_impl import LocalEventBus
from aios.services.intent import Intent, IntentType
from aios.services.memory import Memory, MemoryMetadata, MemoryType
from aios.services.model import LLMResponse
from aios.services.tool import ToolMetadata, ToolResult


def test_career_agent_analyze_job():
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
        content="Stubbed career preference",
        memory_type=MemoryType.LEARNING,
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
        success=True, output="Role: Software Engineer"
    )

    model_service.execute_request.return_value = LLMResponse(
        content="[MockLLM] Job Analysis Complete.",
        model_name="claude-3-5-sonnet",
        provider_name="claude",
    )

    event_bus = LocalEventBus()
    runtime = LocalAgentRuntime(
        event_bus, memory_service, context_service, tool_service, model_service
    )
    runtime.initialize()
    runtime.register_agent(CareerAgent(memory_service, context_service, tool_service, model_service))

    # Track runtime events
    started = []
    completed = []
    failed = []
    event_bus.subscribe(AgentStartedEvent, lambda e: started.append(e))
    event_bus.subscribe(AgentCompletedEvent, lambda e: completed.append(e))
    event_bus.subscribe(AgentFailedEvent, lambda e: failed.append(e))

    intent = Intent(
        intent_type=IntentType.CAREER,
        target_service="AgentRuntimeService",
        action="AnalyzeJob",
        parameters={"job_description_path": "job.pdf"},
        confidence=1.0,
    )

    res = runtime.execute(intent)

    assert res.success is True
    assert "[MockLLM]" in res.response
    tool_service.execute_tool.assert_called_with(
        "filesystem", {"action": "read", "path": "job.pdf"}
    )
    model_service.execute_request.assert_called()

    # Check events
    assert len(started) == 1
    assert len(completed) == 1
    assert len(failed) == 0


def test_career_agent_tailor_resume():
    memory_service = MagicMock()
    context_service = MagicMock()
    tool_service = MagicMock()
    model_service = MagicMock()

    tool_service.execute_tool.return_value = ToolResult(success=True, output="Dummy file content")
    model_service.execute_request.return_value = LLMResponse(
        content="[MockLLM] Suggestions to tailor resume.",
        model_name="claude-3-5-sonnet",
        provider_name="claude",
    )

    event_bus = LocalEventBus()
    runtime = LocalAgentRuntime(
        event_bus, memory_service, context_service, tool_service, model_service
    )
    runtime.initialize()
    runtime.register_agent(CareerAgent(memory_service, context_service, tool_service, model_service))

    intent = Intent(
        intent_type=IntentType.CAREER,
        target_service="AgentRuntimeService",
        action="TailorResume",
        parameters={"resume_path": "resume.pdf", "job_description_path": "job.pdf"},
        confidence=1.0,
    )

    res = runtime.execute(intent)

    assert res.success is True
    assert "[MockLLM]" in res.response
    assert tool_service.execute_tool.call_count == 2


def test_career_agent_ats_score():
    memory_service = MagicMock()
    context_service = MagicMock()
    tool_service = MagicMock()
    model_service = MagicMock()

    tool_service.execute_tool.return_value = ToolResult(success=True, output="Dummy file content")
    model_service.execute_request.return_value = LLMResponse(
        content="[MockLLM] ATS Score: 85.",
        model_name="claude-3-5-sonnet",
        provider_name="claude",
    )

    event_bus = LocalEventBus()
    runtime = LocalAgentRuntime(
        event_bus, memory_service, context_service, tool_service, model_service
    )
    runtime.initialize()
    runtime.register_agent(CareerAgent(memory_service, context_service, tool_service, model_service))

    intent = Intent(
        intent_type=IntentType.CAREER,
        target_service="AgentRuntimeService",
        action="ATSScore",
        parameters={"resume_path": "resume.pdf", "job_description_path": "job.pdf"},
        confidence=1.0,
    )

    res = runtime.execute(intent)

    assert res.success is True
    assert "[MockLLM]" in res.response


def test_career_agent_interview_prep():
    memory_service = MagicMock()
    context_service = MagicMock()
    tool_service = MagicMock()
    model_service = MagicMock()

    tool_service.execute_tool.return_value = ToolResult(
        success=True, output="Role: Software Engineer"
    )
    model_service.execute_request.return_value = LLMResponse(
        content="[MockLLM] Q1: Tell me about yourself.",
        model_name="claude-3-5-sonnet",
        provider_name="claude",
    )

    event_bus = LocalEventBus()
    runtime = LocalAgentRuntime(
        event_bus, memory_service, context_service, tool_service, model_service
    )
    runtime.initialize()
    runtime.register_agent(CareerAgent(memory_service, context_service, tool_service, model_service))

    intent = Intent(
        intent_type=IntentType.CAREER,
        target_service="AgentRuntimeService",
        action="InterviewPrep",
        parameters={"job_description_path": "job.pdf"},
        confidence=1.0,
    )

    res = runtime.execute(intent)

    assert res.success is True
    assert "[MockLLM]" in res.response


def test_career_agent_cover_letter():
    memory_service = MagicMock()
    context_service = MagicMock()
    tool_service = MagicMock()
    model_service = MagicMock()

    tool_service.execute_tool.return_value = ToolResult(success=True, output="Dummy content")
    model_service.execute_request.return_value = LLMResponse(
        content="[MockLLM] Dear Hiring Manager...",
        model_name="claude-3-5-sonnet",
        provider_name="claude",
    )

    event_bus = LocalEventBus()
    runtime = LocalAgentRuntime(
        event_bus, memory_service, context_service, tool_service, model_service
    )
    runtime.initialize()
    runtime.register_agent(CareerAgent(memory_service, context_service, tool_service, model_service))

    intent = Intent(
        intent_type=IntentType.CAREER,
        target_service="AgentRuntimeService",
        action="CoverLetter",
        parameters={"resume_path": "resume.pdf", "job_description_path": "job.pdf"},
        confidence=1.0,
    )

    res = runtime.execute(intent)

    assert res.success is True
    assert "[MockLLM]" in res.response
