from unittest.mock import MagicMock

from aios.services.agent import (
    AgentCapability,
    AgentContext,
    AgentFactory,
    AgentLifecycle,
    AgentRegistry,
    AgentTask,
    LocalAgentManager,
)
from aios.services.agent_impl import CareerAgent, MockAgent
from aios.services.intent import Intent, IntentType


def test_agent_registry_and_factory():
    # Test factory creation
    career_agent = AgentFactory.create_agent("career", None, None, None, None)
    assert isinstance(career_agent, CareerAgent)
    assert career_agent.name == "career_agent"

    mock_agent = AgentFactory.create_agent("mock", None, None, None)
    assert isinstance(mock_agent, MockAgent)
    assert mock_agent.name == "mock_agent"

    # Test registry registration and lookups
    registry = AgentRegistry()
    registry.register(career_agent)
    registry.register(mock_agent)

    assert registry.get_agent("career_agent") == career_agent
    assert registry.get_agent("mock_agent") == mock_agent
    assert len(registry.list_agents()) == 2

    registry.unregister("mock_agent")
    assert registry.get_agent("mock_agent") is None
    assert len(registry.list_agents()) == 1


def test_agent_task_and_capabilities():
    task = AgentTask(task_id="t-1", description="Analyze CV", parameters={"format": "pdf"})
    assert task.task_id == "t-1"
    assert task.parameters["format"] == "pdf"

    capability = AgentCapability(name="ats", description="ATS Scoring System")
    assert capability.name == "ats"

    lifecycle = AgentLifecycle.EXECUTING
    assert lifecycle == AgentLifecycle.EXECUTING


def test_local_agent_manager_coordination():
    registry = AgentRegistry()
    orchestrator = MagicMock()
    
    manager = LocalAgentManager(registry, orchestrator)
    manager.initialize()
    
    assert manager.registry == registry
    assert manager.orchestrator == orchestrator


def test_career_agent_context_propagation():
    # Test mock setup for career agent context
    memory_svc = MagicMock()
    context_svc = MagicMock()
    tool_svc = MagicMock()
    model_svc = MagicMock()

    agent = CareerAgent(memory_svc, context_svc, tool_svc, model_svc)

    intent = Intent(
        intent_type=IntentType.CAREER,
        action="AnalyzeJob",
        parameters={"job_description_path": "job.pdf"},
        target_service="career_agent",
        confidence=1.0
    )
    
    # Mock tool reading output
    mock_tool_res = MagicMock()
    mock_tool_res.success = True
    mock_tool_res.output = "Position: Senior Python Architect."
    tool_svc.execute_tool.return_value = mock_tool_res

    # Mock LLM output
    mock_llm_res = MagicMock()
    mock_llm_res.content = "Analysis: High alignment."
    model_svc.execute_request.return_value = mock_llm_res

    ctx = AgentContext(
        intent=intent,
        context=None,
        memories=[],
        tools=[]
    )

    result = agent.execute(ctx)
    assert result.success is True
    assert "Analysis: High alignment." in result.response
    tool_svc.execute_tool.assert_called_once_with("filesystem", {"action": "read", "path": "job.pdf"})
