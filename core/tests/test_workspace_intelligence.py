from typing import List
from unittest.mock import MagicMock

import pytest
from aios.services.knowledge_hub import KnowledgeHubService
from aios.services.memory import MemoryService
from aios.services.model import LLMResponse, ModelService
from aios.services.project_intelligence import ProjectContext, ProjectIntelligenceService
from aios.services.workspace_intelligence_impl import (
    LocalArchitectureAnalyzer,
    LocalDependencyAnalyzer,
    LocalDocumentationAnalyzer,
    LocalRepositoryAnalyzer,
    LocalTechnologyAnalyzer,
    LocalWorkspaceIntelligenceService,
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


from aios.services.workspace_intelligence import (
    LanguageASTParser,
    SymbolReference,
)
from aios.services.workspace_intelligence_impl import (
    LocalCallGraphBuilder,
    LocalCodeIntelligenceService,
    LocalDependencyGraphBuilder,
    PythonASTParser,
    TypeScriptASTParser,
)


def test_python_ast_parsing_and_symbol_extraction():
    python_code = """
import os
from math import pi, sin
from dataclasses import dataclass
from abc import ABC, abstractmethod
from enum import Enum

@dataclass
class Point:
    x: float
    y: float

class Shape(ABC):
    @abstractmethod
    def area(self) -> float:
        pass

class Color(Enum):
    RED = 1
    BLUE = 2

@my_decorator
def calculate_distance(p1: Point, p2: Point) -> float:
    return 0.0
"""
    parser = PythonASTParser()
    symbols = parser.parse("dummy.py", python_code)
    
    # Assert module symbol
    module_syms = [s for s in symbols if s.symbol_type == "module"]
    assert len(module_syms) == 1
    assert module_syms[0].name == "dummy"
    
    # Assert imports
    imports = [s for s in symbols if s.symbol_type == "import"]
    assert len(imports) == 5
    assert any(imp.name == "os" for imp in imports)
    assert any(imp.name == "math" for imp in imports)
    
    # Assert dataclass
    dataclasses = [s for s in symbols if s.symbol_type == "dataclass"]
    assert len(dataclasses) == 1
    assert dataclasses[0].name == "Point"
    
    # Assert interface ( Shape inherits from ABC )
    interfaces = [s for s in symbols if s.symbol_type == "interface"]
    assert len(interfaces) == 1
    assert interfaces[0].name == "Shape"
    
    # Assert enum
    enums = [s for s in symbols if s.symbol_type == "enum"]
    assert len(enums) == 1
    assert enums[0].name == "Color"
    
    # Assert function and decorators
    functions = [s for s in symbols if s.symbol_type == "function"]
    assert len(functions) == 1
    assert functions[0].name == "calculate_distance"
    assert "my_decorator" in functions[0].decorators


def test_typescript_ast_parsing_and_symbol_extraction():
    ts_code = """
import { Dependency } from "./dependency";
import * as fs from "fs";

@Component({ selector: 'app-root' })
@Injectable()
export class AppComponent extends BaseComponent implements OnInit {
    @Input() title: string;

    constructor() {}

    public ngOnInit(): void {
        this.runApp();
    }

    private runApp() {
        console.log("running");
    }
}

export interface MyInterface {
    name: string;
}

export enum Status {
    ACTIVE,
    INACTIVE
}

export function helperFunction() {}

export const arrowFunc = () => {
    console.log("arrow");
};
"""
    parser = TypeScriptASTParser()
    symbols = parser.parse("app.component.ts", ts_code)
    
    # Assert module symbol
    module_syms = [s for s in symbols if s.symbol_type == "module"]
    assert len(module_syms) == 1
    
    # Assert imports
    imports = [s for s in symbols if s.symbol_type == "import"]
    assert len(imports) == 2
    assert any(imp.name == "./dependency" for imp in imports)
    
    # Assert class, decorator, and inheritance
    classes = [s for s in symbols if s.symbol_type == "class"]
    assert len(classes) == 1
    assert classes[0].name == "AppComponent"
    assert classes[0].is_public is True
    assert classes[0].meta.get("extends") == "BaseComponent"
    assert "OnInit" in classes[0].meta.get("implements")
    assert "Component" in classes[0].decorators
    assert "Injectable" in classes[0].decorators
    
    # Assert methods
    methods = [s for s in symbols if s.symbol_type == "method"]
    assert len(methods) == 2
    assert any(m.name == "AppComponent.ngOnInit" for m in methods)
    assert any(m.name == "AppComponent.runApp" for m in methods)
    # Check method visibility
    ng_init = next(m for m in methods if m.name == "AppComponent.ngOnInit")
    run_app = next(m for m in methods if m.name == "AppComponent.runApp")
    assert ng_init.is_public is True
    assert run_app.is_public is False
    
    # Assert interface
    interfaces = [s for s in symbols if s.symbol_type == "interface"]
    assert len(interfaces) == 1
    assert interfaces[0].name == "MyInterface"
    assert interfaces[0].is_public is True
    
    # Assert enum
    enums = [s for s in symbols if s.symbol_type == "enum"]
    assert len(enums) == 1
    assert enums[0].name == "Status"
    
    # Assert functions
    functions = [s for s in symbols if s.symbol_type == "function"]
    assert len(functions) == 2
    assert any(f.name == "helperFunction" for f in functions)
    assert any(f.name == "arrowFunc" for f in functions)


def test_dependency_graph_builder():
    symbols = [
        SymbolReference("f1::import::f2", "f2", "import", "f1", 1, 1, meta={"module": "f2"}),
        SymbolReference("f2::import::f3", "f3", "import", "f2", 1, 1, meta={"module": "f3"}),
    ]
    builder = LocalDependencyGraphBuilder()
    graph = builder.build_graph(["f1", "f2", "f3"], symbols)
    
    assert graph["f1"] == ["f2"]
    assert graph["f2"] == ["f3"]
    assert graph["f3"] == []


def test_call_graph_builder(tmp_path):
    f1 = tmp_path / "f1.py"
    f1.write_text("def first():\n    second()\n")
    
    symbols = [
        SymbolReference("f1::first", "first", "function", str(f1), 1, 2),
        SymbolReference("f1::second", "second", "function", str(f1), 4, 5),
    ]
    
    builder = LocalCallGraphBuilder()
    graph = builder.build_call_graph(symbols)
    
    assert graph["first"] == ["second"]


def test_code_intelligence_service_integration(mock_project_intel, mock_memory_service, mock_knowledge_hub, tmp_path):
    python_file = tmp_path / "main.py"
    python_file.write_text("def hello():\n    pass\n")
    
    mock_project_intel.analyze_workspace.return_value.structure = ["main.py"]
    
    service = LocalCodeIntelligenceService(
        mock_project_intel, mock_memory_service, mock_knowledge_hub
    )
    service.initialize()
    
    # Run codebase analysis
    summary = service.analyze_codebase(str(tmp_path))
    assert f"{str(python_file)}::hello" in summary.symbols
    
    # Test memory integration
    service.store_code_summary(summary)
    mock_memory_service.add_memory.assert_called_once()
    
    # Test knowledge hub integration
    service.publish_code_report(summary)
    mock_knowledge_hub.sync_document.assert_called_once()


def test_backward_compatibility_and_future_languages():
    class GoASTParser(LanguageASTParser):
        def can_parse(self, file_extension: str) -> bool:
            return file_extension.lower() == ".go"

        def parse(self, file_path: str, content: str) -> List[SymbolReference]:
            return [
                SymbolReference(f"{file_path}::GoFunc", "GoFunc", "function", file_path, 1, 5)
            ]
            
    service = LocalCodeIntelligenceService(
        MagicMock(), MagicMock()
    )
    service._analyzer.register_parser(GoASTParser())
    
    symbols = service._analyzer.parse_file("main.go", "package main")
    assert len(symbols) == 1
    assert symbols[0].name == "GoFunc"

