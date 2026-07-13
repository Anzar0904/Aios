from unittest.mock import MagicMock

import pytest
from aios.services.knowledge_hub import KnowledgeHubService
from aios.services.memory import MemoryService
from aios.services.model import LLMResponse, ModelService
from aios.services.test_engineer import (
    TestCategory,
    TestStrategy,
)
from aios.services.test_engineer_impl import (
    LocalAITestEngineerService,
    LocalTestPlanner,
)
from aios.services.workspace_intelligence import CodeStructureSummary


@pytest.fixture
def mock_code_summary():
    return CodeStructureSummary(
        summary_id="s1",
        timestamp=0.0,
        symbols={},
        call_graph={},
        dependency_graph={
            "core/src/aios/kernel.py": [
                "core/src/aios/bootstrap.py",
                "core/src/aios/services/memory.py",
            ],
            "core/src/aios/services/memory.py": [],
        },
        inheritance_map={},
        public_apis=["boot"],
    )


def test_test_planner_strategy_selection(mock_code_summary):
    planner = LocalTestPlanner()

    # 1. Non-critical change
    res_std = planner.plan_tests(
        objective="Update styling guidelines",
        affected_files=["core/src/aios/services/memory.py"],
        code_summary=mock_code_summary,
    )
    assert res_std.plan.strategy == TestStrategy.STANDARD
    assert res_std.plan.scope.risk_level == "Medium"

    # 2. Critical file changes (e.g. kernel.py)
    res_crit = planner.plan_tests(
        objective="Refactor execution engine loops",
        affected_files=["core/src/aios/kernel.py"],
        code_summary=mock_code_summary,
    )
    assert res_crit.plan.strategy == TestStrategy.STRICT
    assert res_crit.plan.scope.risk_level == "High"


def test_test_planner_category_selection(mock_code_summary):
    planner = LocalTestPlanner()

    # 1. Database objective
    res_db = planner.plan_tests(
        objective="Integrate sql database storage",
        affected_files=["core/src/aios/services/memory.py"],
        code_summary=mock_code_summary,
    )
    categories = [s.category for s in res_db.plan.suites]
    assert TestCategory.DATABASE in categories
    assert TestCategory.UNIT in categories

    # 2. API routing objective
    res_api = planner.plan_tests(
        objective="Create REST api endpoints handler",
        affected_files=["core/src/aios/services/memory.py"],
        code_summary=mock_code_summary,
    )
    categories_api = [s.category for s in res_api.plan.suites]
    assert TestCategory.API in categories_api


def test_test_planner_prioritization(mock_code_summary):
    planner = LocalTestPlanner()

    res = planner.plan_tests(
        objective="Change system bootstrap config",
        affected_files=["core/src/aios/services/memory.py", "core/src/aios/kernel.py"],
        code_summary=mock_code_summary,
    )

    # kernel.py has 2 dependencies, memory.py has 0 dependencies.
    # Prioritization should rank kernel.py first.
    targets_order = res.plan.suites[0].target_files
    assert targets_order[0] == "core/src/aios/kernel.py"


def test_test_engineer_service_flow(mock_code_summary):
    mock_model = MagicMock(spec=ModelService)
    mock_memory = MagicMock(spec=MemoryService)
    mock_kh = MagicMock(spec=KnowledgeHubService)

    # Mock LLM Refinement Response
    mock_response = MagicMock(spec=LLMResponse)
    mock_response.content = (
        '{\n  "validation_checkpoints": [ "Refined checkpoint 1" ],\n  "coverage_goal": 95.0\n}'
    )
    mock_model.execute_request.return_value = mock_response

    service = LocalAITestEngineerService(
        memory_service=mock_memory, knowledge_hub=mock_kh, model_service=mock_model
    )
    service.initialize()

    result = service.generate_test_plan(
        workspace_id="ws_1",
        objective="Verify system kernel routes",
        affected_files=["core/src/aios/kernel.py"],
        code_summary=mock_code_summary,
    )

    # Checks LLM merger values
    assert "Refined checkpoint 1" in result.validation_checkpoints
    assert result.plan.scope.coverage_goal == 95.0

    # Store memory check
    service.store_test_plan(result)
    mock_memory.add_memory.assert_called_once()

    # Publish Knowledge Hub check
    service.publish_test_plan(result)
    mock_kh.sync_document.assert_called_once()


def test_backward_compatibility():
    class CustomPlanner(LocalTestPlanner):
        def plan_tests(self, objective, affected_files, code_summary):
            res = super().plan_tests(objective, affected_files, code_summary)
            res.validation_checkpoints.append("Custom validation checkpoint")
            return res

    planner = CustomPlanner()
    res = planner.plan_tests("Verify system kernel routes", [], MagicMock())
    assert "Custom validation checkpoint" in res.validation_checkpoints
