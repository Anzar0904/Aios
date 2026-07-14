from unittest.mock import patch

import pytest
from aios.cli import execute_builtin_cli_command
from aios.registry import ServiceRegistry
from aios.services.context import ContextChangedEvent, ContextLoadedEvent, ContextService
from aios.services.context_impl import LocalContextService
from aios.services.event_bus_impl import LocalEventBus
from aios.services.graph import EntityType, GraphService, RelationshipType
from aios.services.graph_impl import GraphServiceImpl
from aios.services.intent import Intent, IntentType
from aios.services.nl_os import ActionPlan, ActionStep, NLOSService
from aios.services.nl_os_impl import NLOSServiceImpl


@pytest.fixture
def setup_services(tmp_path):
    event_bus = LocalEventBus()
    event_bus.register_event_type(ContextLoadedEvent)
    event_bus.register_event_type(ContextChangedEvent)

    # Context service
    context_svc = LocalContextService(event_bus)
    context_svc._context_path = tmp_path / "context.json"
    context_svc.initialize()

    # Graph service
    graph_svc = GraphServiceImpl(db_path=str(tmp_path / "test_graph.db"))
    graph_svc.initialize()
    graph_svc.start()

    # NL OS Service
    nl_os_svc = NLOSServiceImpl(workspace_root=str(tmp_path))
    nl_os_svc.initialize()

    # Register globally
    registry = ServiceRegistry()
    ServiceRegistry._global_registry = registry
    registry.register(ContextService, context_svc)
    registry.register(GraphService, graph_svc)
    registry.register(NLOSService, nl_os_svc)

    yield context_svc, graph_svc, nl_os_svc

    graph_svc.shutdown()
    nl_os_svc.shutdown()
    ServiceRegistry._global_registry = None


def test_context_engine_get_set_clear(setup_services):
    context_svc, _, _ = setup_services

    context_svc.set_context_item("project", "TestProject")
    context_svc.set_context_item("workflow", "LeadGen")

    assert context_svc.get_context_item("project") == "TestProject"
    assert context_svc.get_context_item("workflow") == "LeadGen"
    assert context_svc.get_context_item("nonexistent") is None

    # Clear context
    context_svc.clear_context()
    assert context_svc.get_context_item("project") is None
    assert context_svc.get_context_item("workflow") is None


def test_natural_language_router_heuristics(setup_services):
    _, _, nl_os_svc = setup_services

    # GitHub prs
    tokens = nl_os_svc.route_query("Show open GitHub PRs")
    assert tokens == ["github", "prs"]

    # Workflow deploy
    tokens = nl_os_svc.route_query("Deploy workflow my_workflow")
    assert tokens == ["workflow", "deploy", "my_workflow"]

    # Project create
    tokens = nl_os_svc.route_query("Create a project for hackathon")
    assert tokens == ["project", "create", "hackathon"]

    # Personal Priorities
    tokens = nl_os_svc.route_query("Show today's priorities")
    assert tokens == ["today"]


def test_pronoun_resolution(setup_services):
    context_svc, _, nl_os_svc = setup_services

    # Set context items
    context_svc.set_context_item("workflow", "lead_generation")
    context_svc.set_context_item("project", "ai_tutor")

    # Pronoun resolution for workflow
    tokens = nl_os_svc.route_query("Deploy it")
    assert tokens == ["workflow", "deploy", "lead_generation"]

    # Pronoun resolution for project
    tokens = nl_os_svc.route_query("Create project for it")
    assert tokens == ["project", "create", "ai_tutor"]


def test_entity_extraction(setup_services):
    _, _, nl_os_svc = setup_services

    query = "Design a project for compiler_design and deploy workflow code_deploy"
    entities = nl_os_svc.extract_entities(query)

    assert "compiler_design" in entities["projects"]
    assert "code_deploy" in entities["workflows"]


def test_action_planner(setup_services):
    _, _, nl_os_svc = setup_services

    query = "Create a project AI_Tutor and deploy the workflow marketing_campaign"
    plan = nl_os_svc.generate_plan(query)

    assert isinstance(plan, ActionPlan)
    assert len(plan.steps) == 2
    assert plan.steps[0].target == "aios project create AI_Tutor"
    assert plan.steps[1].target == "aios workflow deploy marketing_campaign"
    assert "step_1" in plan.steps[1].dependencies


def test_action_executor_and_graph_sync(setup_services):
    _, graph_svc, nl_os_svc = setup_services

    # Create simple plan
    step1 = ActionStep(
        step_id="step_1",
        action_type="cli_command",
        target="aios context set project my_test_proj",
        description="Set project context",
    )
    plan = ActionPlan(
        plan_id="plan_test_123", objective="Set project to my_test_proj", steps=[step1]
    )

    with patch("aios.cli.execute_builtin_cli_command", return_value=True) as mock_exec:
        success = nl_os_svc.execute_plan(plan)
        assert success is True
        assert step1.status == "completed"
        assert plan.status == "completed"
        mock_exec.assert_called_once_with(
            ["context", "set", "project", "my_test_proj"], exit_on_complete=False
        )

    # Verify entities were synced in Knowledge Graph
    plan_node = graph_svc.get_entity("plan_plan_test_123")
    assert plan_node is not None
    assert plan_node.entity_type == EntityType.PLAN
    assert plan_node.properties["objective"] == "Set project to my_test_proj"

    act_node = graph_svc.get_entity("act_plan_test_123_step_1")
    assert act_node is not None
    assert act_node.entity_type == EntityType.ACTION
    assert act_node.properties["target"] == "aios context set project my_test_proj"

    # Check relationships
    rels = graph_svc.find_relationships(source_id="plan_plan_test_123")
    assert len(rels) > 0
    assert rels[0].relationship_type == RelationshipType.PLANNED


def test_learning_engine(setup_services):
    _, _, nl_os_svc = setup_services

    # Execute a plan that succeeds
    step = ActionStep(
        step_id="step_1",
        action_type="cli_command",
        target="aios status",
        description="Check status",
    )
    plan = ActionPlan(plan_id="plan_1", objective="check system status", steps=[step])

    with patch("aios.cli.execute_builtin_cli_command", return_value=True):
        nl_os_svc.execute_plan(plan)

    patterns = nl_os_svc.get_learning_patterns()
    assert "check system status" in patterns["successful_patterns"]
    assert patterns["frequently_used_actions"]["check system"] == 1


def test_explanation_engine(setup_services):
    _, _, nl_os_svc = setup_services

    intent = Intent(
        intent_type=IntentType.GITHUB,
        target_service="GitHubService",
        action="list_prs",
        parameters={},
        confidence=0.95,
    )
    nl_os_svc.record_intent_history("Show open GitHub PRs", intent, success=True)

    explanation = nl_os_svc.get_last_explanation()
    assert explanation["objective"] == "Show open GitHub PRs"
    assert "Resolved via" in explanation["reasoning"]


def test_cli_subcommands(setup_services):
    # Verify execute_builtin_cli_command routes correctly for NL OS commands
    with patch("aios.cli.execute_builtin_cli_command", return_value=True):
        # aios context set project AI_Tutor
        res = execute_builtin_cli_command(
            ["context", "set", "project", "AI_Tutor"], exit_on_complete=False
        )
        assert res is True

        # aios context clear
        res = execute_builtin_cli_command(["context", "clear"], exit_on_complete=False)
        assert res is True

        # aios context (list/show)
        res = execute_builtin_cli_command(["context"], exit_on_complete=False)
        assert res is True
