from unittest.mock import MagicMock

from aios.brain.context_manager import ContextManager
from aios.brain.models import Workflow, WorkflowStep
from aios.brain.planner import BrainPlanner
from aios.brain.provider_selector import ProviderSelector
from aios.brain.skill_selector import SkillSelector
from aios.brain.workflow import WorkflowExecutor
from aios.services.context import WorkspaceContext
from aios.services.memory import Memory, MemoryMetadata, MemoryType
from aios.services.model import LLMResponse
from aios.services.tool import ToolResult
from aios.skills.base import BaseSkill
from aios.skills.metadata import SkillMetadata
from aios.skills.registry import SkillRegistry


def test_skill_selection():
    registry = SkillRegistry()
    
    meta = SkillMetadata(
        id="test_github",
        name="GitHub Mock",
        version="1.0.0",
        author="Tester",
        description="Integrate with GitHub repository and issues",
        category="Automation",
        commands=["github login", "clone repository"],
    )
    skill = BaseSkill(meta, "/tmp/mock_github")
    registry.register(skill)

    selector = SkillSelector(registry)

    # 1. Deterministic/Exact command match
    selections = selector.select_skills("github login")
    assert len(selections) == 1
    assert selections[0].skill_id == "test_github"
    assert selections[0].confidence == 1.0
    assert "github login" in selections[0].matched_commands

    # 2. Heuristic/Keyword match
    selections_heuristic = selector.select_skills("integrate and scan code")
    assert len(selections_heuristic) >= 1
    assert selections_heuristic[0].skill_id == "test_github"
    assert selections_heuristic[0].confidence < 1.0


def test_provider_selection():
    model_service = MagicMock()
    model_service.registry.get_provider_for_model.side_effect = lambda m: {
        "mock-model": "mock",
        "gpt-4o": "openai",
        "claude-3-5-sonnet": "claude",
        "gemini-1.5-pro": "gemini",
        "llama3": "ollama",
    }.get(m, "mock")

    selector = ProviderSelector(model_service)

    # Keyword matching
    p1 = selector.select_provider("please run mock test")
    assert p1.provider_name == "mock"
    assert p1.model_name == "mock-model"

    p2 = selector.select_provider("review PR in github using claude")
    assert p2.provider_name == "claude"
    assert p2.model_name == "claude-3-5-sonnet"

    p3 = selector.select_provider("generate text with gemini")
    assert p3.provider_name == "gemini"
    assert p3.model_name == "gemini-1.5-pro"


def test_context_assembly():
    context_service = MagicMock()
    memory_service = MagicMock()

    workspace_ctx = WorkspaceContext(
        working_directory="/Users/anzarakhtar/aios",
        git_repo_path="/Users/anzarakhtar/aios/.git",
        git_branch="main",
        project_root="/Users/anzarakhtar/aios",
        project_name="aios",
    )
    context_service.get_current_context.return_value = workspace_ctx

    # Mock memory search
    memory_meta = MemoryMetadata(workspace_id="ws1", session_id="sess1")
    mock_memory = Memory(
        memory_id="mem1",
        content="Git configuration stored",
        memory_type=MemoryType.NOTE,
        metadata=memory_meta,
        created_at=0.0,
        updated_at=0.0
    )
    memory_service.search_memory.return_value = [mock_memory]

    manager = ContextManager(context_service, memory_service)
    assembled = manager.assemble_context("setup git connection")

    assert assembled.project_name == "aios"
    assert assembled.git_branch == "main"
    assert assembled.project_root == "/Users/anzarakhtar/aios"
    assert len(assembled.memories) == 1
    assert assembled.memories[0] == "Git configuration stored"


def test_workflow_planning():
    registry = SkillRegistry()
    meta = SkillMetadata(
        id="test_github",
        name="GitHub Mock",
        version="1.0.0",
        author="Tester",
        description="Integrate with GitHub",
        category="Automation",
        commands=["github login", "clone repository"],
    )
    skill = BaseSkill(meta, "/tmp/mock_github")
    registry.register(skill)

    skill_selector = SkillSelector(registry)
    model_service = MagicMock()

    # Stub ModelService to return a structured JSON workflow for complex/multi-skill goals
    mock_llm_response = LLMResponse(
        content='''
        [
            {
                "description": "Log in to GitHub",
                "skill_id": "test_github",
                "command": "github login",
                "args": ""
            },
            {
                "description": "Clone the repository",
                "skill_id": "test_github",
                "command": "clone repository",
                "args": "Anzar0904/aios"
            }
        ]
        ''',
        model_name="claude-3-5-sonnet",
        provider_name="claude"
    )
    model_service.execute_request.return_value = mock_llm_response

    planner = BrainPlanner(skill_selector, model_service)

    # 1. Test deterministic workflow planning (confidence=1.0)
    workflow_det = planner.plan("github login")
    assert len(workflow_det.steps) == 1
    assert workflow_det.steps[0].command == "github login"
    assert workflow_det.steps[0].skill_id == "test_github"

    # 2. Test multi-skill / LLM planning
    workflow_complex = planner.plan("First log in and then clone the repo Anzar0904/aios")
    assert len(workflow_complex.steps) == 2
    assert workflow_complex.steps[0].command == "github login"
    assert workflow_complex.steps[1].command == "clone repository"
    assert workflow_complex.steps[1].args == "Anzar0904/aios"


def test_workflow_execution():
    kernel = MagicMock()
    command_registry = MagicMock()
    tool_service = MagicMock()
    kernel.registry.get.return_value = tool_service

    # Setup command handlers
    mock_login_handler = MagicMock(return_value="Login successful")
    command_registry.get_handler.side_effect = lambda cmd: {
        "github login": mock_login_handler,
    }.get(cmd)

    executor = WorkflowExecutor(kernel, command_registry)

    # 1. Execute regular skill command
    step1 = WorkflowStep(
        step_id="s1",
        description="Login step",
        skill_id="test_github",
        command="github login",
        args="my-token"
    )
    wf = Workflow(workflow_id="wf1", objective="test login", steps=[step1])

    success = executor.execute(wf)
    assert success is True
    assert step1.status == "completed"
    assert "Login successful" in step1.output
    mock_login_handler.assert_called_once_with("my-token")

    # 2. Execute via Action Engine handoff (filesystem write)
    tool_service.execute_tool.return_value = ToolResult(success=True, output="File written successfully")
    step2 = WorkflowStep(
        step_id="s2",
        description="Write a settings config",
        skill_id="action",
        command="write file",
        args="config.txt port=8080"
    )
    wf2 = Workflow(workflow_id="wf2", objective="write settings", steps=[step2])

    success2 = executor.execute(wf2)
    assert success2 is True
    assert step2.status == "completed"
    assert "Execution Report" in step2.output
