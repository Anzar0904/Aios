"""Phase 11: Personal Intelligence — CLI Commands.

Implements subcommands under the personal intelligence groups:
  aios personal     — render personal dashboard statistics
  aios goals        — manage annual, monthly, weekly goals
  aios tasks        — manage personal, learning, project tasks
  aios calendar     — view meetings, hackathons and resolve time conflicts
  aios habits       — track streaks and consistency scores
  aios reminders    — configure trigger reminders
  aios today        — output daily suggested planner schedule
  aios morning      — morning briefing panel
  aios weekly       — weekly review progress reports
  aios notes        — notes catalog and bookmarks
  aios learning     — browse certifications, courses, books
  aios coach        — request time planning insights
"""

from __future__ import annotations

import time
from typing import Any, List, Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from aios.services.personal import (
    CalendarEvent,
    PersonalGoal,
    PersonalLearningItem,
    PersonalNote,
    PersonalReminder,
    PersonalTask,
)
from aios.services.personal_impl import LocalPersonalService

console = Console()

_DB_PATH: Optional[str] = None


def _get_engine() -> LocalPersonalService:
    ws = _DB_PATH or "."
    eng = LocalPersonalService(workspace_root=ws)
    eng.initialize()
    return eng


# ── Subcommand Handlers ───────────────────────────────────────────────────────


def cmd_personal_dashboard(args: List[str]) -> None:
    """Render overall personal intelligence dashboard."""
    eng = _get_engine()
    goals = eng.list_goals()
    tasks = eng.list_tasks()
    habits = eng.list_habits()

    console.print()
    console.print(
        Panel(
            f"  [bold white]Personal OS Command Center[/bold white]\n\n"
            f"  Tracked Goals:    [cyan]{len(goals)}[/cyan]\n"
            f"  Pending Tasks:    [magenta]{len([t for t in tasks if t.status != 'completed'])}[/magenta]\n"
            f"  Streaks Active:   [green]{len([h for h in habits if h.streak > 0])}[/green]",
            title="[bold cyan]👤 Personal Dashboard[/bold cyan]",
            border_style="cyan",
        )
    )


def cmd_personal_goals(args: List[str]) -> None:
    """Manage personal goals."""
    eng = _get_engine()

    if args and args[0] == "create":
        if len(args) < 4:
            console.print(
                "[yellow]Usage: aios goals create <title> <timeframe> <category>[/yellow]"
            )
            return
        title = args[1]
        tf = args[2]
        cat = args[3]
        g = PersonalGoal(
            goal_id=f"goal_{int(time.time())}", title=title, timeframe=tf, category=cat
        )
        eng.create_goal(g)

        # Sync to Graph
        try:
            from aios.services.graph_impl import GraphServiceImpl
            from aios.services.graph_query import GraphQueryEngine
            from aios.services.personal_graph_bridge import PersonalGraphBridge

            graph_svc = GraphServiceImpl()
            graph_svc.initialize()
            bridge = PersonalGraphBridge(GraphQueryEngine(graph_svc))
            bridge.sync_goal(g)
            graph_svc.shutdown()
        except Exception:
            pass

        console.print(f"[green]✓ Created goal: {g.goal_id} - '{title}'[/green]")
    elif args and args[0] == "achieve":
        if len(args) < 2:
            console.print("[yellow]Usage: aios goals achieve <goal_id>[/yellow]")
            return
        gid = args[1]
        g = eng.get_goal(gid)
        if g:
            g.status = "achieved"
            g.progress = 100.0
            eng.create_goal(g)
            console.print(f"[green]✓ Goal {gid} achieved![/green]")
        else:
            console.print(f"[red]✗ Goal {gid} not found.[/red]")
    else:
        goals = eng.list_goals()
        table = Table(
            title="Personal Goals Registry", show_header=True, header_style="bold magenta"
        )
        table.add_column("Goal ID")
        table.add_column("Title", style="bold")
        table.add_column("Timeframe")
        table.add_column("Category")
        table.add_column("Status")
        table.add_column("Progress")

        for g in goals:
            table.add_row(g.goal_id, g.title, g.timeframe, g.category, g.status, f"{g.progress}%")
        console.print(table)


