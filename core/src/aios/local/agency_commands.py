"""Phase 6: Agency Intelligence — CLI Commands.

Implements all agency subcommands:
  aios agency dashboard     — main agency summary and analytics
  aios agency leads         — leads pipeline list, promote, create
  aios agency clients       — client portfolio list
  aios agency companies     — registered company records
  aios agency meetings      — meeting scheduler and notes Sync
  aios agency proposals     — proposal generation and Accept
  aios agency pipeline      — revenue pipeline metrics
  aios agency outreach      — outreach generation and follow-up templates
  aios agency followups     — active follow-ups, alerts for overdue
"""

from __future__ import annotations

import logging
import time
from typing import Any, List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from aios.services.agency import (
    Company,
    Contact,
    Lead,
    LeadPriority,
    LeadStage,
    ProposalType,
    new_id,
)
from aios.services.agency_impl import AgencyCRMServiceImpl

logger = logging.getLogger(__name__)
console = Console()

_DB_PATH: Optional[str] = None


def _get_crm() -> AgencyCRMServiceImpl:
    svc = AgencyCRMServiceImpl(db_path=_DB_PATH)
    svc.initialize()
    return svc


# ── Formatting Helpers ────────────────────────────────────────────────────────


def _stage_color(stage: LeadStage) -> str:
    colors = {
        LeadStage.NEW: "cyan",
        LeadStage.QUALIFIED: "blue",
        LeadStage.CONTACTED: "yellow",
        LeadStage.MEETING_SCHEDULED: "magenta",
        LeadStage.PROPOSAL_SENT: "orange3",
        LeadStage.NEGOTIATION: "purple",
        LeadStage.WON: "green",
        LeadStage.LOST: "red",
    }
    return colors.get(stage, "white")


# ── Subcommand Handlers ───────────────────────────────────────────────────────


def cmd_agency_dashboard(args: List[str]) -> None:
    """Show the overall Agency CRM Dashboard."""
    crm = _get_crm()
    leads = crm.list_leads()
    proposals = crm.list_proposals()
    clients = crm.list_clients()
    followups = crm.list_followups(status="pending")
    pipe = crm.get_revenue_pipeline()

    console.print()
    console.print(
        Panel(
            f"  [bold white]AI OS Agency Intelligence Command Center[/bold white]\n\n"
            f"  Active Leads: [cyan]{len(leads)}[/cyan]  |  "
            f"Closed Clients: [green]{len(clients)}[/green]  |  "
            f"Active Proposals: [magenta]{len(proposals)}[/magenta]\n"
            f"  Pipeline Expected Value: [green]${pipe['expected_revenue']:,.2f}[/green]\n"
            f"  Pipeline Health Score: [bold green]{pipe['pipeline_health']}%[/bold green]  |  "
            f"Pending Follow-Ups: [yellow]{len(followups)}[/yellow]",
            title="[bold cyan]🏢 Agency Operating System[/bold cyan]",
            border_style="cyan",
        )
    )

    # 1. Pipeline Summary
    pipe_table = Table(title="[bold green]Revenue Forecast[/bold green]", box=None)
    pipe_table.add_column("Category")
    pipe_table.add_column("Value", justify="right")
    pipe_table.add_row("Expected Revenue (weighted)", f"${pipe['expected_revenue']:,.2f}")
    pipe_table.add_row("Closed Revenue", f"${pipe['closed_revenue']:,.2f}")
    pipe_table.add_row("Total Pipeline Value", f"${pipe['lead_value']:,.2f}")
    console.print(pipe_table)

    # 2. Key Follow-Ups
    if followups:
        f_table = Table(title="[bold yellow]Pending Follow-Ups[/bold yellow]", box=None)
        f_table.add_column("Task")
        f_table.add_column("Due Date")
        for f in followups[:3]:
            due_str = time.strftime("%Y-%m-%d", time.localtime(f.due_date))
            status_str = "[red]OVERDUE[/red]" if f.due_date < time.time() else "Pending"
            f_table.add_row(f.title, f"{due_str} ({status_str})")
        console.print(f_table)


