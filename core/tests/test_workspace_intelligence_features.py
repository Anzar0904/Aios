import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from aios.cli import execute_builtin_cli_command
from aios.services.developer_workspace import DeveloperWorkspaceInfo, DeveloperWorkspaceService
from aios.services.memory import MemoryService
from aios.services.project_intelligence import ProjectContext
from aios.services.workspace_intelligence import (
    CodeIntelligenceService,
    FileMetadata,
    SymbolReference,
    WorkspaceContext,
    WorkspaceIntelligenceService,
)
from aios.services.workspace_intelligence_impl import (
    LocalCodeIntelligenceService,
    LocalTechnologyAnalyzer,
    LocalWorkspaceIntelligenceService,
    classify_architecture,
    detect_coding_conventions,
    detect_project_boundary,
    find_all_workspaces,
    load_aiosignore_rules,
)


@pytest.fixture
def temp_project_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        # Create a mock project structure
        (tmp_path / ".git").mkdir()
        (tmp_path / "pyproject.toml").write_text(
            "[tool.poetry]\nname='test_project'\ndependencies={fastapi='*'}", encoding="utf-8"
        )

        # Sub-workspace 1
        sub1 = tmp_path / "packages" / "sub1"
        sub1.mkdir(parents=True)
        (sub1 / "package.json").write_text(
            '{"name": "sub1", "dependencies": {"react": "*"}}', encoding="utf-8"
        )

        # Sub-workspace 2
        sub2 = tmp_path / "packages" / "sub2"
        sub2.mkdir(parents=True)
        (sub2 / "Cargo.toml").write_text("[package]\nname = 'sub2'", encoding="utf-8")

        # Ignored venv
        (tmp_path / ".venv").mkdir()
        (tmp_path / ".venv" / "pyproject.toml").write_text("[tool.poetry]", encoding="utf-8")

        # Source files
        src = tmp_path / "src"
        src.mkdir()
        (src / "service.py").write_text("class MyService:\n    pass\n", encoding="utf-8")
        (src / "controller.py").write_text("class MyController:\n    pass\n", encoding="utf-8")
        (src / "db.py").write_text("import sqlite3\n", encoding="utf-8")

        # Test file
        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()
        (tests_dir / "test_main.py").write_text("def test_service():\n    pass\n", encoding="utf-8")

        yield tmp_path


def test_project_boundary_detection(temp_project_dir):
    sub_path = temp_project_dir / "packages" / "sub1"
    boundary = detect_project_boundary(str(sub_path))
    assert Path(boundary).resolve() == Path(temp_project_dir).resolve()


def test_find_all_workspaces(temp_project_dir):
    ignores = {".git", ".venv"}
    workspaces = find_all_workspaces(str(temp_project_dir), ignores)
    assert "." in workspaces or "packages/sub1" in workspaces or "packages/sub2" in workspaces
    assert ".venv" not in workspaces


def test_load_aiosignore_rules(temp_project_dir):
    (temp_project_dir / ".aiosignore").write_text("*.log\n/dist/\n", encoding="utf-8")
    rules = load_aiosignore_rules(temp_project_dir)
    assert "*.log" in rules
    assert "/dist/" in rules


def test_classify_architecture(temp_project_dir):
    structure = ["src/service.py", "src/controller.py", "src/db.py", "pyproject.toml"]
    arch_map = classify_architecture(str(temp_project_dir), structure)
    assert "src/service.py" in arch_map["services"]
    assert "src/controller.py" in arch_map["controllers"]
    assert "src/db.py" in arch_map["database_layer"]
    assert "pyproject.toml" in arch_map["configuration"]


def test_detect_coding_conventions():
    symbols = [
        SymbolReference("f::MyClass", "MyClass", "class", "f.py", 1, 5),
        SymbolReference("f::helper_func", "helper_func", "function", "f.py", 7, 10),
    ]
    convs = detect_coding_conventions(symbols)
    assert convs["class_naming"] == "PascalCase"
    assert convs["function_naming"] == "snake_case"


def test_technology_analyzer():
    analyzer = LocalTechnologyAnalyzer()
    proj_context = {
        "context": MagicMock(
            languages={".py": 5, ".js": 2},
            frameworks=["fastapi"],
            package_managers=["poetry/pip"],
            dependencies=["fastapi", "pytest"],
            structure=["pyproject.toml", "package.json", "Dockerfile"],
        )
    }
    res = analyzer.analyze(".", proj_context)
    assert "Python" in res["languages"]
    assert "JavaScript/TypeScript" in res["languages"]
    assert any("fastapi" in f.lower() for f in res["frameworks"])
    assert "Docker" in res["deployment_configs"]
    assert "poetry/pip" in res["package_managers"]


