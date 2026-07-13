import os
from unittest.mock import MagicMock

from aios.services.knowledge_hub import KnowledgeHubService
from aios.services.memory import MemoryService
from aios.services.model import LLMResponse, ModelService
from aios.services.test_generation_impl import (
    LocalAssertionGenerator,
    LocalEdgeCaseGenerator,
    LocalFixtureGenerator,
    LocalMockGenerator,
    LocalRegressionTestGenerator,
    LocalTestCaseBuilder,
    LocalTestGenerationService,
    LocalTestGenerator,
    LocalTestPatternAnalyzer,
    LocalTestTemplateEngine,
)
from aios.services.workspace_intelligence import CodeStructureSummary


def test_pattern_analyzer():
    analyzer = LocalTestPatternAnalyzer()
    res = analyzer.analyze_patterns(".")
    assert "pytest" in res


def test_template_engine():
    engine = LocalTestTemplateEngine()
    context = {
        "fixtures": "# fixtures",
        "mocks": "# mocks",
        "cases": "pass",
        "assertions": "assert True",
        "edge_cases": "# edge",
        "regression": "# regression"
    }
    code = engine.render_template("", context)
    assert "import pytest" in code
    assert "assert True" in code


def test_case_builder():
    builder = LocalTestCaseBuilder()
    cases = builder.build_cases("test obj", "patterns")
    assert len(cases) == 1
    assert "exec" in cases[0]


def test_generators():
    fixtures = LocalFixtureGenerator()
    mocks = LocalMockGenerator()
    assertions = LocalAssertionGenerator()
    edge = LocalEdgeCaseGenerator()
    regression = LocalRegressionTestGenerator()
    
    assert "@pytest.fixture" in fixtures.generate_fixtures("symbol")[0]
    assert "mock_obj" in mocks.generate_mocks("symbol")[0]
    assert "assert True" in assertions.generate_assertions("symbol")[0]
    assert "with pytest.raises" in edge.generate_edge_cases("symbol")[0]
    assert "assert 1 + 1 == 2" in regression.generate_regression_tests("symbol")[0]


def test_test_generator(tmp_path):
    generator = LocalTestGenerator()
    ws_root = str(tmp_path)
    summary = CodeStructureSummary("s1", 0.0, {}, {}, {}, {}, [])
    
    artifact = generator.generate_test_suite(ws_root, "memory.py", "patterns", summary)
    assert artifact.file_path == "core/tests/test_memory.py"
    assert os.path.exists(os.path.join(ws_root, "core/tests/test_memory.py"))
    assert artifact.checksum is not None


def test_test_generation_service_flow(tmp_path):
    mock_model = MagicMock(spec=ModelService)
    mock_memory = MagicMock(spec=MemoryService)
    mock_kh = MagicMock(spec=KnowledgeHubService)
    
    # Mock LLM Response with valid python test code
    mock_response = MagicMock(spec=LLMResponse)
    mock_response.content = "```python\ndef test_dummy():\n    assert 1 == 1\n```"
    mock_model.execute_request.return_value = mock_response

    service = LocalTestGenerationService(
        memory_service=mock_memory,
        knowledge_hub=mock_kh,
        model_service=mock_model
    )
    service.initialize()
    
    summary = CodeStructureSummary("s1", 0.0, {}, {}, {}, {}, [])
    
    report = service.generate_workspace_tests(
        workspace_id="ws_1",
        objective="Write missing test suite",
        workspace_root=str(tmp_path),
        target_files=["memory.py"],
        code_summary=summary
    )
    
    assert len(report.artifacts) == 1
    assert report.artifacts[0].file_path == "core/tests/test_memory.py"
    assert "def test_dummy():" in report.artifacts[0].content
    
    # Store
    service.store_generation_report(report)
    mock_memory.add_memory.assert_called_once()
    
    # Publish
    service.publish_generation_report(report)
    mock_kh.sync_document.assert_called_once()


def test_backward_compatibility():
    class CustomPatternAnalyzer(LocalTestPatternAnalyzer):
        def analyze_patterns(self, existing_tests_dir):
            res = super().analyze_patterns(existing_tests_dir)
            return f"{res}\nCustom pattern."
            
    analyzer = CustomPatternAnalyzer()
    assert "Custom pattern." in analyzer.analyze_patterns(".")
