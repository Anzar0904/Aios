import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

from aios.brain.context_manager import ContextManager
from aios.services.context import WorkspaceContext
from aios.services.project_intelligence import ProjectContext
from aios.services.project_intelligence_impl import LocalProjectIntelligence


def test_project_intelligence_analysis():
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace_root = Path(tmpdir)

        # Create files
        (workspace_root / "src").mkdir()
        (workspace_root / "src" / "main.py").write_text(
            "print('Hello')\n# TODO: Implement user feedback\n# FIXME: Resolve bug",
            encoding="utf-8"
        )
        (workspace_root / "src" / "utils.js").write_text(
            "console.log('Util')\n// TODO: Add support for CORS",
            encoding="utf-8"
        )
        # Ignored directory file
        (workspace_root / "node_modules").mkdir()
        (workspace_root / "node_modules" / "ignored.js").write_text("console.log('Ignored')", encoding="utf-8")

        # Config files
        pyproject_content = """
[project]
name = "test_project"
dependencies = [
    "fastapi",
    "pytest"
]
"""
        (workspace_root / "pyproject.toml").write_text(pyproject_content, encoding="utf-8")

        pkg_json_content = """
{
  "dependencies": {
    "react": "^18.0.0"
  }
}
"""
        (workspace_root / "package.json").write_text(pkg_json_content, encoding="utf-8")

        # Run analysis
        service = LocalProjectIntelligence(cache_filename=".test_intel_cache.json")
        context = service.analyze_workspace(str(workspace_root))

        assert isinstance(context, ProjectContext)
        assert context.languages == {".py": 1, ".js": 1, ".toml": 1, ".json": 1}
        assert "npm/yarn" in context.package_managers
        assert "poetry/pip" in context.package_managers
        assert "react" in context.frameworks or "fastapi" in context.frameworks
        
        # Verify TODOs
        assert len(context.todo_markers) == 3
        todo_texts = [t["text"] for t in context.todo_markers]
        assert "# TODO: Implement user feedback" in todo_texts
        assert "# FIXME: Resolve bug" in todo_texts
        assert "// TODO: Add support for CORS" in todo_texts

        # Ignored directories should not be parsed
        todo_files = [t["file"] for t in context.todo_markers]
        assert not any("node_modules" in f for f in todo_files)


def test_incremental_indexing():
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace_root = Path(tmpdir)
        main_py = workspace_root / "main.py"
        main_py.write_text("print('test')\n# TODO: original", encoding="utf-8")

        service = LocalProjectIntelligence(cache_filename=".test_intel_cache.json")

        # First scan
        context1 = service.analyze_workspace(str(workspace_root))
        assert len(context1.todo_markers) == 1
        assert context1.todo_markers[0]["text"] == "# TODO: original"

        # Rescan - file has not changed, should hit cache
        context2 = service.analyze_workspace(str(workspace_root))
        assert len(context2.todo_markers) == 1
        assert context2.todo_markers[0]["text"] == "# TODO: original"

        # Mutate file and timestamp
        main_py.write_text("print('updated')\n# TODO: updated_todo", encoding="utf-8")
        # Ensure st_mtime shifts
        mtime = main_py.stat().st_mtime
        main_py.stat() # reload cache

        # Third scan - cache miss because file content and timestamp changed
        context3 = service.analyze_workspace(str(workspace_root))
        assert len(context3.todo_markers) == 1
        assert context3.todo_markers[0]["text"] == "# TODO: updated_todo"


def test_brain_context_manager_integration():
    context_service = MagicMock()
    memory_service = MagicMock()
    project_intel = MagicMock()

    workspace_ctx = WorkspaceContext(
        working_directory="/tmp/test_workspace",
        git_repo_path="/tmp/test_workspace/.git",
        git_branch="main",
        project_root="/tmp/test_workspace",
        project_name="test_proj"
    )
    context_service.get_current_context.return_value = workspace_ctx
    memory_service.search_memory.return_value = []

    mock_proj_context = ProjectContext(
        project_root="/tmp/test_workspace",
        languages={".py": 5},
        git_branch="main"
    )
    project_intel.analyze_workspace.return_value = mock_proj_context

    manager = ContextManager(context_service, memory_service, project_intel)
    assembled = manager.assemble_context("explain architecture")

    assert assembled.project_name == "test_proj"
    # Unified project context object must be present in extra
    assert assembled.extra.get("project_intelligence") == mock_proj_context
    project_intel.analyze_workspace.assert_called_once_with("/tmp/test_workspace")
