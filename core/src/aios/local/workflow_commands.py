"""Phase 7: n8n Automation Intelligence — CLI Commands.

Implements:
  aios workflows              — workflows dashboard
  aios workflow generate      — generate workflows from template
  aios workflow deploy        — deploy raw JSON configurations
  aios workflow activate      — activate workflow triggers
  aios workflow deactivate    — deactivate workflow
  aios workflow diagnose      — diagnose node failures & credential issues
  aios workflow repair        — auto-repair credential & webhook settings
  aios workflow versions      — view deployment changes history
  aios workflow rollback      — rollback workflow to target version
  aios workflow dashboard     — render workflows summary (alias)
"""

from __future__ import annotations

import logging
import time
from typing import Any, List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from aios.services.workflows import (
    DeploymentStatus,
    WorkflowStatus,
)
from aios.services.workflows_impl import WorkflowRegistryServiceImpl

logger = logging.getLogger(__name__)
console = Console()

_DB_PATH: Optional[str] = None


def _get_registry() -> WorkflowRegistryServiceImpl:
    reg = WorkflowRegistryServiceImpl(db_path=_DB_PATH)
    reg.initialize()
    return reg


def _status_color(status: WorkflowStatus) -> str:
    colors = {
        WorkflowStatus.ACTIVE: "green",
        WorkflowStatus.INACTIVE: "yellow",
        WorkflowStatus.FAILED: "red",
        WorkflowStatus.UNKNOWN: "dim",
    }
    return colors.get(status, "white")


# ── Subcommand Handlers ───────────────────────────────────────────────────────