def cmd_agency_leads(args: List[str]) -> None:
    """List, create, or modify Lead Pipeline stages."""
    crm = _get_crm()

    if args and args[0] == "create":
        # aios agency leads create <company_name> <contact_name> <email> <title> <value>
        if len(args) < 6:
            console.print(
                "[red]Usage: aios agency leads create <company> <contact> <email> <title> <value>[/red]"
            )
            return

        company_name = args[1]
        contact_name = args[2]
        email = args[3]
        title = args[4]
        try:
            val = float(args[5])
        except ValueError:
            val = 5000.0

        # Create or fetch company & contact
        companies = crm.list_companies()
        company = next((c for c in companies if c.name.lower() == company_name.lower()), None)
        if not company:
            company = Company(company_id=new_id(), name=company_name)
            crm.create_company(company)

        contacts = crm.list_contacts()
        contact = next((c for c in contacts if c.email.lower() == email.lower()), None)
        if not contact:
            contact = Contact(
                contact_id=new_id(), name=contact_name, email=email, company_id=company.company_id
            )
            crm.create_contact(contact)

        lead = Lead(
            lead_id=new_id(),
            company_id=company.company_id,
            contact_id=contact.contact_id,
            title=title,
            stage=LeadStage.NEW,
            priority=LeadPriority.MEDIUM,
            score=60,
            expected_value=val,
            next_action="Send Discovery Outreach",
        )
        crm.create_lead(lead)

        # KG Bridge Sync
        try:
            from aios.services.agency_graph_bridge import AgencyGraphBridge
            from aios.services.graph_impl import GraphServiceImpl
            from aios.services.graph_query import GraphQueryEngine

            graph_svc = GraphServiceImpl()
            graph_svc.initialize()
            engine = GraphQueryEngine(graph_svc)
            bridge = AgencyGraphBridge(engine)
            bridge.sync_lead(title, val, "medium")
            bridge.sync_contact(contact)
            bridge.sync_company(company)
            bridge.link_contact_to_company(contact_name, company_name)
            graph_svc.shutdown()
        except Exception:
            pass

        console.print(f"[green]✓ Lead created successfully for [bold]{company_name}[/bold].[/green]")
        return

    # Default: List leads
    leads = crm.list_leads()
    table = Table(
        title="[bold cyan]💼 Lead Pipeline[/bold cyan]",
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("Title")
    table.add_column("Company")
    table.add_column("Contact")
    table.add_column("Stage")
    table.add_column("Score")
    table.add_column("Value")
    table.add_column("Next Action")

    for l in leads:
        company = crm.get_company(l.company_id)
        contact = crm.get_contact(l.contact_id)
        sc = _stage_color(l.stage)
        table.add_row(
            l.title,
            company.name if company else "—",
            contact.name if contact else "—",
            f"[{sc}]{l.stage.value}[/{sc}]",
            str(l.score),
            f"${l.expected_value:,.2f}",
            l.next_action or "—",
        )
    console.print(table)


def cmd_agency_clients(args: List[str]) -> None:
    """Show client registry."""
    crm = _get_crm()
    clients = crm.list_clients()

    table = Table(
        title="[bold green]📁 Agency Client Portfolio[/bold green]",
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("Client / Company")
    table.add_column("Status")
    table.add_column("Projects")
    table.add_column("Invoices Count")
    table.add_column("Contracts Count")

    for cl in clients:
        company = crm.get_company(cl.company_id)
        cname = company.name if company else "Unknown Company"
        table.add_row(
            cname,
            cl.status.value,
            ", ".join(cl.projects) or "—",
            str(len(cl.invoices)),
            str(len(cl.contracts)),
        )
    console.print(table)


def cmd_agency_companies(args: List[str]) -> None:
    """Registered companies listing."""
    crm = _get_crm()
    companies = crm.list_companies()

    table = Table(
        title="[bold cyan]🏢 Registered Companies[/bold cyan]",
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("Company Name")
    table.add_column("Industry")
    table.add_column("Location")
    table.add_column("Size")
    table.add_column("Client Status")

    for c in companies:
        table.add_row(
            c.name,
            c.industry or "—",
            c.location or "—",
            c.size or "—",
            c.client_status,
        )
    console.print(table)


def cmd_agency_meetings(args: List[str]) -> None:
    """Retrieve and display meeting records."""
    crm = _get_crm()
    meetings = crm.list_meetings()

    table = Table(
        title="[bold cyan]📅 Meeting Intelligence Logs[/bold cyan]",
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("Title")
    table.add_column("Start Time")
    table.add_column("Duration")
    table.add_column("Decisions")
    table.add_column("Action Items")

    for m in meetings:
        start_str = time.strftime("%Y-%m-%d %H:%M", time.localtime(m.start_time))
        decisions_str = ", ".join(m.decisions) or "—"
        actions_str = ", ".join(item.get("task", "") for item in m.action_items) or "—"
        table.add_row(
            m.title,
            start_str,
            f"{m.duration_min} min",
            decisions_str,
            actions_str,
        )
    console.print(table)


def cmd_agency_proposals(args: List[str]) -> None:
    """Proposals view and auto-draft creator."""
    crm = _get_crm()

    if args and args[0] == "generate":
        # aios agency proposals generate <lead_id> <type>
        if len(args) < 3:
            console.print("[red]Usage: aios agency proposals generate <lead_id> <type>[/red]")
            return
        lid = args[1]
        ptype_str = args[2]
        try:
            ptype = ProposalType(ptype_str)
        except ValueError:
            ptype = ProposalType.AUTOMATION

        prop = crm.generate_proposal_draft(lid, ptype)

        # Sync Proposal to Knowledge Graph
        try:
            from aios.services.agency_graph_bridge import AgencyGraphBridge
            from aios.services.graph_impl import GraphServiceImpl
            from aios.services.graph_query import GraphQueryEngine

            graph_svc = GraphServiceImpl()
            graph_svc.initialize()
            engine = GraphQueryEngine(graph_svc)
            bridge = AgencyGraphBridge(engine)
            bridge.sync_proposal(prop)
            lead = crm.get_lead(lid)
            if lead:
                bridge.link_proposal_to_lead(prop.title, lead.title)
            graph_svc.shutdown()
        except Exception:
            pass

        console.print(
            Panel(
                f"[bold green]✓ Proposal Draft Generated[/bold green]\n\n"
                f"  ID:      {prop.proposal_id}\n"
                f"  Title:   {prop.title}\n"
                f"  Value:   ${prop.value:,.2f}\n\n"
                f"{prop.content[:200]}...",
                title="Proposal Draft",
                border_style="green",
            )
        )
        return

    # List proposals
    proposals = crm.list_proposals()
    table = Table(
        title="[bold magenta]📄 Proposal Engine Documents[/bold magenta]",
        show_header=True,
    )
    table.add_column("Proposal ID")
    table.add_column("Title")
    table.add_column("Type")
    table.add_column("Status")
    table.add_column("Value")

    for p in proposals:
        table.add_row(
            p.proposal_id[:8] + "...",
            p.title,
            p.proposal_type.value,
            p.status.value,
            f"${p.value:,.2f}",
        )
    console.print(table)


def cmd_agency_pipeline(args: List[str]) -> None:
    """Display revenue forecast detail."""
    crm = _get_crm()
    pipe = crm.get_revenue_pipeline()

    console.print(
        Panel(
            f"  Weighted Expected Revenue: [bold green]${pipe['expected_revenue']:,.2f}[/bold green]\n"
            f"  Total Active Lead Pipeline: [bold cyan]${pipe['lead_value']:,.2f}[/bold cyan]\n"
            f"  Current Closed Revenue:     [bold green]${pipe['closed_revenue']:,.2f}[/bold green]\n"
            f"  Pipeline Health Score:      [bold magenta]{pipe['pipeline_health']}%[/bold magenta]",
            title="[bold cyan]💰 Revenue Pipeline & Forecast[/bold cyan]",
            border_style="green",
        )
    )


def cmd_agency_outreach(args: List[str]) -> None:
    """Generate cold email, discovery or follow-up outreach logs."""
    crm = _get_crm()

    if args and args[0] == "generate":
        # aios agency outreach generate <lead_id> <outreach_type>
        if len(args) < 3:
            console.print("[red]Usage: aios agency outreach generate <lead_id> <type>[/red]")
            return
        lid = args[1]
        otype_str = args[2]

        from aios.services.agency import OutreachType

        try:
            otype = OutreachType(otype_str)
        except ValueError:
            otype = OutreachType.COLD_EMAIL

        out = crm.generate_outreach_draft(lid, otype)
        console.print(
            Panel(
                f"[bold green]✓ Outreach Draft Generated[/bold green]\n\n"
                f"  Subject: {out.subject}\n\n"
                f"{out.body}",
                title="Outreach Draft",
                border_style="green",
            )
        )
        return

    # List outreach
    outreaches = crm.list_outreach()
    table = Table(
        title="[bold cyan]📨 Outreach Campaign Logs[/bold cyan]",
        show_header=True,
    )
    table.add_column("Outreach ID")
    table.add_column("Type")
    table.add_column("Status")
    table.add_column("Subject")

    for o in outreaches:
        table.add_row(
            o.outreach_id[:8] + "...",
            o.outreach_type.value,
            o.status.value,
            o.subject or "—",
        )
    console.print(table)


def cmd_agency_followups(args: List[str]) -> None:
    """Render follow-up actions and highlight overdue alerts."""
    crm = _get_crm()

    if args and args[0] == "complete":
        if len(args) < 2:
            console.print("[red]Usage: aios agency followups complete <followup_id>[/red]")
            return
        fid = args[1]
        fol = crm.get_followup(fid)
        if not fol:
            console.print("[red]Follow-up not found.[/red]")
            return
        fol.status = "completed"
        crm.create_followup(fol)
        console.print("[green]✓ Follow-up marked completed.[/green]")
        return

    followups = crm.list_followups()
    table = Table(
        title="[bold yellow]🔔 Follow-Up Action Schedule[/bold yellow]",
        show_header=True,
    )
    table.add_column("ID")
    table.add_column("Title")
    table.add_column("Target Type")
    table.add_column("Due Date")
    table.add_column("Status")

    for f in followups:
        due_str = time.strftime("%Y-%m-%d", time.localtime(f.due_date))
        status_str = f.status.upper()
        if f.due_date < time.time() and f.status == "pending":
            status_str = "[bold red]OVERDUE[/bold red]"
        elif f.status == "completed":
            status_str = "[green]COMPLETED[/green]"

        table.add_row(
            f.followup_id[:8] + "...",
            f.title,
            f.target_type,
            due_str,
            status_str,
        )
    console.print(table)


# ── Main Dispatcher ──────────────────────────────────────────────────────────


def cmd_agency_main(args: List[str], registry: Any = None) -> None:
    """Dispatches command strings from main CLI router to agency subcomponents."""
    if not args:
        cmd_agency_dashboard([])
        return

    sub = args[0].lower()
    subargs = args[1:]

    handlers = {
        "dashboard": cmd_agency_dashboard,
        "leads": cmd_agency_leads,
        "clients": cmd_agency_clients,
        "companies": cmd_agency_companies,
        "meetings": cmd_agency_meetings,
        "proposals": cmd_agency_proposals,
        "pipeline": cmd_agency_pipeline,
        "outreach": cmd_agency_outreach,
        "followups": cmd_agency_followups,
    }

    handler = handlers.get(sub)
    if handler:
        handler(subargs)
    else:
        # Default fallback to dashboard or show usage
        console.print(
            Panel(
                "[bold]Available agency CRM commands:[/bold]\n\n"
                "  [cyan]aios agency dashboard[/cyan]      — main summary and analytics\n"
                "  [cyan]aios agency leads[/cyan]          — display or create leads\n"
                "  [cyan]aios agency clients[/cyan]        — view clients list\n"
                "  [cyan]aios agency companies[/cyan]      — list company directories\n"
                "  [cyan]aios agency meetings[/cyan]       — display meeting schedule & items\n"
                "  [cyan]aios agency proposals[/cyan]      — generate or review proposals\n"
                "  [cyan]aios agency pipeline[/cyan]       — display revenue projections\n"
                "  [cyan]aios agency outreach[/cyan]       — draft Cold Emails / LinkedIn updates\n"
                "  [cyan]aios agency followups[/cyan]      — highlight alerts & pending actions",
                title="[bold cyan]aios agency — CRM Operating Center[/bold cyan]",
                border_style="cyan",
            )
        )
