from aios.services.reasoning import (
    ReasoningContext,
    ReasoningStep,
    ReasoningStrategy,
)
from aios.services.reasoning_impl import (
    LocalReasoningCritic,
    LocalReasoningEvaluator,
    LocalReasoningService,
)


def test_strategy_keyword_routing():
    service = LocalReasoningService()

    # 1. Engineering strategy matching
    assert (
        service._select_strategy("Refactor the Event Bus module") == ReasoningStrategy.ENGINEERING
    )

    # 2. Research strategy matching
    assert (
        service._select_strategy("Find active academic papers on LLM agents")
        == ReasoningStrategy.RESEARCH
    )

    # 3. Career strategy matching
    assert (
        service._select_strategy("Compare my resume against senior developer jobs")
        == ReasoningStrategy.CAREER
    )

    # 4. Automation strategy matching
    assert (
        service._select_strategy("Deploy a custom webhook workflow on n8n")
        == ReasoningStrategy.AUTOMATION
    )

    # 5. Learning strategy matching
    assert service._select_strategy("Study Kubernetes clusters") == ReasoningStrategy.LEARNING


def test_evaluator_safety_and_complexity():
    evaluator = LocalReasoningEvaluator()

    # Safe plan
    plan_safe = {"tasks": [{"command": "career jobs"}, {"command": "n8n workflow validate"}]}
    report_safe = evaluator.evaluate(plan_safe, ReasoningStrategy.HYBRID)
    assert report_safe["safety_status"] == "safe"
    assert report_safe["completeness_score"] == 1.0

    # Unsafe plan
    plan_unsafe = {"tasks": [{"command": "rm -rf docs/"}, {"command": "sudo apt update"}]}
    report_unsafe = evaluator.evaluate(plan_unsafe, ReasoningStrategy.HYBRID)
    assert report_unsafe["safety_status"] == "unsafe"


def test_self_critique():
    critic = LocalReasoningCritic()
    context = ReasoningContext()

    # Safe brief thought
    step_brief = ReasoningStep(step_id="s1", thought="Draft letter")
    critique_brief = critic.critique(step_brief, context)
    assert "thought is brief" in critique_brief

    # Unsafe thought
    step_unsafe = ReasoningStep(step_id="s2", thought="Delete historical CV versions using rm")
    critique_unsafe = critic.critique(step_unsafe, context)
    assert "mentions file deletions" in critique_unsafe


def test_reasoning_session_and_execution():
    service = LocalReasoningService()
    session = service.create_session("I want an AI internship")

    assert session.session_id.startswith("rsession_")
    assert session.objective == "I want an AI internship"

    ctx = ReasoningContext()
    result = service.reason("I want an AI internship", ctx)

    assert result.success is True
    assert result.strategy == ReasoningStrategy.CAREER
    assert len(result.plan["tasks"]) == 2
    assert result.chain is not None
    assert len(result.chain.steps) == 1
    assert "safety_status" in result.self_critique
