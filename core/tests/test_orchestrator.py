import tempfile
from pathlib import Path
from unittest.mock import MagicMock

from aios.bootstrap import bootstrap_kernel
from aios.services.command import CommandRegistry
from aios.services.command.metadata import CommandCategory, CommandMetadata
from aios.services.orchestrator import (
    SkillInvocation,
    ExecutionPlan,
    ExecutionContext,
    OrchestratorService,
)
from aios.services.orchestrator_impl import LocalOrchestratorService


def test_dependency_level_grouping_and_cycles():
    registry = CommandRegistry()
    service = LocalOrchestratorService(registry)

    # 1. Valid acyclic plan
    plan_valid = ExecutionPlan(
        plan_id="plan-1",
        invocations=[
            SkillInvocation("step1", "research", "command1", []),
            SkillInvocation("step2", "personal", "command2", ["step1"]),
            SkillInvocation("step3", "n8n", "command3", ["step1"])
        ]
    )

    levels = service._group_invocations_into_levels(plan_valid.invocations)
    assert len(levels) == 2
    assert levels[0][0].step_id == "step1"
    # step2 and step3 both depend on step1, so they reside at level 1
    level1_steps = {s.step_id for s in levels[1]}
    assert "step2" in level1_steps
    assert "step3" in level1_steps

    # 2. Circular plan
    plan_cycle = ExecutionPlan(
        plan_id="plan-2",
        invocations=[
            SkillInvocation("step1", "research", "command1", ["step2"]),
            SkillInvocation("step2", "personal", "command2", ["step1"])
        ]
    )
    try:
        service._group_invocations_into_levels(plan_cycle.invocations)
        assert False, "Should raise cycle error"
    except ValueError as e:
        assert "Circular dependency" in str(e)


def test_parameter_substitution():
    registry = CommandRegistry()
    service = LocalOrchestratorService(registry)

    variables = {
        "step1": "Research details on event bus",
        "step2.result": "Done"
    }

    cmd = "workflow create check event bus: {step1} status: {step2.result}"
    substituted = service._substitute_parameters(cmd, variables)
    assert substituted == "workflow create check event bus: Research details on event bus status: Done"


def test_multi_skill_flows_orchestration():
    registry = CommandRegistry()
    
    # Register mock command handlers
    def mock_research(args):
        return f"Research results for: {args}"

    def mock_personal(args):
        return f"Personal summary of: {args}"

    def mock_n8n(args):
        return f"Workflow created with input: {args}"

    registry.register_command(
        CommandMetadata("research topic", "...", CommandCategory.CLI, "None", [], "usage"),
        mock_research
    )
    registry.register_command(
        CommandMetadata("profile show", "...", CommandCategory.CLI, "None", [], "usage"),
        mock_personal
    )
    registry.register_command(
        CommandMetadata("workflow create", "...", CommandCategory.CLI, "None", [], "usage"),
        mock_n8n
    )

    service = LocalOrchestratorService(registry)

    # Scenario: Research -> Personal -> n8n
    plan = ExecutionPlan(
        plan_id="multi-flow-1",
        invocations=[
            SkillInvocation("step1", "research", "research topic weather API"),
            SkillInvocation("step2", "personal", "profile show using weather API result: {step1}"),
            SkillInvocation("step3", "n8n", "workflow create deploy weather: {step2}")
        ]
    )

    ctx = ExecutionContext()
    res = service.execute_plan(plan, ctx)

    assert res["success"] is True
    assert "Step ID: step1" in res["report"]
    assert "Step ID: step3" in res["report"]
    assert res["results"]["step1"] == "Research results for: weather API"
    assert res["results"]["step2"] == "Personal summary of: using weather API result: Research results for: weather API"
    assert "Workflow created with input" in res["results"]["step3"]


def test_failure_handling_and_abort():
    registry = CommandRegistry()

    def mock_failing(args):
        raise ValueError("Simulated handler crash")

    registry.register_command(
        CommandMetadata("failing cmd", "...", CommandCategory.CLI, "None", [], "usage"),
        mock_failing
    )

    service = LocalOrchestratorService(registry)
    plan = ExecutionPlan(
        plan_id="failure-plan",
        invocations=[
            SkillInvocation("step1", "fail", "failing cmd"),
            SkillInvocation("step2", "n8n", "workflow create deploy")
        ]
    )

    ctx = ExecutionContext()
    res = service.execute_plan(plan, ctx)

    assert res["success"] is False
    assert "Simulated handler crash" in res["error"]
    assert "ERROR: Simulated handler crash" in res["partial_results"]["step1"]
    assert "step2" not in res["partial_results"]  # step2 should not have run because step1 failed
