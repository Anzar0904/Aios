from unittest.mock import patch

import pytest
from aios.cli import execute_builtin_cli_command
from aios.registry import ServiceRegistry
from aios.services.agent_platform import AgentMessage, AutonomousAgentPlatform, MultiAgentTask
from aios.services.context import ContextChangedEvent, ContextLoadedEvent, ContextService
from aios.services.context_impl import LocalContextService
from aios.services.core_agents import BaseCoreAgent
from aios.services.event_bus_impl import LocalEventBus
from aios.services.graph import GraphService, RelationshipType
from aios.services.graph_impl import GraphServiceImpl


@pytest.fixture
def setup_agent_services(tmp_path):
    event_bus = LocalEventBus()
    event_bus.register_event_type(ContextLoadedEvent)
    event_bus.register_event_type(ContextChangedEvent)

    # Context
    context_svc = LocalContextService(event_bus)
    context_svc._context_path = tmp_path / "context.json"
    context_svc.initialize()

    # Graph
    graph_svc = GraphServiceImpl(db_path=str(tmp_path / "test_graph.db"))
    graph_svc.initialize()
    graph_svc.start()

    # Agent Platform
    platform = AutonomousAgentPlatform(workspace_root=str(tmp_path))

    # Register globally
    registry = ServiceRegistry()
    ServiceRegistry._global_registry = registry
    registry.register(ContextService, context_svc)
    registry.register(GraphService, graph_svc)
    registry.register(AutonomousAgentPlatform, platform)

    platform.initialize()

    yield context_svc, graph_svc, platform

    graph_svc.shutdown()
    platform.shutdown()
    ServiceRegistry._global_registry = None


def test_agent_registry_seeding(setup_agent_services):
    _, _, platform = setup_agent_services

    # 7 Core agents must be seeded
    agents = platform.list_agents()
    assert len(agents) == 7

    roles = [a.role for a in agents]
    assert "Software Engineer" in roles
    assert "Test Engineer" in roles
    assert "Documentation Engineer" in roles
    assert "Research Engineer" in roles
    assert "Agency Engineer" in roles
    assert "Automation Engineer" in roles
    assert "Integration Engineer" in roles

    # Custom Agent Registration
    custom = BaseCoreAgent("agent_custom", "CustomAgent", "Custom Assistant", ["help"])
    platform.register_agent(custom, "Custom Assistant", ["help"])
    assert len(platform.list_agents()) == 8
    assert platform.get_agent("CustomAgent") is not None


def test_communication_bus(setup_agent_services):
    _, graph_svc, platform = setup_agent_services

    # Print diagnostics
    print("Graph service resolves in platform:", platform._get_graph_service())
    print("Software agent entity in DB:", graph_svc.get_entity("agent_agent_software"))
    print("Test agent entity in DB:", graph_svc.get_entity("agent_agent_test"))

    # Send message from software to test
    msg = platform.send_message(
        sender_id="agent_software",
        recipient_id="agent_test",
        content="Please review this implementation.",
        message_type="request",
    )

    assert isinstance(msg, AgentMessage)
    assert msg.sender_id == "agent_software"
    assert msg.recipient_id == "agent_test"
    assert msg.content == "Please review this implementation."

    # Check messages list
    messages = platform.get_messages()
    assert len(messages) == 1

    # Check relationship in Graph
    rels = graph_svc.find_relationships(source_id="agent_agent_software")
    print("Relationships in DB:", rels)
    assert len(rels) > 0
    assert rels[0].relationship_type == RelationshipType.COLLABORATES_WITH
    assert rels[0].target_id == "agent_agent_test"


def test_task_delegation_engine(setup_agent_services):
    _, graph_svc, platform = setup_agent_services

    # Register a parent task
    task = MultiAgentTask(task_id="task_main", title="Main Job", description="Build something")
    platform._tasks[task.task_id] = task
    # Sync task to graph first so that task entity exists!
    platform._sync_task_to_graph(task)

    # Assign task
    platform.assign_task("task_main", "agent_software")

    desc = platform.get_agent_descriptor("softwareengineer")
    assert desc.status == "busy"
    assert "task_main" in desc.assigned_tasks

    # Verify graph sync
    rel = graph_svc.find_relationships(source_id="task_task_main")
    assert len(rel) > 0
    assert rel[0].relationship_type == RelationshipType.ASSIGNED_TO

    # Reassign task
    platform.reassign_task("task_main", "agent_test")
    assert "task_main" not in desc.assigned_tasks
    assert desc.status == "idle"

    test_desc = platform.get_agent_descriptor("testengineer")
    assert "task_main" in test_desc.assigned_tasks
    assert test_desc.status == "busy"

    # Split task
    subtasks = platform.split_task(
        "task_main",
        [
            {"title": "Sub 1", "description": "Part 1"},
            {"title": "Sub 2", "description": "Part 2", "dependencies": ["task_main_sub_1"]},
        ],
    )
    assert len(subtasks) == 2
    assert "task_main_sub_1" in platform._tasks
    assert "task_main_sub_2" in platform._tasks
    assert platform._tasks["task_main_sub_2"].dependencies == ["task_main_sub_1"]

    # Merge tasks
    platform.merge_tasks(["task_main_sub_1", "task_main_sub_2"], "task_main")
    assert "task_main_sub_1" not in platform._tasks


def test_planning_engine(setup_agent_services):
    _, _, platform = setup_agent_services

    tasks = platform.generate_plan("Build a CRM system")
    assert len(tasks) == 4
    assert tasks[0].assigned_agent == "agent_research"
    assert tasks[1].assigned_agent == "agent_software"
    assert tasks[2].assigned_agent == "agent_test"
    assert tasks[3].assigned_agent == "agent_doc"
    assert tasks[1].dependencies == [tasks[0].task_id]


def test_execution_engine_and_memory(setup_agent_services):
    _, _, platform = setup_agent_services

    tasks = platform.generate_plan("Build a CRM system")

    # Execute plan
    success = platform.execute_plan(tasks)
    assert success is True

    # Verify all tasks are completed
    for t in tasks:
        assert t.status == "completed"

    # Check agent memory logs
    mem = platform.get_agent_memory("agent_software")
    assert len(mem) == 1
    assert mem[0]["success"] is True
    assert "successfully" in mem[0]["lesson_learned"].lower()

    # Verify metrics update
    desc = platform.get_agent_descriptor("softwareengineer")
    assert desc.performance_metrics["tasks_completed"] == 1
    assert desc.performance_metrics["success_rate"] == 1.0


def test_cli_agent_commands(setup_agent_services):
    with patch("aios.cli.execute_builtin_cli_command", return_value=True):
        res = execute_builtin_cli_command(["agents"], exit_on_complete=False)
        assert res is True

        res = execute_builtin_cli_command(["agent", "list"], exit_on_complete=False)
        assert res is True

        res = execute_builtin_cli_command(["agent", "status"], exit_on_complete=False)
        assert res is True

        res = execute_builtin_cli_command(
            ["agent", "status", "SoftwareEngineer"], exit_on_complete=False
        )
        assert res is True

        res = execute_builtin_cli_command(
            ["agent", "assign", "task_123", "agent_software"], exit_on_complete=False
        )
        assert res is True

        res = execute_builtin_cli_command(
            ["agent", "execute", "Build a CRM system"], exit_on_complete=False
        )
        assert res is True

        res = execute_builtin_cli_command(
            ["agent", "memory", "agent_software"], exit_on_complete=False
        )
        assert res is True