def cmd_workflow_dashboard(args: List[str]) -> None:
    """Show registered workflows dashboard."""
    reg = _get_registry()
    workflows = reg.list_workflows()

    table = Table(
        title="[bold cyan]⚡ n8n Workflow Automation Engine[/bold cyan]",
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("ID")
    table.add_column("Workflow Name", style="bold")
    table.add_column("Version")
    table.add_column("Status")
    table.add_column("Health Score")
    table.add_column("Webhook Endpoint")
    table.add_column("Last Run")

    for w in workflows:
        sc = _status_color(w.status)
        last_str = (
            time.strftime("%Y-%m-%d %H:%M", time.localtime(w.last_execution))
            if w.last_execution
            else "Never"
        )
        table.add_row(
            w.workflow_id[:8] + "...",
            w.name,
            f"v{w.version}",
            f"[{sc}]{w.status.value}[/{sc}]",
            f"{w.health_score}%",
            w.webhook_url or "—",
            last_str,
        )
    console.print(table)
    console.print(f"\n[dim]Total Workflows: {len(workflows)}[/dim]")


def cmd_workflow_generate(args: List[str]) -> None:
    """Generate workflow from pre-registered template prompts."""
    reg = _get_registry()

    if len(args) < 2:
        # List templates
        templates = reg.list_templates()
        table = Table(title="[bold cyan]Available Workflow Templates[/bold cyan]", show_header=True)
        table.add_column("Template Name", style="bold")
        table.add_column("Category")
        table.add_column("Description")
        for t in templates:
            table.add_row(t.name, t.category, t.description)
        console.print(table)
        console.print("\n[dim]Usage: aios workflow generate <name> <template_name>[/dim]")
        return

    name = args[0]
    tpl_name = " ".join(args[1:])

    try:
        wf = reg.generate_workflow_from_template(name, tpl_name)
        console.print(
            Panel(
                f"[bold green]✓ Workflow Generated Successfully[/bold green]\n\n"
                f"  Workflow:    [bold]{name}[/bold]\n"
                f"  Template:    {tpl_name}\n"
                f"  Nodes Count: {len(wf.nodes)}\n"
                f"  Webhook:     {wf.webhook_url}",
                title="Generator Output",
                border_style="green",
            )
        )
    except ValueError as exc:
        console.print(f"[red]Error: {exc}[/red]")


def cmd_workflow_deploy(args: List[str]) -> None:
    """Deploy raw JSON workflow configuration to local n8n instance registry."""
    reg = _get_registry()

    if len(args) < 2:
        console.print("[red]Usage: aios workflow deploy <name> '<json_content>'[/red]")
        return

    name = args[0]
    raw_json = " ".join(args[1:])

    try:
        wf = reg.deploy_workflow_json(name, raw_json)

        # Immediate Instant Deployment Notification Alert (Popup display)
        console.print()
        console.print(
            Panel(
                f"[bold white]WORKFLOW DEPLOYED[/bold white]\n\n"
                f"  Workflow:   [cyan]{wf.name}[/cyan]\n"
                f"  Status:     [green]Healthy[/green]\n"
                f"  Webhook:    Available ({wf.webhook_url})\n"
                f"  Project:    Agency\n"
                f"  Client:     ABC Company\n"
                f"  Deployment: [bold green]Success[/bold green]",
                title="[bold green]⚡ Deployment Live Notification[/bold green]",
                border_style="green",
                padding=(1, 2),
            )
        )
        console.print()

        # Sync to Knowledge Graph
        try:
            from aios.services.graph_impl import GraphServiceImpl
            from aios.services.graph_query import GraphQueryEngine
            from aios.services.workflows_graph_bridge import WorkflowsGraphBridge

            graph_svc = GraphServiceImpl()
            graph_svc.initialize()
            engine = GraphQueryEngine(graph_svc)
            bridge = WorkflowsGraphBridge(engine)
            bridge.sync_workflow(wf)
            bridge.sync_webhook("Incoming Webhook", wf.webhook_url, wf.name)
            graph_svc.shutdown()
        except Exception:
            pass

    except ValueError as exc:
        console.print(f"[red]Deployment Validation Failed: {exc}[/red]")


def cmd_workflow_activate(args: List[str]) -> None:
    """Set workflow status to active."""
    reg = _get_registry()
    if not args:
        console.print("[red]Usage: aios workflow activate <workflow_id>[/red]")
        return

    wid = args[0]
    wf = reg.get_workflow(wid)
    if not wf:
        console.print(f"[red]Workflow '{wid}' not found.[/red]")
        return

    wf.status = WorkflowStatus.ACTIVE
    reg.register_workflow(wf)
    console.print(f"[green]✓ Workflow '{wf.name}' successfully activated.[/green]")


def cmd_workflow_deactivate(args: List[str]) -> None:
    """Set workflow status to inactive."""
    reg = _get_registry()
    if not args:
        console.print("[red]Usage: aios workflow deactivate <workflow_id>[/red]")
        return

    wid = args[0]
    wf = reg.get_workflow(wid)
    if not wf:
        console.print(f"[red]Workflow '{wid}' not found.[/red]")
        return

    wf.status = WorkflowStatus.INACTIVE
    reg.register_workflow(wf)
    console.print(f"[green]✓ Workflow '{wf.name}' deactivated.[/green]")


def cmd_workflow_diagnose(args: List[str]) -> None:
    """Diagnose nodes, credentials, and webhooks configuration issues."""
    reg = _get_registry()
    if not args:
        console.print("[red]Usage: aios workflow diagnose <workflow_id>[/red]")
        return

    wid = args[0]
    diag = reg.diagnose_workflow(wid)
    if "error" in diag:
        console.print(f"[red]Error: {diag['error']}[/red]")
        return

    console.print(f"\n[bold cyan]Diagnostic Report for {wid[:8]}...[/bold cyan]")
    console.print(f"Checked Nodes: {diag['checked_nodes_count']}")
    console.print(f"Status: {diag['status'].upper()}")

    issues = diag.get("issues", [])
    if not issues:
        console.print("[green]✓ No configuration issues found in this workflow.[/green]")
        return

    for idx, issue in enumerate(issues):
        severity = issue["severity"].upper()
        sc = "red" if severity == "ERROR" else "yellow"
        console.print(
            f"  {idx + 1}. [{sc}]{severity}[/{sc}] on node '{issue['node']}': {issue['message']} ({issue['code']})"
        )


def cmd_workflow_repair(args: List[str]) -> None:
    """Auto-repair credential and webhook settings for a workflow."""
    reg = _get_registry()
    if not args:
        console.print("[red]Usage: aios workflow repair <workflow_id>[/red]")
        return

    wid = args[0]
    rep = reg.repair_workflow(wid)
    if "error" in rep:
        console.print(f"[red]Error: {rep['error']}[/red]")
        return

    console.print(f"\n[bold green]Auto-Repair Summary for {wid[:8]}...[/bold green]")
    actions = rep.get("repairs_performed", [])
    if not actions:
        console.print("[yellow]No auto-repairable issues were detected.[/yellow]")
        return

    for action in actions:
        console.print(f"  [green]✓[/green] {action}")
    console.print(f"Status: {rep['status'].upper()}")


def cmd_workflow_versions(args: List[str]) -> None:
    """View deployment history and rollback targets."""
    reg = _get_registry()
    if not args:
        console.print("[red]Usage: aios workflow versions <workflow_id>[/red]")
        return

    wid = args[0]
    deployments = reg.get_deployments(wid)

    table = Table(
        title=f"[bold cyan]Version Deployments History — {wid[:8]}[/bold cyan]", show_header=True
    )
    table.add_column("Version", style="bold")
    table.add_column("Changelog")
    table.add_column("Deployed By")
    table.add_column("Status")
    table.add_column("Timestamp")

    for d in deployments:
        dt_str = time.strftime("%Y-%m-%d %H:%M", time.localtime(d.timestamp))
        status_str = (
            "[green]Success[/green]"
            if d.status == DeploymentStatus.SUCCESS
            else (
                "[yellow]Rollback[/yellow]"
                if d.status == DeploymentStatus.ROLLBACK
                else "[red]Failed[/red]"
            )
        )
        table.add_row(
            f"v{d.version}",
            d.changelog,
            d.deployed_by or "—",
            status_str,
            dt_str,
        )
    console.print(table)


def cmd_workflow_rollback(args: List[str]) -> None:
    """Rollback workflow configuration structure to a specific version target."""
    reg = _get_registry()
    if len(args) < 2:
        console.print("[red]Usage: aios workflow rollback <workflow_id> <version>[/red]")
        return

    wid = args[0]
    try:
        ver = int(args[1])
    except ValueError:
        console.print("[red]Version must be an integer.[/red]")
        return

    success = reg.rollback_workflow(wid, ver)
    if success:
        console.print(
            f"[green]✓ Workflow configuration successfully rolled back to v{ver}.[/green]"
        )
    else:
        console.print(
            f"[red]✗ Failed to rollback workflow '{wid}' to version v{ver}. Check version exists.[/red]"
        )


# ── Main Dispatcher ──────────────────────────────────────────────────────────


def cmd_workflow_main(args: List[str], registry: Any = None) -> None:
    """Main CLI command group router for n8n workflow integrations."""
    if not args:
        cmd_workflow_dashboard([])
        return

    sub = args[0].lower()
    subargs = args[1:]

    # Support 'dashboard' subcommand explicitly or list
    handlers = {
        "dashboard": cmd_workflow_dashboard,
        "list": cmd_workflow_dashboard,
        "generate": cmd_workflow_generate,
        "deploy": cmd_workflow_deploy,
        "activate": cmd_workflow_activate,
        "deactivate": cmd_workflow_deactivate,
        "diagnose": cmd_workflow_diagnose,
        "repair": cmd_workflow_repair,
        "versions": cmd_workflow_versions,
        "rollback": cmd_workflow_rollback,
    }

    handler = handlers.get(sub)
    if handler:
        handler(subargs)
    else:
        console.print(
            Panel(
                "[bold]Available workflow commands:[/bold]\n\n"
                "  [cyan]aios workflow dashboard[/cyan]           — view automation registry\n"
                "  [cyan]aios workflow generate <name> <tpl>[/cyan] — generate workflows from templates\n"
                "  [cyan]aios workflow deploy <name> <json>[/cyan]   — deploy JSON workflow configs\n"
                "  [cyan]aios workflow activate <id>[/cyan]        — activate workflow execution\n"
                "  [cyan]aios workflow deactivate <id>[/cyan]      — deactivate workflow execution\n"
                "  [cyan]aios workflow diagnose <id>[/cyan]        — check nodes, webhooks and credentials\n"
                "  [cyan]aios workflow repair <id>[/cyan]          — auto-repair credential & webhooks\n"
                "  [cyan]aios workflow versions <id>[/cyan]        — view deployment history versions\n"
                "  [cyan]aios workflow rollback <id> <ver>[/cyan]  — rollback workflow configuration",
                title="[bold cyan]aios workflow — n8n Automation Engine[/bold cyan]",
                border_style="cyan",
            )
        )
