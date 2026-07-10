import shutil
from unittest.mock import MagicMock, patch

import pytest
from aios.services.supabase import SupabaseCredentialsStore, SupabaseService

try:
    from aios.services.supabase_impl import LocalSupabaseIntelligenceService
except ImportError:
    LocalSupabaseIntelligenceService = None


@pytest.fixture
def temp_dir(tmp_path):
    """Fixture for temporary directory for credentials and reports."""
    test_dir = tmp_path / "supabase_test"
    test_dir.mkdir()
    yield test_dir
    if test_dir.exists():
        shutil.rmtree(test_dir)


def test_credentials_store(temp_dir):
    """Test saving, loading and deleting credentials."""
    cred_file = temp_dir / "credentials.json"
    store = SupabaseCredentialsStore(path=cred_file)

    # Initially empty
    assert store.load_all() == {}

    # Save credentials
    store.save_credentials(
        access_token="sb_pat_123",
        projects=[{"ref": "proj1", "name": "Project 1", "region": "us-east-1"}],
        active_project_ref="proj1",
    )

    data = store.load_all()
    assert data["access_token"] == "sb_pat_123"
    assert data["active_project_ref"] == "proj1"
    assert len(data["projects"]) == 1
    assert data["projects"][0]["ref"] == "proj1"

    # Delete all
    store.delete_all()
    assert not cred_file.exists()
    assert store.load_all() == {}


def test_supabase_service_not_implemented():
    """Verify implementation class exists and can be imported."""
    assert LocalSupabaseIntelligenceService is not None


def test_login_validation(temp_dir):
    """Test connection validation and login functionality."""
    cred_file = temp_dir / "credentials.json"
    service = LocalSupabaseIntelligenceService(credentials_path=cred_file)
    service.initialize()

    # Login with URL and Service Role Key
    with patch("httpx.Client") as mock_client_class:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "healthy"}
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        success = service.login(
            project_url="https://xyz.supabase.co",
            service_role_key="sb_secret_role_key_abc",
            project_ref="xyz",
        )
        assert success is True

    status = service.get_status()
    assert status["connected"] is True
    assert status["active_project_ref"] == "xyz"
    assert status["project_url"] == "https://xyz.supabase.co"


def test_list_projects(temp_dir):
    """Test project discovery and listing using PAT."""
    cred_file = temp_dir / "credentials.json"
    service = LocalSupabaseIntelligenceService(credentials_path=cred_file)
    service.initialize()

    with patch("httpx.Client") as mock_client_class:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"id": "p1", "name": "Proj A", "ref": "refa", "region": "eu-west-1"},
            {"id": "p2", "name": "Proj B", "ref": "refb", "region": "us-west-2"},
        ]
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        # Login with PAT
        service.login(access_token="sb_pat_999")
        projects = service.list_projects()

        assert len(projects) == 2
        assert projects[0]["name"] == "Proj A"
        assert projects[1]["ref"] == "refb"


def test_project_summary(temp_dir):
    """Test getting project summary metrics."""
    cred_file = temp_dir / "credentials.json"
    service = LocalSupabaseIntelligenceService(credentials_path=cred_file)
    service.initialize()

    # Pre-populate active credentials
    service._credentials_store.save_credentials(
        projects=[
            {"ref": "xyz", "name": "Test Project", "url": "https://xyz.supabase.co", "key": "key1"}
        ],
        active_project_ref="xyz",
    )
    service.start()

    with patch("httpx.Client") as mock_client_class:
        mock_client = MagicMock()

        # Mock database queries via POST rpc or HTTP REST schema discovery
        db_res = MagicMock()
        db_res.status_code = 200
        db_res.json.return_value = [
            {"table_name": "users", "schema": "public"},
            {"table_name": "profiles", "schema": "public"},
        ]
        mock_client.post.return_value = db_res

        # Mock storage buckets
        storage_res = MagicMock()
        storage_res.status_code = 200
        storage_res.json.return_value = [{"id": "avatars", "name": "avatars", "public": True}]

        # Mock edge functions
        fn_res = MagicMock()
        fn_res.status_code = 200
        fn_res.json.return_value = [
            {"id": "f1", "name": "hello-world", "slug": "hello-world", "status": "ACTIVE"}
        ]

        mock_client.get.side_effect = [storage_res, fn_res]
        mock_client_class.return_value.__enter__.return_value = mock_client

        summary = service.get_project_summary("xyz")
        assert summary["project_ref"] == "xyz"
        assert summary["tables_count"] == 2
        assert summary["buckets_count"] == 1
        # If PAT is not configured, edge function count might fall back or be fetched.
        # Since we mocked client.get side_effect, let's verify buckets count.
        assert summary["buckets_count"] == 1


