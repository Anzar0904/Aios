import time
from unittest.mock import MagicMock
import pytest

from aios.registry import ServiceRegistry
from aios.services.project_intelligence import ProjectIntelligenceService, ProjectContext
from aios.services.memory import MemoryService, MemoryType
from aios.services.knowledge_hub import KnowledgeHubService
from aios.services.model import ModelService, LLMResponse
from aios.services.workspace_intelligence import (
    WorkspaceIntelligenceService,
    RepositorySummary,
    RepositoryHealth,
)
from aios.services.workspace_intelligence_impl import (
    LocalWorkspaceIntelligenceService,
    LocalRepositoryAnalyzer,
    LocalArchitectureAnalyzer,
    LocalDependencyAnalyzer,
    LocalTechnologyAnalyzer,
    LocalDocumentationAnalyzer,
)


@pytest.fixture
def mock_project_context():
    return ProjectContext(
        project_root=".",
        languages={".py": 10, ".md": 5, ".json": 2},
        frameworks=["fastapi"],
        package_managers=["poetry/pip"],
        dependencies=["pytest", "fastapi", "ruff"],
        git_branch="main",
        git_commits=["Init commit"],
        todo_markers=[],
        statistics={"total_files": 17, "total_folders": 3},
        structure=["core/src/aios/kernel.py", "docs/decision_1.md", "README.md"],
        adr_count=1,
    )


@pytest.fixture
def mock_project_intel(mock_project_context):
    service = MagicMock(spec=ProjectIntelligenceService)
    service.analyze_workspace.return_value = mock_project_context
    return service


@pytest.fixture
def mock_memory_service():
    service = MagicMock(spec=MemoryService)
    return service


@pytest.fixture
def mock_knowledge_hub():
    service = MagicMock(spec=KnowledgeHubService)
    return service


def test_repository_analyzer(mock_project_intel):
    analyzer = LocalRepositoryAnalyzer(mock_project_intel)
    res = analyzer.analyze(".")

    assert res["context"] is not None
    assert isinstance(res["cicd_workflows"], list)
    assert isinstance(res["has_docker"], bool)
    assert isinstance(res["env_files"], list)


def test_architecture_analyzer():
    # LLM test path
    model_mock = MagicMock(spec=ModelService)
    model_mock.execute_request.return_value = LLMResponse(
        content='{"high_level_architecture": "Microservices", "components": ["A", "B"], "entry_points": ["main.py"], "execution_paths": [], "design_patterns": [], "architectural_observations": []}',
        model_name="mock-model",
        provider_name="mock-provider"
    )

    context_mock = {
        "context": MagicMock(structure=["main.py"], statistics={"total_folders": 2}, languages={".py": 1}, package_managers=[])
    }

    analyzer = LocalArchitectureAnalyzer(model_mock)
    res = analyzer.analyze(".", context_mock)
    assert res["high_level_architecture"] == "Microservices"
    assert "A" in res["components"]

    # Rule-based fallback test path
    fallback_analyzer = LocalArchitectureAnalyzer(None)
    fallback_res = fallback_analyzer.analyze(".", context_mock)
    assert "Kernel" in fallback_res["components"]


def test_dependency_analyzer(mock_project_context):
    context_mock = {"context": mock_project_context}
    analyzer = LocalDependencyAnalyzer()
    res = analyzer.analyze(".", context_mock)

    assert "Kernel" in res
    assert "Orchestrator" in res


def test_technology_analyzer(mock_project_context):
    context_mock = {"context": mock_project_context}
    analyzer = LocalTechnologyAnalyzer()
    res = analyzer.analyze(".", context_mock)

    assert "Python" in res["languages"]
    assert "fastapi" in res["frameworks"]
    assert "pytest" in res["testing_frameworks"]


def test_documentation_analyzer(mock_project_context):
    context_mock = {"context": mock_project_context}
    analyzer = LocalDocumentationAnalyzer()
    res = analyzer.analyze(".", context_mock)

    assert res["doc_files_count"] == 2  # docs/decision_1.md, README.md
    assert res["readme_files_count"] == 1
    assert res["adr_count"] == 1


def test_workspace_intelligence_service(mock_project_intel, mock_memory_service, mock_knowledge_hub):
    service = LocalWorkspaceIntelligenceService(
        mock_project_intel, mock_memory_service, mock_knowledge_hub
    )
    service.initialize()

    summary = service.analyze_repository(".")
    assert summary.high_level_architecture is not None
    assert summary.health.file_count == 17
    assert summary.health.adr_count == 1

    # Assert memory storage call
    service.store_summary_in_memory(summary)
    mock_memory_service.add_memory.assert_called_once()

    # Assert Knowledge Hub publish call
    service.publish_to_knowledge_hub(summary)
    mock_knowledge_hub.sync_document.assert_called_once()
