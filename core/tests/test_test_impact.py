from unittest.mock import MagicMock

import pytest
from aios.services.knowledge_hub import KnowledgeHubService
from aios.services.memory import MemoryService
from aios.services.model import LLMResponse, ModelService
from aios.services.test_impact_impl import LocalChangeImpactAnalyzer
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


def test_impact_graph_generation(mock_code_summary):
    analyzer = LocalChangeImpactAnalyzer(memory_service=MagicMock())

    result = analyzer.analyze_change_impact(
        workspace_id="ws_1",
        objective="Modify kernel loader",
        affected_files=["core/src/aios/kernel.py"],
        code_summary=mock_code_summary,
    )

    # Check impact nodes and edges
    assert len(result.impact_graph.nodes) == 3  # kernel.py + bootstrap.py + memory.py
    assert result.impact_graph.nodes["core/src/aios/kernel.py"].is_modified
    assert not result.impact_graph.nodes["core/src/aios/bootstrap.py"].is_modified
    assert len(result.impact_graph.edges) == 2


def test_affected_modules_suites_detection(mock_code_summary):
    analyzer = LocalChangeImpactAnalyzer(memory_service=MagicMock())

    result = analyzer.analyze_change_impact(
        workspace_id="ws_1",
        objective="Update bootstrap configuration",
        affected_files=["core/src/aios/bootstrap.py"],
        code_summary=mock_code_summary,
    )

    # Verify components and suites
    assert len(result.affected_components) == 1
    assert result.affected_components[0].name == "bootstrap.py"

    assert len(result.affected_suites) == 1
    assert result.affected_suites[0].suite_name == "test_bootstrap.py"
    assert result.affected_suites[0].run_required


def test_regression_candidates(mock_code_summary):
    analyzer = LocalChangeImpactAnalyzer(memory_service=MagicMock())

    result = analyzer.analyze_change_impact(
        workspace_id="ws_1",
        objective="Alter core logic flow",
        affected_files=["core/src/aios/services/memory.py"],
        code_summary=mock_code_summary,
    )

    # Indirect dependency checks: memory.py is imported by kernel.py.
    # Therefore, when memory.py changes, kernel.py is flagged as a regression candidate.
    assert len(result.regression_candidates) == 1
    assert result.regression_candidates[0].file_path == "core/src/aios/kernel.py"


def test_risk_assessment(mock_code_summary):
    analyzer = LocalChangeImpactAnalyzer(memory_service=MagicMock())

    # 1. Non-critical risk
    res_std = analyzer.analyze_change_impact(
        "ws_1", "Update documentation", ["core/src/aios/services/memory.py"], mock_code_summary
    )
    assert res_std.risk_assessment.overall_risk == "Medium"

    # 2. Critical file changes risk (kernel.py)
    res_crit = analyzer.analyze_change_impact(
        "ws_1", "Alter boot sequence", ["core/src/aios/kernel.py"], mock_code_summary
    )
    assert res_crit.risk_assessment.overall_risk == "High"


def test_coverage_targets(mock_code_summary):
    analyzer = LocalChangeImpactAnalyzer(memory_service=MagicMock())

    result = analyzer.analyze_change_impact(
        "ws_1", "Optimize code", ["core/src/aios/services/memory.py"], mock_code_summary
    )
    assert len(result.coverage_targets) == 1
    assert result.coverage_targets[0].statement_coverage >= 80.0
    assert result.coverage_targets[0].branch_coverage >= 75.0


def test_service_integrations(mock_code_summary):
    mock_model = MagicMock(spec=ModelService)
    mock_memory = MagicMock(spec=MemoryService)
    mock_kh = MagicMock(spec=KnowledgeHubService)

    # Mock LLM response
    mock_response = MagicMock(spec=LLMResponse)
    mock_response.content = '{\n  "overall_risk": "High",\n  "dep_chain_risk": "High",\n  "statement_coverage_target": 95.0\n}'
    mock_model.execute_request.return_value = mock_response

    analyzer = LocalChangeImpactAnalyzer(
        memory_service=mock_memory, knowledge_hub=mock_kh, model_service=mock_model
    )
    analyzer.initialize()

    result = analyzer.analyze_change_impact(
        workspace_id="ws_1",
        objective="Alter core boot sequence",
        affected_files=["core/src/aios/kernel.py"],
        code_summary=mock_code_summary,
    )

    # Checks LLM refinement values
    assert result.risk_assessment.overall_risk == "High"
    assert result.risk_assessment.dep_chain_risk == "High"
    assert result.coverage_targets[0].statement_coverage == 95.0

    # Store
    analyzer.store_impact_result(result)
    mock_memory.add_memory.assert_called_once()

    # Publish
    analyzer.publish_impact_report(result)
    mock_kh.sync_document.assert_called_once()


def test_backward_compatibility():
    class CustomAnalyzer(LocalChangeImpactAnalyzer):
        def analyze_change_impact(self, workspace_id, objective, affected_files, code_summary):
            res = super().analyze_change_impact(
                workspace_id, objective, affected_files, code_summary
            )
            res.risk_assessment.overall_risk = "Critical"
            return res

    analyzer = CustomAnalyzer(memory_service=MagicMock())
    res = analyzer.analyze_change_impact("ws_1", "Optimize", [], MagicMock())
    assert res.risk_assessment.overall_risk == "Critical"