def test_circular_dependency_detection():
    dep_graph = {"f1.py": ["f2.py"], "f2.py": ["f3.py"], "f3.py": ["f1.py"], "f4.py": []}

    visited = {}
    path = []
    circular_deps = []

    def detect_cycle(node):
        visited[node] = 1
        path.append(node)
        for neighbor in dep_graph.get(node, []):
            if visited.get(neighbor) == 1:
                cycle_start = path.index(neighbor)
                cycle = path[cycle_start:] + [node]
                circular_deps.append(cycle)
            elif neighbor not in visited:
                detect_cycle(neighbor)
        path.pop()
        visited[node] = 2

    for node in dep_graph:
        if node not in visited:
            detect_cycle(node)

    assert len(circular_deps) == 1


def test_workspace_context_generation(temp_project_dir):
    project_intel = MagicMock()
    project_intel.analyze_workspace.return_value = ProjectContext(
        project_root=str(temp_project_dir),
        languages={".py": 3},
        frameworks=["fastapi"],
        package_managers=["poetry/pip"],
        dependencies=["fastapi"],
        statistics={"total_files": 4, "total_folders": 2},
        structure=["src/service.py", "pyproject.toml"],
    )

    memory_service = MagicMock(spec=MemoryService)
    registry = MagicMock()

    code_intel = MagicMock(spec=LocalCodeIntelligenceService)
    code_intel.analyze_codebase.return_value = MagicMock()
    code_intel._indexer = MagicMock()
    code_intel._indexer.list_symbols.return_value = []
    code_intel.get_file_metadata.return_value = FileMetadata(
        file_path="src/service.py",
        language="Python",
        module="src.service",
        extension=".py",
        size=100,
        purpose="source",
    )
    code_intel.list_all_files_metadata.return_value = []

    registry.get.return_value = code_intel

    service = LocalWorkspaceIntelligenceService(project_intel, memory_service, registry=registry)

    ctx = service.get_workspace_context(str(temp_project_dir))
    assert isinstance(ctx, WorkspaceContext)
    assert ctx.project_type == "monorepo"


@patch("sys.exit")
def test_cli_workspace_subcommands(mock_exit, temp_project_dir):
    from aios.registry import ServiceRegistry

    project_intel = MagicMock()
    project_intel.analyze_workspace.return_value = ProjectContext(
        project_root=str(temp_project_dir),
        languages={".py": 3},
        frameworks=["fastapi"],
        package_managers=["poetry/pip"],
        dependencies=["fastapi"],
        statistics={"total_files": 4, "total_folders": 2},
        structure=["src/service.py", "pyproject.toml"],
    )

    memory_service = MagicMock(spec=MemoryService)
    registry = ServiceRegistry()

    dev_ws = MagicMock(spec=DeveloperWorkspaceService)
    dev_ws.get_workspace_info.return_value = DeveloperWorkspaceInfo(
        git_status="",
        git_diff_summary="",
        staged_files=[],
        unstaged_files=[],
        untracked_files=[],
        detected_tests=[],
        build_systems=["poetry"],
        linters=["ruff"],
        diagnostics={},
    )

    code_intel = MagicMock(spec=CodeIntelligenceService)
    code_intel.analyze_codebase.return_value = MagicMock(dependency_graph={})
    code_intel.list_all_files_metadata.return_value = []

    service = LocalWorkspaceIntelligenceService(project_intel, memory_service, registry=registry)

    registry.register(WorkspaceIntelligenceService, service)
    registry.register(DeveloperWorkspaceService, dev_ws)
    registry.register(CodeIntelligenceService, code_intel)

    # Temporarily set global registry
    ServiceRegistry._global_registry = registry

    res = execute_builtin_cli_command(["workspace", "scan"], exit_on_complete=False)
    assert res is True

    res = execute_builtin_cli_command(["workspace", "summary"], exit_on_complete=False)
    assert res is True

    res = execute_builtin_cli_command(["workspace", "status"], exit_on_complete=False)
    assert res is True

    res = execute_builtin_cli_command(["workspace", "refresh"], exit_on_complete=False)
    assert res is True