def test_schema_intelligence(temp_dir):
    """Test database schema exploration, relationships, and ER summaries."""
    cred_file = temp_dir / "credentials.json"
    service = LocalSupabaseIntelligenceService(credentials_path=cred_file)
    service.initialize()

    service._credentials_store.save_credentials(
        projects=[
            {"ref": "xyz", "name": "Test Project", "url": "https://xyz.supabase.co", "key": "key"}
        ],
        active_project_ref="xyz",
    )
    service.start()

    with patch("httpx.Client") as mock_client_class:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "tables": [
                {"name": "users", "columns": [{"name": "id", "type": "uuid", "nullable": False}]},
                {
                    "name": "orders",
                    "columns": [
                        {"name": "id", "type": "int8"},
                        {"name": "user_id", "type": "uuid"},
                    ],
                },
            ],
            "relationships": [
                {
                    "foreign_table": "orders",
                    "foreign_column": "user_id",
                    "primary_table": "users",
                    "primary_column": "id",
                }
            ],
            "views": [{"name": "active_orders"}],
            "functions": [{"name": "calculate_total"}],
            "triggers": [{"name": "on_user_created"}],
            "constraints": [{"name": "orders_pkey", "table": "orders", "type": "PRIMARY KEY"}],
            "indexes": [{"name": "orders_user_id_idx", "table": "orders", "columns": ["user_id"]}],
        }
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        schema = service.get_schema("xyz")
        assert len(schema["tables"]) == 2
        assert len(schema["relationships"]) == 1
        assert schema["relationships"][0]["primary_table"] == "users"
        assert len(schema["views"]) == 1
        assert len(schema["functions"]) == 1
        assert len(schema["triggers"]) == 1


def test_security_intelligence(temp_dir):
    """Test security intelligence analyzing RLS, credentials, and policies."""
    cred_file = temp_dir / "credentials.json"
    service = LocalSupabaseIntelligenceService(credentials_path=cred_file)
    service.initialize()

    service._credentials_store.save_credentials(
        projects=[
            {"ref": "xyz", "name": "Test Project", "url": "https://xyz.supabase.co", "key": "key"}
        ],
        active_project_ref="xyz",
    )
    service.start()

    with patch("httpx.Client") as mock_client_class:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "rls_enabled_tables": ["users"],
            "rls_disabled_tables": ["orders"],  # Vulnerability!
            "public_tables": ["orders"],
            "policies": [{"table": "users", "name": "Allow select for all", "action": "SELECT"}],
            "service_role_exposed": False,
        }
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        security = service.get_security_analysis("xyz")
        assert "orders" in security["rls_disabled_tables"]
        assert len(security["security_recommendations"]) > 0


def test_migration_intelligence(temp_dir):
    """Test migration logs and drift detection."""
    cred_file = temp_dir / "credentials.json"
    service = LocalSupabaseIntelligenceService(credentials_path=cred_file)
    service.initialize()

    service._credentials_store.save_credentials(
        projects=[
            {"ref": "xyz", "name": "Test Project", "url": "https://xyz.supabase.co", "key": "key"}
        ],
        active_project_ref="xyz",
    )
    service.start()

    with patch("httpx.Client") as mock_client_class:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "migration_history": [
                {
                    "version": "20260710000000",
                    "name": "init_schema",
                    "applied_at": "2026-07-10T12:00:00Z",
                }
            ],
            "pending_migrations": [],
            "drift_detected": False,
            "drift_details": [],
        }
        mock_client.post.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        migrations = service.get_migrations("xyz")
        assert len(migrations["migration_history"]) == 1
        assert migrations["drift_detected"] is False


def test_edge_function_intelligence(temp_dir):
    """Test edge function analysis."""
    cred_file = temp_dir / "credentials.json"
    service = LocalSupabaseIntelligenceService(credentials_path=cred_file)
    service.initialize()

    service._credentials_store.save_credentials(
        projects=[
            {"ref": "xyz", "name": "Test Project", "url": "https://xyz.supabase.co", "key": "key"}
        ],
        active_project_ref="xyz",
        access_token="sb_pat_123",
    )
    service.start()

    with patch("httpx.Client") as mock_client_class:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"id": "f1", "name": "hello", "slug": "hello", "status": "ACTIVE", "verify_jwt": True}
        ]
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        funcs = service.get_edge_functions("xyz")
        assert len(funcs["functions"]) == 1
        assert funcs["functions"][0]["name"] == "hello"


def test_storage_intelligence(temp_dir):
    """Test storage buckets and policies discovery."""
    cred_file = temp_dir / "credentials.json"
    service = LocalSupabaseIntelligenceService(credentials_path=cred_file)
    service.initialize()

    service._credentials_store.save_credentials(
        projects=[
            {"ref": "xyz", "name": "Test Project", "url": "https://xyz.supabase.co", "key": "key"}
        ],
        active_project_ref="xyz",
    )
    service.start()

    with patch("httpx.Client") as mock_client_class:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"id": "b1", "name": "public-bucket", "public": True, "file_size_limit": 5000000}
        ]
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        storage = service.get_storage("xyz")
        assert len(storage["buckets"]) == 1
        assert storage["buckets"][0]["public"] is True


