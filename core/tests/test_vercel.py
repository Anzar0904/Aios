import shutil
from unittest.mock import MagicMock, patch

import pytest
from aios.services.vercel import VercelCredentialsStore, VercelService

try:
    from aios.services.vercel_impl import LocalVercelIntelligenceService
except ImportError:
    LocalVercelIntelligenceService = None


@pytest.fixture
def temp_dir(tmp_path):
    """Fixture for temporary directory for credentials and reports."""
    test_dir = tmp_path / "vercel_test"
    test_dir.mkdir()
    yield test_dir
    if test_dir.exists():
        shutil.rmtree(test_dir)


def test_credentials_store(temp_dir):
    """Test saving, loading and deleting credentials."""
    cred_file = temp_dir / "credentials.json"
    store = VercelCredentialsStore(path=cred_file)

    # Initially empty
    assert store.load_all() == {}

    # Save credentials
    store.save_credentials(
        access_token="vc_token_123",
        team_id="team_abc",
        active_project_id="proj_1",
        projects=[{"id": "proj_1", "name": "project-one"}],
        teams=[{"id": "team_abc", "name": "Team Alpha"}],
    )

    data = store.load_all()
    assert data["access_token"] == "vc_token_123"
    assert data["team_id"] == "team_abc"
    assert data["active_project_id"] == "proj_1"
    assert len(data["projects"]) == 1
    assert data["projects"][0]["name"] == "project-one"

    # Delete all
    store.delete_all()
    assert not cred_file.exists()
    assert store.load_all() == {}


def test_vercel_service_not_implemented():
    """Verify implementation class exists and can be imported."""
    assert LocalVercelIntelligenceService is not None


def test_login_validation(temp_dir):
    """Test connection validation and login functionality."""
    cred_file = temp_dir / "credentials.json"
    service = LocalVercelIntelligenceService(credentials_path=cred_file)
    service.initialize()

    with patch("httpx.Client") as mock_client_class:
        mock_client = MagicMock()

        # Mock team list response (shows login is successful)
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"teams": [{"id": "t1", "name": "Team 1"}]}
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        success = service.login(access_token="vc_token_123", team_id="t1")
        assert success is True

    status = service.get_status()
    assert status["connected"] is True
    assert status["team_id"] == "t1"


def test_list_projects(temp_dir):
    """Test listing discovered projects."""
    cred_file = temp_dir / "credentials.json"
    service = LocalVercelIntelligenceService(credentials_path=cred_file)
    service.initialize()

    with patch("httpx.Client") as mock_client_class:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "projects": [
                {"id": "p1", "name": "proj-a", "framework": "nextjs"},
                {"id": "p2", "name": "proj-b", "framework": "vite"},
            ]
        }
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        service.login(access_token="vc_token")
        projects = service.list_projects()

        assert len(projects) == 2
        assert projects[0]["name"] == "proj-a"
        assert projects[1]["framework"] == "vite"


def test_project_summary(temp_dir):
    """Test getting project settings and summary metrics."""
    cred_file = temp_dir / "credentials.json"
    service = LocalVercelIntelligenceService(credentials_path=cred_file)
    service.initialize()

    service._credentials_store.save_credentials(
        projects=[{"id": "p1", "name": "proj-a", "framework": "nextjs"}], active_project_id="p1"
    )
    service.start()

    with patch("httpx.Client") as mock_client_class:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "p1",
            "name": "proj-a",
            "framework": "nextjs",
            "targets": {"production": {"url": "proj-a.vercel.app"}},
            "link": {"orgId": "team_1"},
        }
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        summary = service.get_project_summary("p1")
        assert summary["project_id"] == "p1"
        assert summary["framework"] == "nextjs"
        assert summary["production_url"] == "proj-a.vercel.app"


def test_deployments_list(temp_dir):
    """Test retrieving deployments list."""
    cred_file = temp_dir / "credentials.json"
    service = LocalVercelIntelligenceService(credentials_path=cred_file)
    service.initialize()

    service._credentials_store.save_credentials(
        projects=[{"id": "p1", "name": "proj-a"}], active_project_id="p1"
    )
    service.start()

    with patch("httpx.Client") as mock_client_class:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "deployments": [
                {"uid": "d1", "url": "d1.vercel.app", "state": "READY", "created": 1718000000000}
            ]
        }
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        deps = service.get_deployments("p1")
        assert len(deps["deployments"]) == 1
        assert deps["deployments"][0]["uid"] == "d1"
        assert deps["deployments"][0]["state"] == "READY"


def test_build_intelligence(temp_dir):
    """Test build failure analysis and logs."""
    cred_file = temp_dir / "credentials.json"
    service = LocalVercelIntelligenceService(credentials_path=cred_file)
    service.initialize()

    service._credentials_store.save_credentials(
        projects=[{"id": "p1", "name": "proj-a"}], active_project_id="p1"
    )
    service.start()

    with patch("httpx.Client") as mock_client_class:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        # Mock Vercel build events response
        mock_response.json.return_value = {
            "lines": [{"message": "Error: Cannot find module 'react'"}, {"message": "Build failed"}]
        }
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        analysis = service.get_build_analysis("d1")
        assert "react" in analysis["error_log_summary"]
        assert len(analysis["explanation"]) > 0


