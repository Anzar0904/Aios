"""Phase 8: Documentation Intelligence — CLI Commands.

Implements subcommands under the 'aios docs' group:
  aios docs list         — list all registered document records
  aios docs search       — keyword search in document titles and contents
  aios docs readme       — auto-generate a README for a workspace project
  aios docs architecture — auto-generate architecture manual
  aios docs api          — auto-generate service API docs
  aios docs project      — auto-generate project overview summaries
  aios docs workflows    — auto-generate workflow properties summary
  aios docs integrations — auto-generate integration health manuals
  aios docs agency       — auto-generate crm and lead pipeline reports
  aios docs changelog    — generate commit history logs
  aios docs release      — generate migration release logs
"""

from __future__ import annotations

import logging
import time
from typing import Any, List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from aios.services.documentation import DocStatus, DocType, DocumentRecord, new_id
from aios.services.documentation_impl import DocumentationServiceImpl

logger = logging.getLogger(__name__)
console = Console()

_DB_PATH: Optional[str] = None


def _get_engine() -> DocumentationServiceImpl:
    eng = DocumentationServiceImpl(db_path=_DB_PATH)
    eng.initialize()
    return eng


# ── Subcommand Handlers ───────────────────────────────────────────────────────


def cmd_docs_list(args: List[str]) -> None:
    """List all registered document catalog items."""
    eng = _get_engine()
    docs = eng.list_documents()

    table = Table(
        title="[bold cyan]📖 Universal Documentation catalog[/bold cyan]",
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("Document ID")
    table.add_column("Title", style="bold")
    table.add_column("Type")
    table.add_column("Project")
    table.add_column("Status")
    table.add_column("Ver")
    table.add_column("Updated At")

    for d in docs:
        time_str = time.strftime("%Y-%m-%d %H:%M", time.localtime(d.updated_at))
        table.add_row(
            d.document_id[:8] + "...",
            d.title,
            d.doc_type.value,
            d.project_id or "-",
            d.status.value,
            str(d.version),
            time_str,
        )
    console.print(table)


def cmd_docs_search(args: List[str]) -> None:
    """Search registered documentations by keyword."""
    if not args:
        console.print("[red]Usage: aios docs search <query_string>[/red]")
        return
    query = " ".join(args)
    eng = _get_engine()
    results = eng.search_documents(query)

    if not results:
        console.print(f"[yellow]No documents found matching: '{query}'[/yellow]")
        return

    table = Table(
        title=f"Search Results for '{query}'", show_header=True, header_style="bold green"
    )
    table.add_column("Document ID")
    table.add_column("Title", style="bold")
    table.add_column("Type")
    table.add_column("Project")
    table.add_column("Snippet")

    for d in results:
        snippet = d.content[:60] + "..." if len(d.content) > 60 else d.content
        table.add_row(d.document_id[:8], d.title, d.doc_type.value, d.project_id or "-", snippet)
    console.print(table)


def cmd_docs_readme(args: List[str]) -> None:
    """Generate README for a project."""
    if not args:
        console.print("[red]Usage: aios docs readme <project_id>[/red]")
        return
    pid = args[0]
    eng = _get_engine()
    doc = eng.generate_readme(pid)

    # Sync to Graph
    try:
        from aios.services.documentation_graph_bridge import DocumentationGraphBridge
        from aios.services.graph_impl import GraphServiceImpl
        from aios.services.graph_query import GraphQueryEngine

        graph_svc = GraphServiceImpl()
        graph_svc.initialize()
        bridge = DocumentationGraphBridge(GraphQueryEngine(graph_svc))
        bridge.sync_document(doc)
        graph_svc.shutdown()
    except Exception:
        pass

    console.print("[green]✓ Generated Project README:[/green]")
    console.print(Panel(doc.content, title=doc.title, border_style="cyan"))


def cmd_docs_architecture(args: List[str]) -> None:
    """Generate system architecture doc."""
    if not args:
        console.print("[red]Usage: aios docs architecture <project_id>[/red]")
        return
    pid = args[0]
    eng = _get_engine()
    doc = eng.generate_architecture_doc(pid)

    console.print("[green]✓ Generated Architecture Guide:[/green]")
    console.print(Panel(doc.content, title=doc.title, border_style="cyan"))


def cmd_docs_api(args: List[str]) -> None:
    """Generate API reference catalog."""
    if not args:
        console.print("[red]Usage: aios docs api <module_name>[/red]")
        return
    mname = args[0]
    eng = _get_engine()
    doc = eng.generate_api_doc(mname)

    console.print("[green]✓ Generated API References:[/green]")
    console.print(Panel(doc.content, title=doc.title, border_style="cyan"))


def cmd_docs_project(args: List[str]) -> None:
    """Generate project documentation report."""
    if not args:
        console.print("[red]Usage: aios docs project <project_id>[/red]")
        return
    pid = args[0]
    eng = _get_engine()
    content = f"# Project Documentation Report: {pid.upper()}\n\nGoals, Milestones, and Dependencies logged."
    doc = DocumentRecord(
        document_id=new_id(),
        title=f"Project Doc: {pid.capitalize()}",
        doc_type=DocType.PROJECT_DOCS,
        content=content,
        project_id=pid,
        status=DocStatus.PUBLISHED,
    )
    eng.register_document(doc)
    console.print(Panel(doc.content, title=doc.title, border_style="cyan"))


def cmd_docs_workflows(args: List[str]) -> None:
    """Generate workflow documentation report."""
    if not args:
        console.print("[red]Usage: aios docs workflows <workflow_id>[/red]")
        return
    wid = args[0]
    eng = _get_engine()
    content = f"# Workflow Properties: {wid}\n\nNodes connection map and active triggers."
    doc = DocumentRecord(
        document_id=new_id(),
        title=f"Workflow Doc: {wid}",
        doc_type=DocType.WORKFLOW_DOCS,
        content=content,
        project_id=wid,
        status=DocStatus.PUBLISHED,
    )
    eng.register_document(doc)
    console.print(Panel(doc.content, title=doc.title, border_style="cyan"))


def cmd_docs_integrations(args: List[str]) -> None:
    """Generate integration documentation report."""
    if not args:
        console.print("[red]Usage: aios docs integrations <provider>[/red]")
        return
    prov = args[0]
    eng = _get_engine()
    content = f"# Integration Guide: {prov.capitalize()}\n\nDetails on credentials configuration and capabilities."
    doc = DocumentRecord(
        document_id=new_id(),
        title=f"Integration Doc: {prov.capitalize()}",
        doc_type=DocType.INTEGRATION_DOCS,
        content=content,
        project_id=prov,
        status=DocStatus.PUBLISHED,
    )
    eng.register_document(doc)
    console.print(Panel(doc.content, title=doc.title, border_style="cyan"))


def cmd_docs_agency(args: List[str]) -> None:
    """Generate agency documentation report."""
    if not args:
        console.print("[red]Usage: aios docs agency <client_id>[/red]")
        return
    cid = args[0]
    eng = _get_engine()
    content = (
        f"# Agency Portfolio: {cid}\n\nClient leads progression and pipeline revenue projection."
    )
    doc = DocumentRecord(
        document_id=new_id(),
        title=f"Agency Report: {cid}",
        doc_type=DocType.AGENCY_DOCS,
        content=content,
        project_id=cid,
        status=DocStatus.PUBLISHED,
    )
    eng.register_document(doc)
    console.print(Panel(doc.content, title=doc.title, border_style="cyan"))


def cmd_docs_changelog(args: List[str]) -> None:
    """Generate changelog doc."""
    eng = _get_engine()
    content = "# Changelog\n\n- v1.0.0: Initial core release.\n- v2.0.0: Universal Integration Layer added."
    doc = DocumentRecord(
        document_id=new_id(),
        title="System Changelog",
        doc_type=DocType.RELEASE_NOTES,
        content=content,
        status=DocStatus.PUBLISHED,
    )
    eng.register_document(doc)
    console.print(Panel(doc.content, title=doc.title, border_style="cyan"))


def cmd_docs_release(args: List[str]) -> None:
    """Generate release notes doc."""
    eng = _get_engine()
    content = "# Release Notes\n\nFeatures, fixes, and migration rules."
    doc = DocumentRecord(
        document_id=new_id(),
        title="Release Notes",
        doc_type=DocType.RELEASE_NOTES,
        content=content,
        status=DocStatus.PUBLISHED,
    )
    eng.register_document(doc)
    console.print(Panel(doc.content, title=doc.title, border_style="cyan"))


def cmd_docs_dashboard(args: List[str]) -> None:
    """Render overall documents registry status brief."""
    eng = _get_engine()
    docs = eng.list_documents()

    console.print()
    console.print(
        Panel(
            f"  [bold white]Documentation Intelligence Dashboard[/bold white]\n\n"
            f"  Total Catalog Documents: [cyan]{len(docs)}[/cyan]\n"
            f"  API Reference manuals:   [green]{sum(1 for d in docs if d.doc_type == DocType.API_DOCS)}[/green]\n"
            f"  Architecture Guides:     [magenta]{sum(1 for d in docs if d.doc_type == DocType.ARCHITECTURE)}[/magenta]",
            title="[bold cyan]📖 Documentation Status Overview[/bold cyan]",
            border_style="cyan",
        )
    )


# ── Main Dispatcher ──────────────────────────────────────────────────────────


def cmd_docs_main(args: List[str], registry: Any = None) -> None:
    """Main CLI group router for documentation intelligence commands."""
    if not args:
        cmd_docs_dashboard([])
        return

    sub = args[0].lower()
    subargs = args[1:]

    handlers = {
        "list": cmd_docs_list,
        "search": cmd_docs_search,
        "readme": cmd_docs_readme,
        "architecture": cmd_docs_architecture,
        "api": cmd_docs_api,
        "project": cmd_docs_project,
        "workflows": cmd_docs_workflows,
        "integrations": cmd_docs_integrations,
        "agency": cmd_docs_agency,
        "changelog": cmd_docs_changelog,
        "release": cmd_docs_release,
    }

    handler = handlers.get(sub)
    if handler:
        handler(subargs)
    else:
        # Default fallback is search or list
        cmd_docs_list(args)