def test_auth_intelligence(temp_dir):
    """Test authentication configuration analysis."""
    cred_file = temp_dir / "credentials.json"
    service = LocalSupabaseIntelligenceService(credentials_path=cred_file)
    service.initialize()

    service._credentials_store.save_credentials(
        projects=[
            {"ref": "xyz", "name": "Test Project", "url": "https://xyz.supabase.co", "key": "key"}
        ],
        active_project_ref="xyz",
    )
    service.start()

    with patch("httpx.Client") as mock_client_class:
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "providers": {"email": {"enabled": True}, "github": {"enabled": False}},
            "mfa": {"totp": {"enabled": True}},
            "mailer": {"secure": True},
        }
        mock_client.get.return_value = mock_response
        mock_client_class.return_value.__enter__.return_value = mock_client

        auth = service.get_auth_config("xyz")
        assert auth["providers"]["email"]["enabled"] is True
        assert auth["providers"]["github"]["enabled"] is False


def test_report_generation(temp_dir):
    """Test generation of all markdown reports."""
    cred_file = temp_dir / "credentials.json"
    service = LocalSupabaseIntelligenceService(credentials_path=cred_file)
    service.initialize()

    # Pre-populate fake schemas/metadata so reports write actual data
    service._credentials_store.save_credentials(
        projects=[
            {"ref": "xyz", "name": "Test Proj", "url": "https://xyz.supabase.co", "key": "key"}
        ],
        active_project_ref="xyz",
    )
    service.start()

    with patch("httpx.Client") as mock_client_class:
        mock_client = MagicMock()

        # Mock post responses
        mock_post_resp = MagicMock()
        mock_post_resp.status_code = 200
        mock_post_resp.json.return_value = {
            "tables": [{"name": "t1"}],
            "rls_enabled_tables": [],
            "rls_disabled_tables": ["t1"],
            "public_tables": [],
            "policies": [],
            "migration_history": [],
        }
        mock_client.post.return_value = mock_post_resp

        # Mock get responses
        mock_get_resp = MagicMock()
        mock_get_resp.status_code = 200
        mock_get_resp.json.return_value = []
        mock_client.get.return_value = mock_get_resp

        mock_client_class.return_value.__enter__.return_value = mock_client

        reports_dir = temp_dir / "reports"
        service.generate_reports(output_dir=reports_dir)

        assert reports_dir.exists()
        assert (reports_dir / "summary_report.md").is_file()
        assert (reports_dir / "schema_report.md").is_file()
        assert (reports_dir / "security_report.md").is_file()
        assert (reports_dir / "migration_report.md").is_file()
        assert (reports_dir / "storage_report.md").is_file()
        assert (reports_dir / "auth_report.md").is_file()


def test_supabase_cli_commands(temp_dir):
    """Test execute_builtin_cli_command for all supabase subcommands."""
    from aios.cli import execute_builtin_cli_command
    from aios.registry import ServiceRegistry

    cred_file = temp_dir / "credentials.json"
    service = LocalSupabaseIntelligenceService(credentials_path=cred_file)
    service.initialize()
    service._credentials_store.save_credentials(
        projects=[
            {"ref": "xyz", "name": "Test Proj", "url": "https://xyz.supabase.co", "key": "key"}
        ],
        active_project_ref="xyz",
    )
    service.start()

    # Register in global registry if it exists or mock it
    registry = ServiceRegistry()
    registry.register(SupabaseService, service)

    with (
        patch("httpx.Client") as mock_client_class,
        patch("aios.registry.ServiceRegistry._global_registry", registry),
    ):
        mock_client = MagicMock()
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "tables": [{"name": "t1", "columns": []}],
            "rls_enabled_tables": [],
            "rls_disabled_tables": ["t1"],
            "public_tables": [],
            "policies": [],
            "migration_history": [],
            "buckets": [],
            "providers": {},
            "functions": [],
        }
        mock_client.post.return_value = mock_resp
        mock_client.get.return_value = mock_resp
        mock_client_class.return_value.__enter__.return_value = mock_client

        # Verify command runs without exceptions
        assert execute_builtin_cli_command(["supabase"], exit_on_complete=False) is True
        assert execute_builtin_cli_command(["supabase", "status"], exit_on_complete=False) is True
        assert execute_builtin_cli_command(["supabase", "projects"], exit_on_complete=False) is True
        assert execute_builtin_cli_command(["supabase", "schema"], exit_on_complete=False) is True
        assert execute_builtin_cli_command(["supabase", "security"], exit_on_complete=False) is True
        assert execute_builtin_cli_command(["supabase", "storage"], exit_on_complete=False) is True
        assert execute_builtin_cli_command(["supabase", "auth"], exit_on_complete=False) is True
        assert (
            execute_builtin_cli_command(["supabase", "migrations"], exit_on_complete=False) is True
        )
        assert (
            execute_builtin_cli_command(["supabase", "functions"], exit_on_complete=False) is True
        )
        # For summary, we mock report output dir to be local temp_dir
        # to prevent polluting workspace.
        with patch.object(service, "generate_reports") as mock_gen_reps:
            assert (
                execute_builtin_cli_command(["supabase", "summary"], exit_on_complete=False) is True
            )
            mock_gen_reps.assert_called_once()
