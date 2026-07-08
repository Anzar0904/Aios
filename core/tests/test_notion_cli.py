from unittest.mock import MagicMock, patch

from aios.cli import execute_builtin_cli_command
from aios.registry import ServiceRegistry


def test_cli_notion_usage_no_args():
    with patch("rich.console.Console.print") as mock_print:
        execute_builtin_cli_command(["notion"], exit_on_complete=False)
        mock_print.assert_called_once()
        args = mock_print.call_args[0][0]
        assert "Usage: aios notion" in args


def test_cli_notion_login():
    mock_service = MagicMock()
    mock_service.login.return_value = True

    mock_registry = MagicMock()
    mock_registry.get.return_value = mock_service

    with patch.object(ServiceRegistry, "_global_registry", mock_registry):
        with patch("rich.console.Console.print") as mock_print:
            execute_builtin_cli_command(
                ["notion", "login", "secret_123", "my_workspace"], exit_on_complete=False
            )
            mock_service.login.assert_called_once_with("secret_123", "my_workspace")
            mock_print.assert_any_call(
                "[green]Successfully connected workspace 'my_workspace'[/green]"
            )


def test_cli_notion_logout():
    mock_service = MagicMock()

    mock_registry = MagicMock()
    mock_registry.get.return_value = mock_service

    with patch.object(ServiceRegistry, "_global_registry", mock_registry):
        with patch("rich.console.Console.print") as mock_print:
            execute_builtin_cli_command(
                ["notion", "logout", "my_workspace"], exit_on_complete=False
            )
            mock_service.logout.assert_called_once_with("my_workspace")
            mock_print.assert_any_call(
                "[green]Successfully logged out of workspace 'my_workspace'[/green]"
            )


def test_cli_notion_status():
    mock_service = MagicMock()
    mock_service.get_status.return_value = {
        "status": "connected",
        "workspaces": ["workspace_a", "workspace_b"],
    }

    mock_registry = MagicMock()
    mock_registry.get.return_value = mock_service

    with patch.object(ServiceRegistry, "_global_registry", mock_registry):
        with patch("rich.console.Console.print") as mock_print:
            execute_builtin_cli_command(["notion", "status"], exit_on_complete=False)
            mock_print.assert_any_call("Status: [bold]connected[/bold]")
            mock_print.assert_any_call("Connected Workspaces: workspace_a, workspace_b")


def test_cli_notion_sync():
    mock_service = MagicMock()
    mock_service.sync.return_value = {
        "status": "success",
        "synced_pages": 4,
        "workspaces": ["workspace_a"],
    }

    mock_registry = MagicMock()
    mock_registry.get.return_value = mock_service

    with patch.object(ServiceRegistry, "_global_registry", mock_registry):
        with patch("rich.console.Console.print") as mock_print:
            execute_builtin_cli_command(["notion", "sync"], exit_on_complete=False)
            mock_print.assert_any_call("[green]✓ Successfully synchronized 4 pages.[/green]")


def test_cli_notion_search():
    mock_service = MagicMock()
    mock_service.search.return_value = [
        {"title": "My Page", "type": "page", "workspace": "ws_1", "id": "page_id_1"}
    ]

    mock_registry = MagicMock()
    mock_registry.get.return_value = mock_service

    with patch.object(ServiceRegistry, "_global_registry", mock_registry):
        with patch("rich.console.Console.print") as mock_print:
            execute_builtin_cli_command(["notion", "search", "My Query"], exit_on_complete=False)
            mock_service.search.assert_called_once_with("My Query")
            mock_print.assert_any_call("- My Page (page) in workspace 'ws_1' [ID: page_id_1]")


def test_cli_notion_summarize():
    mock_service = MagicMock()
    mock_service.summarize.return_value = "Page Summary text"

    mock_registry = MagicMock()
    mock_registry.get.return_value = mock_service

    with patch.object(ServiceRegistry, "_global_registry", mock_registry):
        with patch("rich.console.Console.print") as mock_print:
            execute_builtin_cli_command(["notion", "summarize", "page_1"], exit_on_complete=False)
            mock_service.summarize.assert_called_once_with("page_1")
            mock_print.assert_any_call("[bold]Summary of page page_1:[/bold]\nPage Summary text")


def test_cli_notion_create_page():
    mock_service = MagicMock()
    mock_service.create_page.return_value = {"id": "new_page_id"}

    mock_registry = MagicMock()
    mock_registry.get.return_value = mock_service

    with patch.object(ServiceRegistry, "_global_registry", mock_registry):
        with patch("rich.console.Console.print") as mock_print:
            execute_builtin_cli_command(
                ["notion", "create-page", "parent_1", "Page Title", "Page Content"],
                exit_on_complete=False,
            )
            mock_service.create_page.assert_called_once_with(
                "parent_1", "Page Title", "Page Content"
            )
            mock_print.assert_any_call(
                "[green]Successfully created page 'Page Title' [ID: new_page_id][/green]"
            )


def test_cli_notion_update_page():
    mock_service = MagicMock()
    mock_service.update_page.return_value = {"blocks_added": 3}

    mock_registry = MagicMock()
    mock_registry.get.return_value = mock_service

    with patch.object(ServiceRegistry, "_global_registry", mock_registry):
        with patch("rich.console.Console.print") as mock_print:
            execute_builtin_cli_command(
                ["notion", "update-page", "page_1", "Appended Content"], exit_on_complete=False
            )
            mock_service.update_page.assert_called_once_with("page_1", "Appended Content")
            mock_print.assert_any_call(
                "[green]Successfully updated page page_1. Blocks added: 3[/green]"
            )


def test_cli_notion_list_databases():
    mock_service = MagicMock()
    mock_service.list_databases.return_value = [
        {"id": "db_1", "title": [{"plain_text": "My Database"}]}
    ]

    mock_registry = MagicMock()
    mock_registry.get.return_value = mock_service

    with patch.object(ServiceRegistry, "_global_registry", mock_registry):
        with patch("rich.console.Console.print") as mock_print:
            execute_builtin_cli_command(["notion", "list-databases"], exit_on_complete=False)
            mock_print.assert_any_call("- My Database [ID: db_1]")
