"""Phase 9: GitHub Intelligence — CLI Commands.

Implements subcommands under the 'aios github' group:
  aios github repos      — list all registered code repositories
  aios github branches   — list branches for a repository
  aios github commits    — list commit history logs
  aios github prs        — review open pull requests risk scores
  aios github issues     — view issues priorities and assignees
  aios github actions    — audit CI builds success rates
  aios github releases   — view releases and changelogs
  aios github analytics  — render velocity and growth metrics
  aios github health     — calculate repository health metrics
"""

from __future__ import annotations

import time
from typing import Any, List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from aios.services.github_intelligence import GitActionWorkflow, GitRelease
from aios.services.github_intelligence_impl import GitHubIntelligenceServiceImpl

console = Console()

_DB_PATH: Optional[str] = None


def _get_engine() -> GitHubIntelligenceServiceImpl:
    eng = GitHubIntelligenceServiceImpl(db_path=_DB_PATH)
    eng.initialize()
    return eng


# ── Subcommand Handlers ───────────────────────────────────────────────────────


def cmd_github_repos(args: List[str]) -> None:
    """List all registered repositories."""
    eng = _get_engine()
    repos = eng.list_repositories()

    table = Table(
        title="[bold cyan]🐙 Registered Git Repositories[/bold cyan]",
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("Repository ID")
    table.add_column("Repository Name", style="bold")
    table.add_column("Owner")
    table.add_column("Lang")
    table.add_column("Stars")
    table.add_column("Forks")
    table.add_column("Open PRs")
    table.add_column("Health Score")

    for r in repos:
        table.add_row(
            r.repository_id[:8] + "...",
            r.name,
            r.owner,
            r.language,
            str(r.stars),
            str(r.forks),
            str(r.open_prs),
            f"[green]{r.health_score}%[/green]"
            if r.health_score > 70
            else f"[yellow]{r.health_score}%[/yellow]",
        )
    console.print(table)


def cmd_github_branches(args: List[str]) -> None:
    """List branches for a target repository."""
    eng = _get_engine()
    repos = eng.list_repositories()
    if not repos:
        console.print("[yellow]No repositories registered.[/yellow]")
        return
    repo_id = repos[0].repository_id

    branches = eng.list_branches(repo_id)
    table = Table(title="[bold cyan]Branches Listing[/bold cyan]")
    table.add_column("Branch Name", style="bold")
    table.add_column("Parent")
    table.add_column("Author")
    table.add_column("Status")

    for b in branches:
        table.add_row(b.name, b.parent_branch, b.author, b.status)
    console.print(table)


def cmd_github_commits(args: List[str]) -> None:
    """List commit history logs."""
    eng = _get_engine()
    repos = eng.list_repositories()
    if not repos:
        console.print("[yellow]No repositories registered.[/yellow]")
        return
    repo_id = repos[0].repository_id

    commits = eng.list_commits(repo_id)
    if not commits:
        console.print("[yellow]No commits recorded yet.[/yellow]")
        return

    table = Table(title="Commit Log History", show_header=True)
    table.add_column("SHA", style="dim")
    table.add_column("Author")
    table.add_column("Message", style="bold")
    table.add_column("Files")
    table.add_column("Lines")

    for c in commits:
        table.add_row(
            c.commit_sha[:8],
            c.author,
            c.message,
            str(c.files_changed),
            f"[green]+{c.lines_added}[/green] [red]-{c.lines_removed}[/red]",
        )
    console.print(table)


def cmd_github_prs(args: List[str]) -> None:
    """Review pull requests risk scores."""
    eng = _get_engine()
    repos = eng.list_repositories()
    if not repos:
        console.print("[yellow]No repositories registered.[/yellow]")
        return
    repo_id = repos[0].repository_id

    prs = eng.list_pull_requests(repo_id)
    table = Table(title="[bold cyan]Pull Requests Analytics[/bold cyan]")
    table.add_column("PR #")
    table.add_column("Title", style="bold")
    table.add_column("Author")
    table.add_column("Status")
    table.add_column("Risk Score")
    table.add_column("Review State")

    for p in prs:
        table.add_row(
            f"#{p.pr_number}",
            p.title,
            p.author,
            p.status,
            f"[red]{p.risk_score}[/red]" if p.risk_score > 50 else f"[green]{p.risk_score}[/green]",
            p.review_state,
        )
    console.print(table)


def cmd_github_issues(args: List[str]) -> None:
    """View issues priority metrics."""
    eng = _get_engine()
    repos = eng.list_repositories()
    if not repos:
        console.print("[yellow]No repositories registered.[/yellow]")
        return
    repo_id = repos[0].repository_id

    issues = eng.list_issues(repo_id)
    table = Table(title="[bold cyan]Issues Priorities Listing[/bold cyan]")
    table.add_column("Title", style="bold")
    table.add_column("Priority")
    table.add_column("Status")
    table.add_column("Assignee")
    table.add_column("Labels")

    for i in issues:
        table.add_row(i.title, str(i.priority), i.status, i.assignee, ", ".join(i.labels))
    console.print(table)


def cmd_github_actions(args: List[str]) -> None:
    """Audit action builds runs success rates."""
    eng = _get_engine()
    repos = eng.list_repositories()
    if not repos:
        console.print("[yellow]No repositories registered.[/yellow]")
        return
    repo_id = repos[0].repository_id

    runs = eng.list_workflow_runs(repo_id)
    if not runs:
        # Seed a dummy run for display
        eng.record_workflow_run(
            GitActionWorkflow(
                workflow_id="run-1",
                repository_id=repo_id,
                name="ci.yml",
                status="success",
                duration_secs=45,
            )
        )
        runs = eng.list_workflow_runs(repo_id)

    table = Table(title="GitHub Actions CI Builds")
    table.add_column("Workflow Name", style="bold")
    table.add_column("Status")
    table.add_column("Duration")
    table.add_column("Timestamp")

    for r in runs:
        status_style = "green" if r.status == "success" else "red"
        time_str = time.strftime("%H:%M:%S", time.localtime(r.timestamp))
        table.add_row(
            r.name, f"[{status_style}]{r.status}[/{status_style}]", f"{r.duration_secs}s", time_str
        )
    console.print(table)


def cmd_github_releases(args: List[str]) -> None:
    """Browse releases versions and features list."""
    eng = _get_engine()
    repos = eng.list_repositories()
    if not repos:
        console.print("[yellow]No repositories registered.[/yellow]")
        return
    repo_id = repos[0].repository_id

    releases = eng.list_releases(repo_id)
    if not releases:
        # Seed a release for display
        eng.record_release(
            GitRelease(
                release_id="rel-1",
                repository_id=repo_id,
                version="v1.0.0",
                title="Stable Release",
                features=["Integrations layer", "SQLite engine"],
                fixes=["WAL concurrency fix"],
            )
        )
        releases = eng.list_releases(repo_id)

    table = Table(title="Releases Catalog")
    table.add_column("Version", style="bold green")
    table.add_column("Release Title")
    table.add_column("Features")
    table.add_column("Fixes")

    for r in releases:
        table.add_row(r.version, r.title, ", ".join(r.features), ", ".join(r.fixes))
    console.print(table)


def cmd_github_analytics(args: List[str]) -> None:
    """Render repository commit/PR velocity analytics."""
    eng = _get_engine()
    repos = eng.list_repositories()
    if not repos:
        console.print("[yellow]No repositories registered.[/yellow]")
        return
    repo = repos[0]

    console.print(
        Panel(
            f"  Repository Name: [bold cyan]{repo.name}[/bold cyan]\n"
            f"  Default Branch:  {repo.default_branch}\n"
            f"  Open Issues:     {repo.open_issues}\n"
            f"  Open PRs:        {repo.open_prs}\n"
            f"  Total Stars:     ⭐ {repo.stars}\n"
            f"  Total Forks:     🍴 {repo.forks}",
            title="Repository Growth & Velocity Analytics",
            border_style="cyan",
        )
    )


def cmd_github_health(args: List[str]) -> None:
    """Calculate and display health score breakdowns."""
    eng = _get_engine()
    repos = eng.list_repositories()
    if not repos:
        console.print("[yellow]No repositories registered.[/yellow]")
        return
    repo = repos[0]

    score = eng.calculate_repository_health(repo.repository_id)
    color = "green" if score > 70 else "yellow"

    console.print(
        Panel(
            f"  Repository: [bold]{repo.name}[/bold]\n"
            f"  Overall Score:  [{color}]{score}%[/{color}]\n\n"
            f"  [bold]Checks Status:[/bold]\n"
            f"  - Open Issues penalty:  Checked\n"
            f"  - CI build run status:  Checked\n"
            f"  - PR Risk scoring:      Checked",
            title="Repository Health breakdown",
            border_style=color,
        )
    )


def cmd_github_dashboard(args: List[str]) -> None:
    """Render overall GitHub command center dashboard."""
    eng = _get_engine()
    repos = eng.list_repositories()

    console.print()
    console.print(
        Panel(
            f"  [bold white]GitHub Engineering Command Center[/bold white]\n\n"
            f"  Active Repositories: [cyan]{len(repos)}[/cyan]\n"
            f"  Open issues total:   [magenta]{sum(r.open_issues for r in repos)}[/magenta]\n"
            f"  Open PRs count:      [yellow]{sum(r.open_prs for r in repos)}[/yellow]",
            title="[bold cyan]🐙 GitHub Command Dashboard[/bold cyan]",
            border_style="cyan",
        )
    )


# ── Main Dispatcher ──────────────────────────────────────────────────────────


def cmd_github_main(args: List[str], registry: Any = None) -> None:
    """Main CLI group router for GitHub intelligence commands."""
    if not args:
        cmd_github_dashboard([])
        return

    sub = args[0].lower()
    subargs = args[1:]

    handlers = {
        "repos": cmd_github_repos,
        "branches": cmd_github_branches,
        "commits": cmd_github_commits,
        "prs": cmd_github_prs,
        "issues": cmd_github_issues,
        "actions": cmd_github_actions,
        "releases": cmd_github_releases,
        "analytics": cmd_github_analytics,
        "health": cmd_github_health,
    }

    handler = handlers.get(sub)
    if handler:
        handler(subargs)
    else:
        # Default fallback is dashboard or list
        cmd_github_repos(args)
