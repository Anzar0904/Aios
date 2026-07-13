import shutil
from unittest.mock import patch

import pytest
from aios.services.business import BusinessDataStore

try:
    from aios.services.business_impl import LocalBusinessIntelligenceService
except ImportError:
    LocalBusinessIntelligenceService = None


@pytest.fixture
def temp_dir(tmp_path):
    """Fixture for temporary directory for business stores and reports."""
    test_dir = tmp_path / "business_test"
    test_dir.mkdir()
    yield test_dir
    if test_dir.exists():
        shutil.rmtree(test_dir)


def test_business_data_store(temp_dir):
    """Test saving, loading and deleting entries in secure store."""
    store_file = temp_dir / "clients.json"
    store = BusinessDataStore("clients.json", path=store_file)

    # Empty initially
    assert store.load_all() == {}

    # Save entry
    store.save_entry("client_1", {"name": "Acme Corp", "status": "active"})
    data = store.load_all()
    assert "client_1" in data
    assert data["client_1"]["name"] == "Acme Corp"

    # Delete entry
    store.delete_entry("client_1")
    assert store.load_all() == {}


def test_business_service_exists():
    """Verify implementation class exists."""
    assert LocalBusinessIntelligenceService is not None


def test_organization_management(temp_dir):
    """Test creating and listing organizations."""
    service = LocalBusinessIntelligenceService(base_dir=temp_dir)
    service.initialize()
    service.start()

    service.save_organization("org_1", {"name": "AI Agency", "members": []})
    orgs = service.list_organizations()
    assert len(orgs) == 1
    assert orgs[0]["name"] == "AI Agency"


def test_client_and_leads_management(temp_dir):
    """Test client and lead registrations."""
    service = LocalBusinessIntelligenceService(base_dir=temp_dir)
    service.initialize()
    service.start()

    service.save_client("c1", {"name": "John Doe", "email": "john@example.com"})
    service.save_lead("l1", {"name": "Prospective Lead", "score": 90})

    clients = service.list_clients()
    leads = service.list_leads()
    assert len(clients) == 1
    assert clients[0]["name"] == "John Doe"
    assert len(leads) == 1
    assert leads[0]["score"] == 90


def test_project_portfolio_integration(temp_dir):
    """Test listing portfolio projects linking to Project Intelligence."""
    service = LocalBusinessIntelligenceService(base_dir=temp_dir)
    service.initialize()
    service.start()

    projects = service.list_projects()
    assert isinstance(projects, list)


def test_proposal_management(temp_dir):
    """Test proposal creation and versioning."""
    service = LocalBusinessIntelligenceService(base_dir=temp_dir)
    service.initialize()
    service.start()

    service.save_proposal("prop_1", {"title": "AI Integration Proposal", "budget": 5000})
    proposal = service.get_proposal("prop_1")
    assert proposal["budget"] == 5000


def test_workflow_and_task_tracking(temp_dir):
    """Test client workflow ownership and milestone tracking."""
    service = LocalBusinessIntelligenceService(base_dir=temp_dir)
    service.initialize()
    service.start()

    workflows = service.list_workflows()
    tasks = service.list_tasks()
    assert isinstance(workflows, list)
    assert isinstance(tasks, list)


def test_business_analytics(temp_dir):
    """Test business metrics calculation."""
    service = LocalBusinessIntelligenceService(base_dir=temp_dir)
    service.initialize()
    service.start()

    analytics = service.get_analytics()
    assert "active_clients" in analytics
    assert "success_rate" in analytics
    assert "revenue_estimate" in analytics


def test_client_timeline(temp_dir):
    """Test client meeting and deploy history timelines."""
    service = LocalBusinessIntelligenceService(base_dir=temp_dir)
    service.initialize()
    service.start()

    timeline = service.get_client_timeline("c1")
    assert "events" in timeline


def test_business_report_generation(temp_dir):
    """Test writing 6 operations markdown reports."""
    service = LocalBusinessIntelligenceService(base_dir=temp_dir)
    service.initialize()
    service.start()

    reports_dir = temp_dir / "reports"
    res = service.generate_reports(output_dir=reports_dir)

    assert res["reports_written"] == 6
    assert (reports_dir / "client_report.md").is_file()
    assert (reports_dir / "organization_report.md").is_file()
    assert (reports_dir / "project_portfolio.md").is_file()
    assert (reports_dir / "proposal_report.md").is_file()
    assert (reports_dir / "workflow_ownership_report.md").is_file()
    assert (reports_dir / "analytics_report.md").is_file()


def test_business_cli_commands(temp_dir):
    """Test execute_builtin_cli_command for Business Intelligence integration."""
    from aios.cli import execute_builtin_cli_command
    from aios.registry import ServiceRegistry
    from aios.services.business import BusinessIntelligenceService

    service = LocalBusinessIntelligenceService(base_dir=temp_dir)
    service.initialize()
    service.save_client("c1", {"name": "John Doe"})
    service.save_proposal("p1", {"title": "Prop 1"})
    service.start()

    registry = ServiceRegistry()
    registry.register(BusinessIntelligenceService, service)

    with patch("aios.registry.ServiceRegistry._global_registry", registry):
        assert execute_builtin_cli_command(["business"], exit_on_complete=False)
        assert execute_builtin_cli_command(["business", "organizations"], exit_on_complete=False)
        assert execute_builtin_cli_command(["business", "clients"], exit_on_complete=False)
        assert execute_builtin_cli_command(["business", "leads"], exit_on_complete=False)
        assert execute_builtin_cli_command(["business", "projects"], exit_on_complete=False)
        assert execute_builtin_cli_command(["business", "proposals"], exit_on_complete=False)
        assert execute_builtin_cli_command(["business", "workflows"], exit_on_complete=False)
        assert execute_builtin_cli_command(["business", "tasks"], exit_on_complete=False)
        assert execute_builtin_cli_command(["business", "analytics"], exit_on_complete=False)
        assert execute_builtin_cli_command(["business", "timeline", "c1"], exit_on_complete=False)
        assert execute_builtin_cli_command(["business", "summary"], exit_on_complete=False)
