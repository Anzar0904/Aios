from unittest.mock import MagicMock

import pytest
from aios.services.architecture_documentation import (
    ArchitectureComponent,
    ArchitectureDecision,
    ArchitectureDiagram,
    ArchitectureLayer,
    ArchitectureRegistry,
    ArchitectureReport,
    ArchitectureSummary,
)
from aios.services.architecture_documentation_impl import (
    LocalArchitectureAnalyzer,
    LocalArchitectureDocumentationService,
    LocalArchitectureDocumentPlanner,
    LocalArchitectureValidator,
)
from aios.services.knowledge_hub import KnowledgeHubService
from aios.services.memory import MemoryService
from aios.services.model import LLMResponse, ModelService


@pytest.fixture
def sample_code_structure():
    return {
        "workspace_id": "ws_1",
        "dependencies": {
            "ModuleA": ["ModuleB"],
            "ModuleB": ["ModuleA"],  # Circular dependency cycle
        },
        "layers": {
            "Domain": {"level": 1, "imports": ["Infrastructure"]},
            "Infrastructure": {
                "level": 2,
                "imports": [],
            },  # Level 1 importing Level 2 is fine, but if Level 2 imports Level 1 it violates layering rules
        },
    }


def test_architecture_analyzer(sample_code_structure):
    analyzer = LocalArchitectureAnalyzer()
    report = analyzer.analyze_architecture(sample_code_structure, "")

    assert len(report.circular_dependencies) == 1
    assert "ModuleA <-> ModuleB" in report.circular_dependencies


def test_architecture_planner():
    planner = LocalArchitectureDocumentPlanner()
    report = ArchitectureReport("r1", "ws_1", [], [], [], 0.0)

    components = planner.plan_architecture_documentation(report)
    assert len(components) > 0
    assert any(c.name == "Kernel" for c in components)


def test_architecture_validator():
    validator = LocalArchitectureValidator()
    registry = ArchitectureRegistry()

    # Register components
    registry.register_component(ArchitectureComponent("A", "core", "c1"))
    registry.register_component(ArchitectureComponent("B", "core", "c2"))

    # 1. Valid diagram
    diag = ArchitectureDiagram("d1", "mermaid_flowchart", "graph TD\n    A -->|calls| B")
    errors = validator.validate_architecture_document(diag, registry)
    assert len(errors) == 0

    # 2. Invalid connection
    diag_invalid = ArchitectureDiagram("d2", "mermaid_flowchart", "graph TD\n    A -->|calls| C")
    errors_inv = validator.validate_architecture_document(diag_invalid, registry)
    assert len(errors_inv) == 1
    assert "undefined component node 'C'" in errors_inv[0]


def test_architecture_registry():
    registry = ArchitectureRegistry()
    comp = ArchitectureComponent("Kernel", "core", "composition root")
    layer = ArchitectureLayer("Domain", 1, [comp])
    decision = ArchitectureDecision("adr_1", "Use SQLite", "accepted", "context description")

    registry.register_component(comp)
    registry.register_layer(layer)
    registry.register_decision(decision)

    assert registry.get_component("Kernel") == comp
    assert registry.get_layer("Domain") == layer
    assert registry.get_decision("adr_1") == decision


def test_service_evaluation_flow(sample_code_structure):
    mock_memory = MagicMock(spec=MemoryService)
    mock_kh = MagicMock(spec=KnowledgeHubService)
    mock_model = MagicMock(spec=ModelService)

    # Mock LLM Response
    mock_response = MagicMock(spec=LLMResponse)
    mock_response.content = "graph TD\n    Kernel --> ServiceRegistry"
    mock_model.execute_request.return_value = mock_response

    service = LocalArchitectureDocumentationService(
        memory_service=mock_memory, knowledge_hub=mock_kh, model_service=mock_model
    )
    service.initialize()

    diag = service.generate_architecture_documentation("ws_1", sample_code_structure, "")
    assert "Kernel --> ServiceRegistry" in diag.content

    # Store
    summary = ArchitectureSummary("s1", 1, 3, 1, 0.0)
    service.store_architecture_summary(summary)
    mock_memory.add_memory.assert_called_once()

    # Publish
    report = ArchitectureReport("r1", "ws_1", [], [], [], 0.0)
    service.publish_architecture_report(report)
    mock_kh.sync_document.assert_called_once()


def test_backward_compatibility():
    class CustomPlanner(LocalArchitectureDocumentPlanner):
        def plan_architecture_documentation(self, report):
            components = super().plan_architecture_documentation(report)
            components.append(ArchitectureComponent("Custom", "extra", "custom node"))
            return components

    planner = CustomPlanner()
    components = planner.plan_architecture_documentation(MagicMock())
    assert any(c.name == "Custom" for c in components)
