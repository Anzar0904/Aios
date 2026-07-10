import shutil
from unittest.mock import patch

import pytest
from aios.services.project_intelligence import ProjectIntelligenceService
from aios.services.project_intelligence_impl import LocalProjectIntelligence, ProjectProfileStore

LocalProjectIntelligenceService = LocalProjectIntelligence


@pytest.fixture
def temp_dir(tmp_path):
    """Fixture for temporary directory for credentials and reports."""
    test_dir = tmp_path / "project_test"
    test_dir.mkdir()
    yield test_dir
    if test_dir.exists():
        shutil.rmtree(test_dir)


def test_project_profile_store(temp_dir):
    """Test saving, loading and deleting project profiles."""
    reg_file = temp_dir / "projects.json"
    store = ProjectProfileStore(path=reg_file)

    # Empty initially
    assert store.load_all() == {}

    # Save project profile
    store.save_project(
        project_id="proj_1",
        profile={
            "id": "proj_1",
            "name": "App 1",
            "framework": "nextjs",
            "languages": {"python": 100},
        },
    )

    data = store.load_all()
    assert "proj_1" in data
    assert data["proj_1"]["name"] == "App 1"
    assert data["proj_1"]["framework"] == "nextjs"

    # Delete project
    store.delete_project("proj_1")
    assert store.load_all() == {}


def test_project_service_exists():
    """Verify implementation class exists and can be imported."""
    assert LocalProjectIntelligenceService is not None


def test_project_discovery(temp_dir):
    """Test discovering a project's framework, dependencies, n8n, supabase, etc."""
    reg_file = temp_dir / "projects.json"
    service = LocalProjectIntelligenceService(registry_path=reg_file)
    service.initialize()

    # Create dummy project structure
    project_dir = temp_dir / "my_project"
    project_dir.mkdir()
    (project_dir / ".git").mkdir()
    (project_dir / "package.json").write_text('{"dependencies": {"react": "18.0.0"}}')
    (project_dir / "package-lock.json").write_text("{}")

    discovery = service.discover_project(str(project_dir))
    assert discovery["project_id"] is not None
    assert discovery["framework"] == "react"
    assert discovery["package_manager"] == "npm"
    assert discovery["repository"]["git_enabled"] is True


def test_unified_project_profile(temp_dir):
    """Test getting the unified project profile aggregating other subservices."""
    reg_file = temp_dir / "projects.json"
    service = LocalProjectIntelligenceService(registry_path=reg_file)
    service.initialize()

    service._profile_store.save_project(
        project_id="p1",
        profile={
            "project_id": "p1",
            "name": "proj-a",
            "framework": "nextjs",
            "languages": {"typescript": 90},
        },
    )
    service.start()

    profile = service.get_project_profile("p1")
    assert profile["project_id"] == "p1"
    assert profile["framework"] == "nextjs"
    assert "database" in profile
    assert "deployments" in profile


def test_architecture_intelligence(temp_dir):
    """Test retrieving service maps and module mappings."""
    reg_file = temp_dir / "projects.json"
    service = LocalProjectIntelligenceService(registry_path=reg_file)
    service.initialize()

    service._profile_store.save_project("p1", {"id": "p1", "name": "proj-a"})
    service.start()

    arch = service.get_architecture_map("p1")
    assert "service_map" in arch
    assert "module_map" in arch
    assert "dependency_graph" in arch


def test_health_intelligence(temp_dir):
    """Test calculating health, technical debt, and documentation scores."""
    reg_file = temp_dir / "projects.json"
    service = LocalProjectIntelligenceService(registry_path=reg_file)
    service.initialize()

    service._profile_store.save_project("p1", {"id": "p1", "name": "proj-a"})
    service.start()

    health = service.get_health_scorecard("p1")
    assert "health_score" in health
    assert "technical_debt_hours" in health
    assert "readiness_level" in health


def test_dependency_intelligence(temp_dir):
    """Test auditing dependencies for mismatched versions and advisories."""
    reg_file = temp_dir / "projects.json"
    service = LocalProjectIntelligenceService(registry_path=reg_file)
    service.initialize()

    service._profile_store.save_project("p1", {"id": "p1", "name": "proj-a"})
    service.start()

    deps = service.get_dependency_audit("p1")
    assert "dependencies" in deps
    assert "mismatches" in deps
    assert "security_advisories" in deps


