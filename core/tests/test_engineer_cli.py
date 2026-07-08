from unittest.mock import MagicMock, patch

from aios.cli import execute_builtin_cli_command
from aios.registry import ServiceRegistry


def test_cli_engineer_validate_no_violations():
    mock_service = MagicMock()
    mock_service.rule_engine.validate.return_value = []

    mock_registry = MagicMock()
    mock_registry.get.return_value = mock_service

    with patch.object(ServiceRegistry, "_global_registry", mock_registry):
        with patch("rich.console.Console.print") as mock_print:
            execute_builtin_cli_command(["engineer", "validate"], exit_on_complete=False)
            mock_print.assert_any_call("✓ No architectural validation violations found.")


def test_cli_engineer_validate_with_violations():
    mock_service = MagicMock()
    mock_service.rule_engine.validate.return_value = [
        {"type": "layering_violation", "description": "Layering violation error message"}
    ]

    mock_registry = MagicMock()
    mock_registry.get.return_value = mock_service

    with patch.object(ServiceRegistry, "_global_registry", mock_registry):
        with patch("rich.console.Console.print") as mock_print:
            execute_builtin_cli_command(["engineer", "validate"], exit_on_complete=False)
            mock_print.assert_any_call(
                "[red]Violation: layering_violation[/red] - Layering violation error message"
            )


def test_cli_engineer_search():
    mock_service = MagicMock()
    mock_service.search.return_value = [
        {"name": "ContextService", "type": "service", "file": "core/src/aios/services/context.py"}
    ]

    mock_registry = MagicMock()
    mock_registry.get.return_value = mock_service

    with patch.object(ServiceRegistry, "_global_registry", mock_registry):
        with patch("rich.console.Console.print") as mock_print:
            execute_builtin_cli_command(
                ["engineer", "search", "ContextService"], exit_on_complete=False
            )
            mock_print.assert_any_call(
                "- [bold cyan]ContextService[/bold cyan] (service) "
                "in core/src/aios/services/context.py"
            )


def test_cli_engineer_explain():
    mock_service = MagicMock()
    mock_service.graph.entities = {
        "ContextService": {
            "name": "ContextService",
            "type": "service",
            "file": "core/src/aios/services/context.py",
            "bases": ["ServiceLifecycle"],
        }
    }

    mock_registry = MagicMock()
    mock_registry.get.return_value = mock_service

    with patch.object(ServiceRegistry, "_global_registry", mock_registry):
        with patch("rich.console.Console.print") as mock_print:
            execute_builtin_cli_command(
                ["engineer", "explain", "ContextService"], exit_on_complete=False
            )
            mock_print.assert_any_call("[bold green]Entity: ContextService[/bold green]")
            mock_print.assert_any_call("Type: service")
            mock_print.assert_any_call("File: core/src/aios/services/context.py")
            mock_print.assert_any_call("Bases: ServiceLifecycle")


def test_cli_engineer_impact():
    mock_service = MagicMock()
    mock_service.impact_analyzer.analyze.return_value = {
        "entity": "ContextService",
        "file": "core/src/aios/services/context.py",
        "dependents": ["core/src/aios/services/memory.py"],
        "affected_tests": ["core/tests/test_memory.py"],
        "risk_score": 30,
    }

    mock_registry = MagicMock()
    mock_registry.get.return_value = mock_service

    with patch.object(ServiceRegistry, "_global_registry", mock_registry):
        with patch("rich.console.Console.print") as mock_print:
            execute_builtin_cli_command(
                ["engineer", "impact", "ContextService"], exit_on_complete=False
            )
            mock_print.assert_any_call(
                "[bold green]Impact Analysis for ContextService:[/bold green]"
            )
            mock_print.assert_any_call("File: core/src/aios/services/context.py")
            mock_print.assert_any_call("Dependents: core/src/aios/services/memory.py")
            mock_print.assert_any_call("Affected Tests: core/tests/test_memory.py")
            mock_print.assert_any_call("Risk Score: [bold red]30/100[/bold red]")


def test_cli_engineer_graph():
    mock_service = MagicMock()
    mock_service.dependency_analyzer.generate_import_graph.return_value = "digraph ImportGraph {}"

    mock_registry = MagicMock()
    mock_registry.get.return_value = mock_service

    with patch.object(ServiceRegistry, "_global_registry", mock_registry):
        with patch("rich.console.Console.print") as mock_print:
            execute_builtin_cli_command(["engineer", "graph", "import"], exit_on_complete=False)
            mock_print.assert_any_call("digraph ImportGraph {}")