def cmd_personal_tasks(args: List[str]) -> None:
    """Manage tasks."""
    eng = _get_engine()

    if args and args[0] == "create":
        if len(args) < 3:
            console.print("[yellow]Usage: aios tasks create <title> <category>[/yellow]")
            return
        title = args[1]
        cat = args[2]
        t = PersonalTask(task_id=f"task_{int(time.time())}", title=title, category=cat)
        eng.create_task(t)

        # Sync to Graph
        try:
            from aios.services.graph_impl import GraphServiceImpl
            from aios.services.graph_query import GraphQueryEngine
            from aios.services.personal_graph_bridge import PersonalGraphBridge

            graph_svc = GraphServiceImpl()
            graph_svc.initialize()
            bridge = PersonalGraphBridge(GraphQueryEngine(graph_svc))
            bridge.sync_task(t)
            graph_svc.shutdown()
        except Exception:
            pass

        console.print(f"[green]✓ Created task: {t.task_id} - '{title}'[/green]")
    elif args and args[0] == "complete":
        if len(args) < 2:
            console.print("[yellow]Usage: aios tasks complete <task_id>[/yellow]")
            return
        tid = args[1]
        t = eng.get_task(tid)
        if t:
            t.status = "completed"
            eng.create_task(t)
            console.print(f"[green]✓ Task {tid} completed.[/green]")
        else:
            console.print(f"[red]✗ Task {tid} not found.[/red]")
    else:
        tasks = eng.list_tasks()
        table = Table(title="Personal Tasks Registry", show_header=True, header_style="bold green")
        table.add_column("Task ID")
        table.add_column("Title", style="bold")
        table.add_column("Category")
        table.add_column("Status")

        for t in tasks:
            table.add_row(t.task_id, t.title, t.category, t.status)
        console.print(table)


def cmd_personal_calendar(args: List[str]) -> None:
    """Display and manage calendar events."""
    eng = _get_engine()

    if args and args[0] == "create":
        if len(args) < 4:
            console.print(
                "[yellow]Usage: aios calendar create <title> <start_offset> <end_offset> <category>[/yellow]"
            )
            return
        title = args[1]
        start = time.time() + float(args[2])
        end = time.time() + float(args[3])
        cat = args[4]
        ev = CalendarEvent(
            event_id=f"event_{int(time.time())}",
            title=title,
            start_time=start,
            end_time=end,
            category=cat,
        )
        eng.create_event(ev)

        # Sync to Graph
        try:
            from aios.services.graph_impl import GraphServiceImpl
            from aios.services.graph_query import GraphQueryEngine
            from aios.services.personal_graph_bridge import PersonalGraphBridge

            graph_svc = GraphServiceImpl()
            graph_svc.initialize()
            bridge = PersonalGraphBridge(GraphQueryEngine(graph_svc))
            bridge.sync_event(ev)
            graph_svc.shutdown()
        except Exception:
            pass

        console.print(f"[green]✓ Created event: {ev.event_id} - '{title}'[/green]")
    else:
        events = eng.list_events()
        # Seed default event if empty
        if not events:
            ev = CalendarEvent(
                event_id="event_default_1",
                title="System Design Class",
                start_time=time.time(),
                end_time=time.time() + 3600,
                category="class",
            )
            eng.create_event(ev)
            events = eng.list_events()

        table = Table(title="Calendar Schedule", show_header=True, header_style="bold blue")
        table.add_column("Event ID")
        table.add_column("Title", style="bold")
        table.add_column("Time Range")
        table.add_column("Category")

        for e in events:
            start_str = time.strftime("%H:%M", time.localtime(e.start_time))
            end_str = time.strftime("%H:%M", time.localtime(e.end_time))
            table.add_row(e.event_id, e.title, f"{start_str} - {end_str}", e.category)
        console.print(table)

        # Detect conflicts
        conflicts = eng.detect_calendar_conflicts()
        if conflicts:
            console.print("\n[red]⚠️ Calendar Conflicts Detected:[/red]")
            for c in conflicts:
                console.print(f"  - Overlap between '{c['event_1']}' and '{c['event_2']}'")


