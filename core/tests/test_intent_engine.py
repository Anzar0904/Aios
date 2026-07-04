import json
from unittest.mock import MagicMock, patch
import pytest

from aios.registry import ServiceRegistry
from aios.services.memory import MemoryService, Memory, MemoryType, MemoryMetadata, RetrievalContext
from aios.services.reasoning import ReasoningService, ReasoningContext, ReasoningResult
from aios.services.model import ModelService, LLMResponse
from aios.services.intent_engine import IntentEngine, IntentPlan, IntentContext
from aios.services.intent_engine_impl import (
    LocalIntentEngine,
    LocalIntentClassifier,
    LocalIntentAnalyzer,
    LocalIntentResolver,
)


@pytest.fixture
def mock_memory_service():
    service = MagicMock(spec=MemoryService)
    retriever = MagicMock()

    # Mock some memories
    mock_meta = MemoryMetadata(workspace_id="ws_1", session_id="sess_1")
    memories = [
        Memory(
            memory_id="mem_1",
            content="User prefers coding in Python.",
            memory_type=MemoryType.USER_PREFERENCE,
            metadata=mock_meta,
            created_at=0.0,
            updated_at=0.0
        )
    ]
    retriever.retrieve.return_value = memories
    service.retriever = retriever
    return service


@pytest.fixture
def mock_reasoning_service():
    service = MagicMock(spec=ReasoningService)
    res = ReasoningResult(
        success=True,
        plan={"plan_id": "rplan_123", "tasks": []},
        self_critique={"safety_status": "safe"}
    )
    service.reason.return_value = res
    return service


def test_intent_classification_rule_based():
    classifier = LocalIntentClassifier()

    # Multi-intent Example 1
    text1 = "I want to apply for Google's AI internship and prepare for the interview."
    cats1 = classifier.classify(text1)
    assert "Career" in cats1  # Matches apply, internship, interview

    # Example 2
    text2 = "Find local AI startups and add them to my Notion workspace."
    cats2 = classifier.classify(text2)
    assert "Research" in cats2  # Matches find
    assert "Knowledge" in cats2  # Matches notion
    assert "Project" in cats2  # Matches workspace


def test_intent_classification_llm():
    model_mock = MagicMock(spec=ModelService)
    model_mock.execute_request.return_value = LLMResponse(
        content=json.dumps(["Career", "Research", "GitHub"]),
        model_name="mock-model",
        provider_name="mock-provider"
    )

    classifier = LocalIntentClassifier(model_mock)
    cats = classifier.classify("I want to apply for a job and research open source repos on github")
    assert "Career" in cats
    assert "Research" in cats
    assert "Github" in cats


def test_service_composition_and_order():
    classifier = LocalIntentClassifier()
    analyzer = LocalIntentAnalyzer()
    resolver = LocalIntentResolver(classifier, analyzer)

    context = IntentContext(memories=["Memory snippet 1"])
    text = "Tailor my resume for internship and write a research report and sync it to notion."

    plan = resolver.resolve_plan(text, context)

    assert plan.objective == text
    assert "CareerOSService" in plan.participating_services
    assert "ResearchService" in plan.participating_services
    assert "KnowledgeHubService" in plan.participating_services
    assert "MemoryService" in plan.participating_services

    # Assert execution order priorities: Memory first, Knowledge Hub last
    exec_order = plan.execution_order
    assert exec_order[0] == "MemoryService"
    assert exec_order[-1] == "KnowledgeHubService"

    # Assert dependencies exist for services in order
    assert len(plan.dependencies) > 0
    assert "KnowledgeHubService" in plan.dependencies


def test_intent_engine_process_objective(mock_memory_service, mock_reasoning_service):
    engine = LocalIntentEngine(mock_memory_service, mock_reasoning_service)
    engine.initialize()

    text = "Write a research summary and sync it to Notion"
    res = engine.process_objective(text)

    assert res.success is True
    assert res.plan is not None
    assert "ResearchService" in res.plan.participating_services
    assert "KnowledgeHubService" in res.plan.participating_services

    # Assert Memory Retriever was called
    mock_memory_service.retriever.retrieve.assert_called_once()

    # Assert Reasoning Service was called
    mock_reasoning_service.reason.assert_called_once()


def test_intent_engine_reasoning_rejection(mock_memory_service, mock_reasoning_service):
    # Mock reasoning rejection
    mock_reasoning_service.reason.return_value = ReasoningResult(
        success=False,
        plan={},
        self_critique={"safety_status": "unsafe"}
    )

    engine = LocalIntentEngine(mock_memory_service, mock_reasoning_service)
    res = engine.process_objective("Delete all files in active repo and wipe memories")

    assert res.success is False
    assert "Reasoning evaluation rejected the plan" in res.error_message


def test_intent_engine_registry_wiring(mock_memory_service, mock_reasoning_service):
    registry = ServiceRegistry()
    registry.register(MemoryService, mock_memory_service)
    registry.register(ReasoningService, mock_reasoning_service)

    engine = LocalIntentEngine(mock_memory_service, mock_reasoning_service)
    registry.register(IntentEngine, engine)

    retrieved = registry.get(IntentEngine)
    assert retrieved == engine