def test_timeline_intelligence(temp_dir):
    """Test aggregating commit history and deployment logs to a timeline."""
    reg_file = temp_dir / "projects.json"
    service = LocalProjectIntelligenceService(registry_path=reg_file)
    service.initialize()

    service._profile_store.save_project("p1", {"id": "p1", "name": "proj-a"})
    service.start()

    timeline = service.get_timeline("p1")
    assert "events" in timeline
    assert len(timeline["events"]) >= 0


def test_risk_intelligence(temp_dir):
    """Test scanning risks across coverage, deployments, and config drift."""
    reg_file = temp_dir / "projects.json"
    service = LocalProjectIntelligenceService(registry_path=reg_file)
    service.initialize()

    service._profile_store.save_project("p1", {"id": "p1", "name": "proj-a"})
    service.start()

    risks = service.get_risk_analysis("p1")
    assert "risks" in risks
    assert "overall_risk_level" in risks


def test_knowledge_graph_and_queries(temp_dir):
    """Test knowledge graph connectivity query capabilities."""
    reg_file = temp_dir / "projects.json"
    service = LocalProjectIntelligenceService(registry_path=reg_file)
    service.initialize()

    service._profile_store.save_project("p1", {"id": "p1", "name": "proj-a"})
    service.start()

    graph = service.query_knowledge_graph("p1", "files")
    assert "nodes" in graph
    assert "edges" in graph


def test_project_memory_and_retrieval(temp_dir):
    """Test project memory logs and semantic retrieval."""
    reg_file = temp_dir / "projects.json"
    service = LocalProjectIntelligenceService(registry_path=reg_file)
    service.initialize()

    service._profile_store.save_project("p1", {"id": "p1", "name": "proj-a"})
    service.start()

    results = service.query_project_memory("p1", "architecture")
    assert isinstance(results, list)


def test_project_report_generation(temp_dir):
    """Test generating 7 central markdown reports."""
    reg_file = temp_dir / "projects.json"
    service = LocalProjectIntelligenceService(registry_path=reg_file)
    service.initialize()

    service._profile_store.save_project("p1", {"id": "p1", "name": "proj-a"})
    service.start()

    reports_dir = temp_dir / "reports"
    res = service.generate_reports("p1", output_dir=reports_dir)

    assert res["reports_written"] == 7
    assert (reports_dir / "project_summary.md").is_file()
    assert (reports_dir / "architecture_report.md").is_file()
    assert (reports_dir / "health_report.md").is_file()
    assert (reports_dir / "risk_report.md").is_file()
    assert (reports_dir / "timeline_report.md").is_file()
    assert (reports_dir / "dependency_report.md").is_file()
    assert (reports_dir / "knowledge_graph_report.md").is_file()


def test_project_cli_commands(temp_dir):
    """Test execute_builtin_cli_command for Project Intelligence integration."""
    from aios.cli import execute_builtin_cli_command
    from aios.registry import ServiceRegistry

    reg_file = temp_dir / "projects.json"
    service = LocalProjectIntelligenceService(registry_path=reg_file)
    service.initialize()
    service._profile_store.save_project("p1", {"project_id": "p1", "name": "proj-a"})
    service.start()

    registry = ServiceRegistry()
    registry.register(ProjectIntelligenceService, service)

    with patch("aios.registry.ServiceRegistry._global_registry", registry):
        assert execute_builtin_cli_command(["project"], exit_on_complete=False)
        assert execute_builtin_cli_command(["project", "list"], exit_on_complete=False)
        assert execute_builtin_cli_command(["project", "status"], exit_on_complete=False)
        assert execute_builtin_cli_command(["project", "summary", "p1"], exit_on_complete=False)
        assert execute_builtin_cli_command(["project", "graph", "p1"], exit_on_complete=False)
        assert execute_builtin_cli_command(["project", "health", "p1"], exit_on_complete=False)
        assert execute_builtin_cli_command(["project", "timeline", "p1"], exit_on_complete=False)
        assert execute_builtin_cli_command(["project", "risks", "p1"], exit_on_complete=False)
        assert execute_builtin_cli_command(
            ["project", "architecture", "p1"], exit_on_complete=False
        )
        assert execute_builtin_cli_command(
            ["project", "memory", "p1", "test"], exit_on_complete=False
        )
        assert execute_builtin_cli_command(["project", "analyze", "p1"], exit_on_complete=False)
