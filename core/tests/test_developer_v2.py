from aios.services.developer.builder import PromptBuilder
from aios.services.developer.index import CodeIndex
from aios.services.developer.scanner import RepositoryScanner
from aios.services.developer.summary import WorkspaceSummary


def test_repository_scanner(tmp_path):
    # Setup mock project files
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").write_text("print('hello')")
    (tmp_path / "README.md").write_text("# Test Project")
    (tmp_path / "pyproject.toml").write_text("""
[tool.poetry.dependencies]
fastapi = "^0.100.0"
""")

    scanner = RepositoryScanner(str(tmp_path))
    results = scanner.scan()

    assert results["project_name"] == tmp_path.name
    # Since relative_to returns relative string config paths
    assert "pyproject.toml" in results["config_files"]
    assert "Python" in results["languages"]
    assert "FastAPI" in results["frameworks"]
    assert results["package_manager"] == "pip / poetry"


def test_code_index(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "entry.py").write_text("TODO: fix this later")
    (tmp_path / "large.txt").write_text("x" * 500)
    (tmp_path / "larger.txt").write_text("y" * 1000)

    index = CodeIndex(str(tmp_path))
    results = index.index()

    assert "src" in results["source_directories"]
    assert any(todo["comment"] == ": fix this later" for todo in results["todos"])
    assert results["largest_files"][0]["path"] == "larger.txt"


def test_workspace_summary_generation():
    scan_results = {
        "project_name": "test_proj",
        "repository_root": "/test",
        "readme": "README content",
        "languages": ["Python"],
        "frameworks": ["Django"],
        "package_manager": "pip",
        "git_branch": "main",
        "git_status": "clean",
        "last_commits": ["commit1"],
        "test_framework": "pytest",
    }
    index_results = {
        "source_directories": ["src"],
        "test_directories": ["tests"],
        "entry_points": ["src/main.py"],
        "configuration_files": ["pyproject.toml"],
        "todos": [{"type": "TODO", "comment": "hello"}],
    }

    summary = WorkspaceSummary(scan_results, index_results)
    workspace_summary = summary.generate()

    assert workspace_summary["Project"]["name"] == "test_proj"
    assert "Python" in workspace_summary["Languages"]
    assert workspace_summary["Git Status"]["branch"] == "main"
    assert workspace_summary["Open TODOs"][0]["comment"] == "hello"


def test_prompt_builder(tmp_path):
    templates_dir = tmp_path / "prompts" / "developer"
    templates_dir.mkdir(parents=True)
    template_file = templates_dir / "analyze_repository.md"
    template_file.write_text("Project: {project}\nIntent: {intent_action}")

    workspace_summary = {
        "Project": {"name": "test_proj"},
        "Languages": ["Python"],
        "Frameworks": [],
        "Architecture": {},
        "Modules": [],
        "Dependencies": {},
        "Tests": {},
        "Git Status": {},
        "Recent Activity": [],
        "Open TODOs": [],
    }

    builder = PromptBuilder(str(templates_dir))
    prompt = builder.build_prompt(
        template_name="analyze_repository",
        workspace_summary=workspace_summary,
        intent_action="AnalyzeRepository",
        intent_parameters={},
        memories=[],
    )

    assert "Project:" in prompt
    assert "AnalyzeRepository" in prompt