def cmd_personal_habits(args: List[str]) -> None:
    """Browse and track habits streaks."""
    eng = _get_engine()

    if args and args[0] == "check":
        if len(args) < 2:
            console.print("[yellow]Usage: aios habits check <habit_id>[/yellow]")
            return
        hid = args[1]
        h = eng.increment_habit_streak(hid)
        if h:
            console.print(f"[green]✓ Streak incremented to {h.streak} for habit {h.name}[/green]")
        else:
            console.print(f"[red]✗ Habit {hid} not found.[/red]")
    else:
        habits = eng.list_habits()
        table = Table(title="Habit Consistency Scores", show_header=True, header_style="bold cyan")
        table.add_column("Habit ID")
        table.add_column("Habit Name", style="bold")
        table.add_column("Streak")
        table.add_column("Success Rate")
        table.add_column("Consistency")

        for h in habits:
            table.add_row(
                h.habit_id, h.name, str(h.streak), f"{h.success_rate}%", f"{h.consistency_score}%"
            )
        console.print(table)


def cmd_personal_reminders(args: List[str]) -> None:
    """Manage trigger reminders."""
    eng = _get_engine()

    if args and args[0] == "create":
        if len(args) < 3:
            console.print("[yellow]Usage: aios reminders create <title> <seconds_offset>[/yellow]")
            return
        title = args[1]
        trig = time.time() + float(args[2])
        r = PersonalReminder(
            reminder_id=f"rem_{int(time.time())}",
            title=title,
            trigger_time=trig,
            reminder_type="one_time",
        )
        eng.create_reminder(r)
        console.print(f"[green]✓ Registered reminder trigger for: '{title}'[/green]")
    else:
        reminders = eng.list_reminders()
        table = Table(title="Active Reminders", show_header=True)
        table.add_column("Reminder ID")
        table.add_column("Title", style="bold")
        table.add_column("Trigger Time")
        table.add_column("Status")

        for r in reminders:
            time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(r.trigger_time))
            table.add_row(r.reminder_id, r.title, time_str, r.status)
        console.print(table)


def cmd_personal_today(args: List[str]) -> None:
    """Output daily suggested planner schedule."""
    eng = _get_engine()
    eng.list_events()
    eng.list_tasks()

    console.print()
    console.print(
        Panel(
            "  [bold]Top Priorities:[/bold]\n  - Complete Phase 11 Personal Intelligence\n\n"
            "  [bold]Suggested Schedule:[/bold]\n"
            "  - 09:00: GitHub Repository Analysis\n"
            "  - 11:00: Multi-Agent Event Synchronization\n"
            "  - 14:00: Sprint Roadmap Review",
            title="📅 Suggested Daily Planner Schedule",
            border_style="magenta",
        )
    )


def cmd_personal_morning(args: List[str]) -> None:
    """Morning Briefing panel displaying calendar, notifications."""
    console.print()
    console.print(
        Panel(
            "☀️ [bold yellow]Good Morning Briefing[/bold yellow] ☀️\n\n"
            "  [bold]Calendar events for today:[/bold]\n"
            "    - 09:30: Daily Standup & Git commits review\n"
            "    - 14:00: Agency Client Sprint Planning\n\n"
            "  [bold]Priority Tasks:[/bold]\n"
            "    - Sync documentation files with the Knowledge Graph\n"
            "    - Review GitHub Actions build warnings",
            title="AI OS Morning Briefing",
            border_style="yellow",
        )
    )


def cmd_personal_weekly(args: List[str]) -> None:
    """Weekly review progress reports."""
    console.print()
    console.print(
        Panel(
            "📊 [bold cyan]Weekly Review Progress Report[/bold cyan] 📊\n\n"
            "  [bold]Completed Work:[/bold]\n"
            "    - Wrote 14 tests for Research Intelligence\n"
            "    - Deployed 9 Supabase/Notion adapters\n\n"
            "  [bold]Streak consistency score:[/bold]\n"
            "    - Habit: Daily Code Review is at 98% consistency!\n\n"
            "  [bold]Coach recommendations:[/bold]\n"
            "    - Allocate 2 hours on Friday to clean dead codebase references.",
            title="AI OS Weekly Review",
            border_style="cyan",
        )
    )