def test_domain_intelligence(temp_dir):
    """Test Custom domains and DNS verification."""
    cred_file = temp_dir / "credentials.json"
    service = LocalVercelIntelligenceService(credentials_path=cred_file)
    service.initialize()

    service._credentials_store.save_credentials(
        projects=[{"id": "p1", "name": "proj-a"}], active_project_id="p1"
    )
    service.start()

    with patch("httpx.Client") as mock_client_class:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "domains": [{"name": "example.com", "verified": True, "verificationRecord": None}]
        }
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        domains = service.get_domains("p1")
        assert len(domains["domains"]) == 1
        assert domains["domains"][0]["verified"] is True


def test_environment_intelligence(temp_dir):
    """Test environment variable metadata handling."""
    cred_file = temp_dir / "credentials.json"
    service = LocalVercelIntelligenceService(credentials_path=cred_file)
    service.initialize()

    service._credentials_store.save_credentials(
        projects=[{"id": "p1", "name": "proj-a"}], active_project_id="p1"
    )
    service.start()

    with patch("httpx.Client") as mock_client_class:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "envs": [{"id": "e1", "key": "DATABASE_URL", "target": ["production"]}]
        }
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        envs = service.get_environments("p1")
        assert len(envs["variables"]) == 1
        assert envs["variables"][0]["key"] == "DATABASE_URL"
        # Verify secret values are not exposed in metadata
        assert "value" not in envs["variables"][0]


def test_monitoring_and_health(temp_dir):
    """Test generating project activity and monitoring health metrics."""
    cred_file = temp_dir / "credentials.json"
    service = LocalVercelIntelligenceService(credentials_path=cred_file)
    service.initialize()

    service._credentials_store.save_credentials(
        projects=[{"id": "p1", "name": "proj-a"}], active_project_id="p1"
    )
    service.start()

    with patch("httpx.Client") as mock_client_class:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "deployments": [
                {"uid": "d1", "state": "READY", "created": 1718000000000},
                {"uid": "d2", "state": "ERROR", "created": 1718100000000},
            ]
        }
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        monitoring = service.get_monitoring_data("p1")
        assert monitoring["deployment_success_rate"] == 50.0
        assert monitoring["total_deployments"] == 2
        assert monitoring["health_status"] == "DEGRADED"


def test_report_generation(temp_dir):
    """Test Vercel reports generation."""
    cred_file = temp_dir / "credentials.json"
    service = LocalVercelIntelligenceService(credentials_path=cred_file)
    service.initialize()

    service._credentials_store.save_credentials(
        projects=[{"id": "p1", "name": "proj-a", "framework": "nextjs"}], active_project_id="p1"
    )
    service.start()

    with patch("httpx.Client") as mock_client_class:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "p1",
            "name": "proj-a",
            "framework": "nextjs",
            "targets": {"production": {"url": "proj-a.vercel.app"}},
            "deployments": [],
            "domains": [],
            "envs": [],
            "lines": [],
        }
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        reports_dir = temp_dir / "reports"
        service.generate_reports(output_dir=reports_dir)

        assert reports_dir.exists()
        assert (reports_dir / "deployment_report.md").is_file()
        assert (reports_dir / "build_report.md").is_file()
        assert (reports_dir / "domain_report.md").is_file()
        assert (reports_dir / "environment_report.md").is_file()
        assert (reports_dir / "health_report.md").is_file()


def test_vercel_cli_commands(temp_dir):
    """Test execute_builtin_cli_command for Vercel integration."""
    from aios.cli import execute_builtin_cli_command
    from aios.registry import ServiceRegistry

    cred_file = temp_dir / "credentials.json"
    service = LocalVercelIntelligenceService(credentials_path=cred_file)
    service.initialize()
    service._credentials_store.save_credentials(
        projects=[{"id": "p1", "name": "proj-a"}], active_project_id="p1"
    )
    service.start()

    registry = ServiceRegistry()
    registry.register(VercelService, service)

    with (
        patch("httpx.Client") as mock_client_class,
        patch("aios.registry.ServiceRegistry._global_registry", registry),
    ):
        mock_client = MagicMock()
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "teams": [],
            "projects": [],
            "deployments": [],
            "domains": [],
            "envs": [],
            "lines": [],
        }
        mock_client.get.return_value = mock_resp
        mock_client_class.return_value.__enter__.return_value = mock_client

        # Verify command runs without exceptions
        assert execute_builtin_cli_command(["vercel"], exit_on_complete=False)
        assert execute_builtin_cli_command(["vercel", "status"], exit_on_complete=False)
        assert execute_builtin_cli_command(["vercel", "projects"], exit_on_complete=False)
        assert execute_builtin_cli_command(["vercel", "deployments"], exit_on_complete=False)
        assert execute_builtin_cli_command(["vercel", "logs", "d1"], exit_on_complete=False)
        assert execute_builtin_cli_command(["vercel", "domains"], exit_on_complete=False)
        assert execute_builtin_cli_command(["vercel", "env"], exit_on_complete=False)

        # For summary, we mock generate_reports to avoid writing in actual workspace
        with patch.object(service, "generate_reports") as mock_gen_reps:
            assert execute_builtin_cli_command(["vercel", "summary"], exit_on_complete=False)
            mock_gen_reps.assert_called_once()
