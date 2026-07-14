"""Phase 5: Project Intelligence — CLI Commands.

Implements:
  aios projects             — list all projects
  aios project list         — list all projects (alias)
  aios project create       — create a new project
  aios project switch       — switch active project + load context
  aios project dashboard    — rich project dashboard
  aios project status       — quick project status
  aios project graph        — project knowledge graph view
  aios project memory       — project memory browser
  aios project models       — show/set preferred models
  aios project cross        — cross-project intelligence
"""

from __future__ import annotations

import logging
import time
from typing import Any, List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from aios.services.project_registry import (
    KnowledgeGraphProjectConfig,
    MemoryProjectConfig,
    ProjectMemoryEntry,
    ProjectPriority,
    ProjectProfile,
    ProjectStatus,
    ProjectType,
    new_entry_id,
    new_project_id,
)
from aios.services.project_registry_impl import (
    ProjectContextImpl,
    ProjectMemoryImpl,
    ProjectRegistryImpl,
)

logger = logging.getLogger(__name__)
console = Console()

# ── DB paths (shared single SQLite file with project registry impl) ──────────
_DB_PATH: Optional[str] = None


def _get_registry() -> ProjectRegistryImpl:
    reg = ProjectRegistryImpl(db_path=_DB_PATH)
    reg.initialize()
    return reg


def _get_memory(registry: ProjectRegistryImpl) -> ProjectMemoryImpl:
    mem = ProjectMemoryImpl(db_path=registry._db_path)
    mem.initialize()
    return mem


def _get_context(registry: ProjectRegistryImpl) -> ProjectContextImpl:
    ctx = ProjectContextImpl(registry=registry, db_path=registry._db_path)
    ctx.initialize()
    return ctx


def _status_color(status: ProjectStatus) -> str:
    colors = {
        ProjectStatus.ACTIVE: "green",
        ProjectStatus.PAUSED: "yellow",
        ProjectStatus.PLANNING: "cyan",
        ProjectStatus.COMPLETED: "blue",
        ProjectStatus.ARCHIVED: "dim",
    }
    return colors.get(status, "white")


def _priority_color(priority: ProjectPriority) -> str:
    colors = {
        ProjectPriority.CRITICAL: "red",
        ProjectPriority.HIGH: "yellow",
        ProjectPriority.MEDIUM: "cyan",
        ProjectPriority.LOW: "green",
    }
    return colors.get(priority, "white")


# ---------------------------------------------------------------------------
# cmd_project_list
# ---------------------------------------------------------------------------