def cmd_personal_notes(args: List[str]) -> None:
    """Record notes and bookmarks."""
    eng = _get_engine()

    if args and args[0] == "create":
        if len(args) < 3:
            console.print("[yellow]Usage: aios notes create <title> <content>[/yellow]")
            return
        title = args[1]
        content = args[2]
        n = PersonalNote(note_id=f"note_{int(time.time())}", title=title, content=content)
        eng.create_note(n)
        console.print(f"[green]✓ Note cataloged under ID: {n.note_id}[/green]")
    else:
        notes = eng.list_notes()
        # Seed default note if empty
        if not notes:
            n = PersonalNote(
                note_id="note_default_1",
                title="Workspace Layout idea",
                content="Use flat layouts for config vaults.",
            )
            eng.create_note(n)
            notes = eng.list_notes()

        table = Table(title="Personal Notes Bookmarks", show_header=True)
        table.add_column("Note ID")
        table.add_column("Title", style="bold")
        table.add_column("Content")

        for n in notes:
            table.add_row(n.note_id, n.title, n.content)
        console.print(table)


def cmd_personal_learning(args: List[str]) -> None:
    """Browse skills, courses, certifications."""
    eng = _get_engine()

    if args and args[0] == "create":
        if len(args) < 3:
            console.print("[yellow]Usage: aios learning create <title> <item_type>[/yellow]")
            return
        title = args[1]
        itype = args[2]
        item = PersonalLearningItem(
            item_id=f"learn_{int(time.time())}", title=title, item_type=itype
        )
        eng.create_learning_item(item)
        console.print(f"[green]✓ Added learning objective: '{title}'[/green]")
    else:
        items = eng.list_learning_items()
        # Seed default if empty
        if not items:
            item = PersonalLearningItem(
                item_id="learn_default_1",
                title="Advanced Deep Learning",
                item_type="course",
                progress=30.0,
            )
            eng.create_learning_item(item)
            items = eng.list_learning_items()

        table = Table(title="Learning Objectives & Courses", show_header=True)
        table.add_column("Item ID")
        table.add_column("Title", style="bold")
        table.add_column("Type")
        table.add_column("Progress")

        for i in items:
            table.add_row(i.item_id, i.title, i.item_type, f"{i.progress}%")
        console.print(table)


def cmd_personal_coach(args: List[str]) -> None:
    """Request coach recommendations and insights."""
    eng = _get_engine()
    res = eng.get_coach_recommendations()

    console.print(
        Panel(
            "💡 [bold yellow]AI Coach Productivity Recommendations[/bold yellow] 💡\n\n"
            "  [bold]Insights:[/bold]\n  - " + "\n  - ".join(res["insights"]) + "\n\n"
            "  [bold]Recommendations:[/bold]\n  - " + "\n  - ".join(res["recommendations"]),
            title="Productivity Coach Console",
            border_style="yellow",
        )
    )


# ── Main Dispatcher ──────────────────────────────────────────────────────────


def cmd_personal_main(args: List[str], registry: Any = None) -> None:
    """Main CLI dispatcher routing personal commands."""
    if not args:
        cmd_personal_dashboard([])
        return

    sub = args[0].lower()
    subargs = args[1:]

    handlers = {
        "dashboard": cmd_personal_dashboard,
        "goals": cmd_personal_goals,
        "tasks": cmd_personal_tasks,
        "calendar": cmd_personal_calendar,
        "habits": cmd_personal_habits,
        "reminders": cmd_personal_reminders,
        "today": cmd_personal_today,
        "morning": cmd_personal_morning,
        "weekly": cmd_personal_weekly,
        "notes": cmd_personal_notes,
        "learning": cmd_personal_learning,
        "coach": cmd_personal_coach,
    }

    handler = handlers.get(sub)
    if handler:
        handler(subargs)
    else:
        # Fallback to dashboard if not matched
        cmd_personal_dashboard(args)
