from unittest.mock import MagicMock, patch

import httpx
from aios.cli import execute_builtin_cli_command
from aios.n8n.connection import N8NLiveConnectionManager


def test_n8n_connection_load_save(tmp_path):
    """Verify loading and saving n8n connection state."""
    state_file = tmp_path / "connection_state.json"
    with patch("aios.n8n.connection.STATE_FILE", state_file):
        mgr = N8NLiveConnectionManager()

        # Initial default state
        state = mgr.load_state()
        assert state["connected"] is False
        assert state["host"] == "localhost"

        # Save new state
        new_state = {
            "host": "127.0.0.1",
            "port": 5678,
            "url": "http://127.0.0.1:5678",
            "auth_type": "api_key",
            "last_connected": 100.0,
            "connected": True,
        }
        mgr.save_state(new_state)

        loaded = mgr.load_state()
        assert loaded["connected"] is True
        assert loaded["auth_type"] == "api_key"


@patch("httpx.get")
def test_n8n_connection_discover(mock_get):
    """Verify auto-discovery checks local endpoints."""
    # Set up mock response
    mock_resp = MagicMock(spec=httpx.Response)
    mock_resp.status_code = 200
    mock_get.return_value = mock_resp

    mgr = N8NLiveConnectionManager()
    discovered = mgr.discover_instances(ports=[5678])

    assert len(discovered) > 0
    assert "http://localhost:5678" in discovered or "http://127.0.0.1:5678" in discovered


@patch("httpx.get")
def test_n8n_connection_connect_success(mock_get, tmp_path):
    """Verify connection succeeds and persists status when endpoint responds."""
    state_file = tmp_path / "connection_state.json"
    with patch("aios.n8n.connection.STATE_FILE", state_file):
        mock_resp = MagicMock(spec=httpx.Response)
        mock_resp.status_code = 200
        mock_get.return_value = mock_resp

        mgr = N8NLiveConnectionManager()
        res = mgr.connect("http://localhost:5678")

        assert res["success"] is True
        assert res["state"]["connected"] is True


def test_n8n_connection_disconnect(tmp_path):
    """Verify disconnect clears cached state details."""
    state_file = tmp_path / "connection_state.json"
    with patch("aios.n8n.connection.STATE_FILE", state_file):
        mgr = N8NLiveConnectionManager()
        mgr.disconnect()

        state = mgr.load_state()
        assert state["connected"] is False
        assert state["url"] == ""


def test_n8n_connection_reports(tmp_path):
    """Verify report markdown file output creation."""
    state_file = tmp_path / "connection_state.json"
    report_dir = tmp_path / "docs" / "n8n"

    with patch("aios.n8n.connection.STATE_FILE", state_file):
        mgr = N8NLiveConnectionManager()
        mgr.generate_integration_reports(output_dir=str(report_dir))

        assert (report_dir / "connection_report.md").is_file()
        assert (report_dir / "health_report.md").is_file()
        assert (report_dir / "configuration_report.md").is_file()
        assert (report_dir / "api_support_report.md").is_file()


def test_cli_n8n_commands(tmp_path):
    """Verify CLI routing of n8n subcommands."""
    state_file = tmp_path / "connection_state.json"

    with patch("aios.n8n.connection.STATE_FILE", state_file):
        mgr = N8NLiveConnectionManager()
        # Pre-populate connected state
        mgr.save_state(
            {
                "host": "localhost",
                "port": 5678,
                "url": "http://localhost:5678",
                "auth_type": "none",
                "last_connected": 100.0,
                "connected": True,
            }
        )

        with patch("sys.exit") as mock_exit, patch("httpx.get") as mock_get:
            mock_resp = MagicMock(spec=httpx.Response)
            mock_resp.status_code = 200
            mock_resp.json.return_value = {"version": "2.29.10"}
            mock_get.return_value = mock_resp

            # 1. status Command
            execute_builtin_cli_command(["n8n", "status"], exit_on_complete=True)
            mock_exit.assert_called_with(0)

            # 2. config Command
            execute_builtin_cli_command(["n8n", "config"], exit_on_complete=True)
            mock_exit.assert_called_with(0)

            # 3. version Command
            execute_builtin_cli_command(["n8n", "version"], exit_on_complete=True)
            mock_exit.assert_called_with(0)

            # 4. health Command
            execute_builtin_cli_command(["n8n", "health"], exit_on_complete=True)
            mock_exit.assert_called_with(0)

            # 5. test Command
            execute_builtin_cli_command(["n8n", "test"], exit_on_complete=True)
            mock_exit.assert_called_with(0)

            # 6. disconnect Command
            execute_builtin_cli_command(["n8n", "disconnect"], exit_on_complete=True)
            mock_exit.assert_called_with(0)
            assert mgr.load_state()["connected"] is False