def cmd_project_list(args: List[str], registry: Any = None) -> None:
    """List all registered projects."""
    reg = _get_registry()
    projects = reg.list_projects()
    active = reg.get_active_project()
    active_id = active.project_id if active else ""

    table = Table(
        title="[bold cyan]🗂  AI OS — Project Registry[/bold cyan]",
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("", width=2)
    table.add_column("Project", style="bold")
    table.add_column("Type")
    table.add_column("Priority")
    table.add_column("Status")
    table.add_column("Models")
    table.add_column("Phase / Sprint")
    table.add_column("Last Active")

    for p in projects:
        marker = "▶" if p.project_id == active_id else " "
        sc = _status_color(p.status)
        pc = _priority_color(p.priority)
        last_active = time.strftime("%Y-%m-%d", time.localtime(p.last_active))
        models_str = ", ".join(p.preferred_models[:2])
        phase_sprint = f"{p.current_phase or '—'} / {p.current_sprint or '—'}"
        table.add_row(
            f"[bold cyan]{marker}[/bold cyan]",
            p.name,
            p.project_type.value,
            f"[{pc}]{p.priority.value}[/{pc}]",
            f"[{sc}]{p.status.value}[/{sc}]",
            models_str or "—",
            phase_sprint,
            last_active,
        )

    console.print(table)
    console.print(f"\n[dim]Total: {len(projects)} project(s)[/dim]")


# ---------------------------------------------------------------------------
# cmd_project_create
# ---------------------------------------------------------------------------


def cmd_project_create(args: List[str], registry: Any = None) -> None:
    """Create a new project interactively (or from args)."""
    reg = _get_registry()

    if not args:
        console.print(
            Panel(
                "Usage: [bold cyan]aios project create <name> [type] [priority][/bold cyan]\n"
                "Example: [cyan]aios project create MyApp software high[/cyan]",
                title="[bold]Create Project[/bold]",
                border_style="cyan",
            )
        )
        return

    name = args[0]
    ptype = (
        ProjectType(args[1])
        if len(args) > 1 and args[1] in [t.value for t in ProjectType]
        else ProjectType.SOFTWARE
    )
    priority = (
        ProjectPriority(args[2])
        if len(args) > 2 and args[2] in [p.value for p in ProjectPriority]
        else ProjectPriority.MEDIUM
    )

    existing = reg.find_project(name)
    if existing:
        console.print(f"[yellow]Project '[bold]{name}[/bold]' already exists.[/yellow]")
        return

    pid = new_project_id()
    profile = ProjectProfile(
        project_id=pid,
        name=name,
        description="",
        project_type=ptype,
        status=ProjectStatus.PLANNING,
        priority=priority,
        owner="Anzar Akhtar",
        memory=MemoryProjectConfig(enabled=True, namespace=pid),
        knowledge_graph=KnowledgeGraphProjectConfig(enabled=True),
    )
    reg.register_project(profile)

    # Register in knowledge graph
    try:
        from aios.services.graph_impl import GraphServiceImpl
        from aios.services.graph_query import GraphQueryEngine
        from aios.services.project_graph_bridge import ProjectGraphBridge

        graph_svc = GraphServiceImpl()
        graph_svc.initialize()
        engine = GraphQueryEngine(graph_svc)
        bridge = ProjectGraphBridge(engine)
        entity_id = bridge.register_project_in_graph(profile)
        if entity_id:
            reg.update_project(pid, {"knowledge_graph": {"enabled": True, "entity_id": entity_id}})
        graph_svc.shutdown()
    except Exception as exc:
        logger.warning("Graph registration failed for new project: %s", exc)

    console.print(
        Panel(
            f"[bold green]✓ Project Created[/bold green]\n\n"
            f"  Name:     [bold]{name}[/bold]\n"
            f"  Type:     {ptype.value}\n"
            f"  Priority: {priority.value}\n"
            f"  ID:       {pid}\n\n"
            f"[dim]Run [cyan]aios project switch {name}[/cyan] to activate it.[/dim]",
            title="[bold cyan]New Project[/bold cyan]",
            border_style="green",
        )
    )


# ---------------------------------------------------------------------------
# cmd_project_switch
# ---------------------------------------------------------------------------


def cmd_project_switch(args: List[str], registry: Any = None) -> None:
    """Switch active project and load full context."""
    if not args:
        console.print("[red]Usage: aios project switch <project_name>[/red]")
        return

    project_name = " ".join(args)
    reg = _get_registry()
    ctx_svc = _get_context(reg)

    profile = reg.find_project(project_name)
    if not profile:
        # Fuzzy match
        candidates = [p for p in reg.list_projects() if project_name.lower() in p.name.lower()]
        if len(candidates) == 1:
            profile = candidates[0]
        elif len(candidates) > 1:
            console.print(
                f"[yellow]Multiple matches for '{project_name}':[/yellow] "
                + ", ".join(c.name for c in candidates)
            )
            return
        else:
            console.print(f"[red]Project '[bold]{project_name}[/bold]' not found.[/red]")
            return

    ctx = ctx_svc.switch_to(profile.project_id)

    console.print(
        Panel(
            f"[bold green]✓ Switched to Project[/bold green]\n\n"
            f"  Project:  [bold cyan]{profile.name}[/bold cyan]\n"
            f"  Type:     {profile.project_type.value}\n"
            f"  Sprint:   {ctx.current_sprint or '—'}\n"
            f"  Phase:    {ctx.current_phase or '—'}\n"
            f"  Branch:   {ctx.active_branch}\n"
            f"  Models:   {', '.join(ctx.active_models) or '—'}\n\n"
            f"[dim]GitHub: {'✓' if profile.github.enabled else '✗'}  "
            f"Notion: {'✓' if profile.notion.enabled else '✗'}  "
            f"n8n: {'✓' if profile.n8n.enabled else '✗'}[/dim]",
            title=f"[bold cyan]Project Switch → {profile.name}[/bold cyan]",
            border_style="cyan",
        )
    )


# ---------------------------------------------------------------------------
# cmd_project_dashboard
# ---------------------------------------------------------------------------


def cmd_project_dashboard(args: List[str], registry: Any = None) -> None:
    """Render the full project dashboard."""
    reg = _get_registry()
    ctx_svc = _get_context(reg)
    mem_svc = _get_memory(reg)

    # Determine which project
    if args:
        name = " ".join(args)
        profile = reg.find_project(name)
        if not profile:
            console.print(f"[red]Project '{name}' not found.[/red]")
            return
    else:
        profile = reg.get_active_project()
        if not profile:
            console.print(
                "[yellow]No active project. Use [cyan]aios project switch <name>[/cyan] first.[/yellow]"
            )
            return

    dash = ctx_svc.get_dashboard_data(profile.project_id)
    sc = _status_color(profile.status)
    pc = _priority_color(profile.priority)
    health = dash.get("health_score", 100)
    stale = dash.get("stale_days", 0)

    health_color = "green" if health >= 80 else ("yellow" if health >= 50 else "red")

    # ── Header ────────────────────────────────────────────────────────────────
    console.print(
        Panel(
            f"  [bold white]{profile.name}[/bold white]   "
            f"[dim]{profile.description}[/dim]\n\n"
            f"  Type: [cyan]{profile.project_type.value}[/cyan]  "
            f"Priority: [{pc}]{profile.priority.value}[/{pc}]  "
            f"Status: [{sc}]{profile.status.value}[/{sc}]\n"
            f"  Phase: [bold]{profile.current_phase or '—'}[/bold]   "
            f"Sprint: [bold]{profile.current_sprint or '—'}[/bold]\n"
            f"  Health: [{health_color}]{health}%[/{health_color}]   "
            f"[dim]Last active: {stale}d ago[/dim]",
            title=f"[bold cyan]📋 Project Dashboard — {profile.name}[/bold cyan]",
            border_style="cyan",
        )
    )

    # ── Preferred Models ──────────────────────────────────────────────────────
    if profile.preferred_models:
        models_table = Table(title="Preferred Models", box=None, show_header=False)
        models_table.add_column("", style="cyan")
        models_table.add_column("")
        for i, model in enumerate(profile.preferred_models):
            models_table.add_row(f"{'★' if i == 0 else ' '} {model}", "primary" if i == 0 else "")
        console.print(models_table)

    # ── Integrations ──────────────────────────────────────────────────────────
    int_table = Table(title="Integrations", box=None, show_header=True, header_style="bold")
    int_table.add_column("Integration")
    int_table.add_column("Status")
    int_table.add_column("Detail")

    integrations = dash.get("integrations", {})

    gh = integrations.get("github", {})
    int_table.add_row(
        "GitHub",
        "[green]✓ Enabled[/green]" if gh.get("enabled") else "[dim]✗ Disabled[/dim]",
        gh.get("repo", "—"),
    )
    nt = integrations.get("notion", {})
    int_table.add_row(
        "Notion",
        "[green]✓ Enabled[/green]" if nt.get("enabled") else "[dim]✗ Disabled[/dim]",
        "—",
    )
    wf = integrations.get("n8n", {})
    int_table.add_row(
        "n8n",
        "[green]✓ Enabled[/green]" if wf.get("enabled") else "[dim]✗ Disabled[/dim]",
        f"{len(wf.get('workflow_ids', []))} workflows" if wf.get("enabled") else "—",
    )
    kg_enabled = profile.knowledge_graph.enabled
    int_table.add_row(
        "Knowledge Graph",
        "[green]✓ Enabled[/green]" if kg_enabled else "[dim]✗ Disabled[/dim]",
        profile.knowledge_graph.entity_id[:8] + "..." if profile.knowledge_graph.entity_id else "—",
    )
    console.print(int_table)

    # ── Open Tasks ────────────────────────────────────────────────────────────
    open_tasks = dash.get("open_tasks", [])
    if open_tasks:
        tasks_table = Table(title="Open Tasks", box=None, show_header=True)
        tasks_table.add_column("Task")
        tasks_table.add_column("Status")
        for t in open_tasks[:5]:
            tasks_table.add_row(t.get("title", "—"), t.get("status", "—"))
        console.print(tasks_table)
    else:
        console.print("[dim]No open tasks tracked in context.[/dim]")

    # ── Recent Memory ─────────────────────────────────────────────────────────
    try:
        recent = mem_svc.get_recent(profile.project_id, limit=3)
        if recent:
            mem_table = Table(title="Recent Memory", box=None, show_header=True)
            mem_table.add_column("Category", style="cyan")
            mem_table.add_column("Title")
            mem_table.add_column("Date")
            for m in recent:
                date = time.strftime("%Y-%m-%d", time.localtime(m.updated_at))
                mem_table.add_row(m.category, m.title, date)
            console.print(mem_table)
    except Exception:
        pass


# ---------------------------------------------------------------------------
# cmd_project_status
# ---------------------------------------------------------------------------


def cmd_project_status(args: List[str], registry: Any = None) -> None:
    """Quick one-line status for a project."""
    reg = _get_registry()
    if args:
        profile = reg.find_project(" ".join(args))
    else:
        profile = reg.get_active_project()

    if not profile:
        console.print("[yellow]No project found.[/yellow]")
        return

    sc = _status_color(profile.status)
    pc = _priority_color(profile.priority)
    last_active = time.strftime("%Y-%m-%d %H:%M", time.localtime(profile.last_active))

    console.print(
        f"[bold cyan]{profile.name}[/bold cyan] "
        f"[{sc}]{profile.status.value}[/{sc}] "
        f"[{pc}]{profile.priority.value}[/{pc}] "
        f"| {profile.project_type.value} "
        f"| Phase: {profile.current_phase or '—'} "
        f"| Sprint: {profile.current_sprint or '—'} "
        f"| Last: {last_active}"
    )


# ---------------------------------------------------------------------------
# cmd_project_graph
# ---------------------------------------------------------------------------


def cmd_project_graph(args: List[str], registry: Any = None) -> None:
    """Show project knowledge graph subgraph."""
    reg = _get_registry()
    if args:
        profile = reg.find_project(" ".join(args))
    else:
        profile = reg.get_active_project()

    if not profile:
        console.print("[yellow]No project found.[/yellow]")
        return

    try:
        from aios.services.graph_impl import GraphServiceImpl
        from aios.services.graph_query import GraphQueryEngine
        from aios.services.project_graph_bridge import ProjectGraphBridge

        graph_svc = GraphServiceImpl()
        graph_svc.initialize()
        engine = GraphQueryEngine(graph_svc)
        bridge = ProjectGraphBridge(engine)

        overview = bridge.get_project_graph_summary(profile.name)
        graph_svc.shutdown()

        if "error" in overview:
            console.print(f"[yellow]Graph: {overview['error']}[/yellow]")
            return

        sub = overview.get("subgraph", {})
        total_count = sum(len(v) for v in sub.values() if isinstance(v, list))

        console.print(
            Panel(
                f"[bold]{profile.name}[/bold] — {total_count} connected nodes\n\n"
                + "\n".join(
                    f"  [cyan]{etype}[/cyan]: {len(items)} node(s)"
                    for etype, items in sub.items()
                    if isinstance(items, list) and items
                ),
                title=f"[bold cyan]🕸  Knowledge Graph — {profile.name}[/bold cyan]",
                border_style="cyan",
            )
        )
    except Exception as exc:
        console.print(f"[red]Graph error: {exc}[/red]")


# ---------------------------------------------------------------------------
# cmd_project_memory
# ---------------------------------------------------------------------------


def cmd_project_memory(args: List[str], registry: Any = None) -> None:
    """Browse or add project memory entries."""
    reg = _get_registry()
    mem_svc = _get_memory(reg)

    # Sub-action: add
    if args and args[0] == "add":
        # Usage: aios project memory add <project> <category> <title> [content]
        if len(args) < 4:
            console.print("[red]Usage: aios project memory add <project> <category> <title>[/red]")
            return
        pname = args[1]
        category = args[2]
        title = " ".join(args[3:])
        profile = reg.find_project(pname)
        if not profile:
            console.print(f"[red]Project '{pname}' not found.[/red]")
            return
        entry = ProjectMemoryEntry(
            entry_id=new_entry_id(),
            project_id=profile.project_id,
            category=category,
            title=title,
            content="",
        )
        mem_svc.store(entry)
        console.print(f"[green]✓ Memory entry stored for [bold]{pname}[/bold][/green]")
        return

    # Default: list recent
    if args and args[0] not in ("list", "add"):
        profile = reg.find_project(" ".join(args))
    else:
        profile = reg.get_active_project()

    if not profile:
        console.print("[yellow]No project found.[/yellow]")
        return

    entries = mem_svc.retrieve(profile.project_id, limit=20)

    table = Table(
        title=f"[bold cyan]🧠 Project Memory — {profile.name}[/bold cyan]",
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("Category", style="cyan")
    table.add_column("Title")
    table.add_column("Date")

    for e in entries:
        date = time.strftime("%Y-%m-%d", time.localtime(e.updated_at))
        table.add_row(e.category, e.title, date)

    if entries:
        console.print(table)
    else:
        console.print(f"[dim]No memory entries for {profile.name} yet.[/dim]")


# ---------------------------------------------------------------------------
# cmd_project_models
# ---------------------------------------------------------------------------


def cmd_project_models(args: List[str], registry: Any = None) -> None:
    """Show or update preferred models for a project."""
    reg = _get_registry()

    if not args:
        # Show all projects with their models
        projects = reg.list_projects()
        table = Table(
            title="[bold cyan]🤖 Project Model Profiles[/bold cyan]",
            show_header=True,
            header_style="bold magenta",
        )
        table.add_column("Project")
        table.add_column("Type")
        table.add_column("Primary Model", style="green")
        table.add_column("All Preferred Models")

        for p in projects:
            primary = p.preferred_models[0] if p.preferred_models else "—"
            all_models = " → ".join(p.preferred_models) or "—"
            table.add_row(p.name, p.project_type.value, primary, all_models)
        console.print(table)
        return

    # Show models for a specific project
    profile = reg.find_project(" ".join(args))
    if not profile:
        console.print(f"[red]Project '{' '.join(args)}' not found.[/red]")
        return

    console.print(
        Panel(
            "\n".join(
                f"  {'★' if i == 0 else ' '} [cyan]{m}[/cyan]"
                for i, m in enumerate(profile.preferred_models)
            )
            or "  [dim]No preferred models set.[/dim]",
            title=f"[bold cyan]Model Profile — {profile.name}[/bold cyan]",
            border_style="cyan",
        )
    )


# ---------------------------------------------------------------------------
# cmd_project_cross
# ---------------------------------------------------------------------------


def cmd_project_cross(args: List[str], registry: Any = None) -> None:
    """Cross-project intelligence queries."""
    reg = _get_registry()

    subcommand = args[0] if args else ""

    if subcommand == "shared":
        # Show shared integrations/models across projects
        projects = reg.list_projects()
        console.print(
            Panel(
                "\n".join(
                    f"  [cyan]{p.name}[/cyan] — {', '.join(p.preferred_models[:2]) or '—'}"
                    for p in projects
                ),
                title="[bold cyan]🔗 Cross-Project — Shared Resources[/bold cyan]",
                border_style="cyan",
            )
        )

    elif subcommand == "integration" and len(args) > 1:
        integration = args[1]
        matches = reg.query_by_integration(integration)
        table = Table(
            title=f"[bold cyan]Projects using '{integration}'[/bold cyan]",
            show_header=True,
        )
        table.add_column("Project")
        table.add_column("Type")
        table.add_column("Status")
        for p in matches:
            table.add_row(p.name, p.project_type.value, p.status.value)
        if matches:
            console.print(table)
        else:
            console.print(f"[yellow]No projects found using '{integration}'.[/yellow]")

    elif subcommand == "attention":
        needing = reg.get_projects_needing_attention()
        if not needing:
            console.print("[green]✓ All projects are healthy and active.[/green]")
            return
        table = Table(title="[bold yellow]⚠  Projects Needing Attention[/bold yellow]")
        table.add_column("Project")
        table.add_column("Status")
        table.add_column("Last Active")
        for p in needing:
            last = time.strftime("%Y-%m-%d", time.localtime(p.last_active))
            sc = _status_color(p.status)
            table.add_row(p.name, f"[{sc}]{p.status.value}[/{sc}]", last)
        console.print(table)

    elif subcommand == "related" and len(args) > 1:
        pname = " ".join(args[1:])
        profile = reg.find_project(pname)
        if not profile:
            console.print(f"[red]Project '{pname}' not found.[/red]")
            return
        related = reg.find_related_projects(profile.project_id)
        if not related:
            console.print(f"[dim]No related projects found for {pname}.[/dim]")
            return
        table = Table(title=f"[bold cyan]Related Projects — {profile.name}[/bold cyan]")
        table.add_column("Project")
        table.add_column("Type")
        table.add_column("Shared Tags/Models")
        for p in related:
            shared_tags = set(p.tags) & set(profile.tags)
            shared_models = set(p.preferred_models) & set(profile.preferred_models)
            shared = list(shared_tags | shared_models)
            table.add_row(p.name, p.project_type.value, ", ".join(shared[:3]))
        console.print(table)

    else:
        console.print(
            Panel(
                "[bold]Cross-Project Intelligence Commands:[/bold]\n\n"
                "  [cyan]aios project cross shared[/cyan]                — shared resources\n"
                "  [cyan]aios project cross integration <name>[/cyan]    — projects using integration\n"
                "  [cyan]aios project cross attention[/cyan]              — projects needing attention\n"
                "  [cyan]aios project cross related <project>[/cyan]      — find related projects",
                title="[bold cyan]Cross-Project Intelligence[/bold cyan]",
                border_style="cyan",
            )
        )


# ---------------------------------------------------------------------------
# Main dispatcher
# ---------------------------------------------------------------------------


def cmd_project_main(args: List[str], registry: Any = None) -> None:
    """Main dispatcher for `aios project` commands."""
    if not args:
        cmd_project_list([], registry)
        return

    subcommand = args[0].lower()
    subargs = args[1:]

    handlers = {
        "list": cmd_project_list,
        "create": cmd_project_create,
        "switch": cmd_project_switch,
        "dashboard": cmd_project_dashboard,
        "status": cmd_project_status,
        "graph": cmd_project_graph,
        "memory": cmd_project_memory,
        "models": cmd_project_models,
        "cross": cmd_project_cross,
    }

    handler = handlers.get(subcommand)
    if handler:
        handler(subargs, registry)
    else:
        console.print(
            Panel(
                "[bold]Available project subcommands:[/bold]\n\n"
                "  [cyan]aios project list[/cyan]                  — list all projects\n"
                "  [cyan]aios project create <name>[/cyan]         — create a project\n"
                "  [cyan]aios project switch <name>[/cyan]         — switch active project\n"
                "  [cyan]aios project dashboard[/cyan]             — project dashboard\n"
                "  [cyan]aios project status[/cyan]                — quick project status\n"
                "  [cyan]aios project graph[/cyan]                 — knowledge graph view\n"
                "  [cyan]aios project memory[/cyan]                — memory browser\n"
                "  [cyan]aios project models[/cyan]                — preferred model profiles\n"
                "  [cyan]aios project cross[/cyan]                 — cross-project intelligence",
                title="[bold cyan]aios project — Project Intelligence[/bold cyan]",
                border_style="cyan",
            )
        )
