"""
aios/local/cli_commands.py

CLI command handlers for `aios models` subcommand group.

Implements all Phase 1 CLI commands:
  aios models
  aios models list
  aios models status
  aios models benchmark
  aios models doctor
  aios models load
  aios models unload
  aios models registry

Commands use Rich for beautiful terminal output.
"""

from __future__ import annotations

from typing import Any, List

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

console = Console()


def _get_local_service(registry: Any = None) -> Any:
    """
    Retrieves the LocalModelService from the service registry, or
    creates a standalone instance if no registry is provided.
    """
    if registry is not None:
        try:
            from aios.local.service import LocalModelService

            return registry.get(LocalModelService)
        except Exception:
            pass

    # Standalone mode
    from aios.local.service import LocalModelService

    svc = LocalModelService()
    svc.initialize()
    return svc


def cmd_models_list(args: List[str], registry: Any = None) -> None:
    """
    aios models list

    Lists all installed Ollama models with metadata and capabilities.
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]Discovering local models..."),
        transient=True,
        console=console,
    ) as progress:
        progress.add_task("discover", total=None)
        svc = _get_local_service(registry)
        models = svc.discover_models(force=True)

    if not models:
        console.print(
            Panel(
                "[yellow]No local models found.\n"
                "Run: [bold]ollama pull <model>[/bold] to install models.",
                title="[bold red]No Models Found",
                border_style="red",
            )
        )
        return

    table = Table(
        title=f"[bold cyan]Local Ollama Models[/bold cyan] — {len(models)} installed",
        border_style="cyan",
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("Model Name", style="bold white", min_width=25)
    table.add_column("Type", style="cyan", justify="center")
    table.add_column("Size", justify="right", style="green")
    table.add_column("Context", justify="right")
    table.add_column("Status", justify="center")
    table.add_column("Capabilities", style="dim", max_width=40)

    running = svc.discovery.get_running_models()

    for m in models:
        is_running = m.name in running
        status_icon = "[bold green]● RUNNING[/bold green]" if is_running else "[dim]○ idle[/dim]"
        size_str = f"{m.size_gb} GB"
        context_str = f"{m.context_length:,}"

        role = svc.capability_registry.get_role(m.name)
        caps = ", ".join(c.value for c in role.capabilities[:3]) if role else "—"
        if role and len(role.capabilities) > 3:
            caps += f" +{len(role.capabilities) - 3}"

        type_style = (
            "[bold yellow]EMBED[/bold yellow]"
            if m.is_embedding_model
            else "[bold blue]CHAT[/bold blue]"
        )

        table.add_row(
            m.name,
            type_style,
            size_str,
            context_str,
            status_icon,
            caps,
        )

    console.print()
    console.print(table)
    console.print()


def cmd_models_status(args: List[str], registry: Any = None) -> None:
    """
    aios models status

    Shows detailed health status for all models.
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]Refreshing model health..."),
        transient=True,
        console=console,
    ) as progress:
        progress.add_task("health", total=None)
        svc = _get_local_service(registry)
        statuses = svc.get_health_status()

    if not statuses:
        console.print("[yellow]No model health data available. Run: aios models list[/yellow]")
        return

    table = Table(
        title="[bold cyan]Model Health Status[/bold cyan]",
        border_style="cyan",
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("Model", style="bold white", min_width=25)
    table.add_column("Status", justify="center")
    table.add_column("Health", justify="right")
    table.add_column("RAM (MB)", justify="right")
    table.add_column("Latency", justify="right")
    table.add_column("TPS", justify="right")
    table.add_column("Requests", justify="right")
    table.add_column("Failures", justify="right")
    table.add_column("Last Used", justify="right")

    for name, h in sorted(statuses.items()):
        status_text = {
            "running": "[bold green]RUNNING[/bold green]",
            "installed": "[blue]installed[/blue]",
            "unloaded": "[dim]unloaded[/dim]",
            "missing": "[red]MISSING[/red]",
            "error": "[bold red]ERROR[/bold red]",
        }.get(h.status.value, h.status.value)

        health_score = f"{h.health_score:.0f}/100"
        health_color = (
            "green" if h.health_score >= 70 else ("yellow" if h.health_score >= 40 else "red")
        )

        ram_str = f"{h.ram_mb:.0f}" if h.ram_mb > 0 else "—"
        latency_str = f"{h.avg_latency_ms:.0f}ms" if h.avg_latency_ms > 0 else "—"
        tps_str = f"{h.tokens_per_second:.1f}" if h.tokens_per_second > 0 else "—"
        requests_str = str(h.total_requests)
        failures_str = f"[red]{h.failure_count}[/red]" if h.failure_count > 0 else "0"

        if h.last_used_ago_seconds is not None:
            ago = h.last_used_ago_seconds
            if ago < 60:
                last_used = f"{ago:.0f}s ago"
            elif ago < 3600:
                last_used = f"{ago / 60:.0f}m ago"
            else:
                last_used = f"{ago / 3600:.1f}h ago"
        else:
            last_used = "never"

        table.add_row(
            name,
            status_text,
            f"[{health_color}]{health_score}[/{health_color}]",
            ram_str,
            latency_str,
            tps_str,
            requests_str,
            failures_str,
            last_used,
        )

    console.print()
    console.print(table)

    # Summary
    running = [n for n, h in statuses.items() if h.running]
    installed = [n for n, h in statuses.items() if h.installed]
    if running:
        console.print(f"\n[bold green]Currently running:[/bold green] {', '.join(running)}")
    console.print(f"[dim]Total: {len(installed)} installed, {len(running)} running[/dim]\n")


def cmd_models_benchmark(args: List[str], registry: Any = None) -> None:
    """
    aios models benchmark [model_name] [--all] [--fresh]

    Runs benchmarks and displays results.
    """
    model_name = None
    run_all = "--all" in args
    fresh = "--fresh" in args

    # Extract model name from args (first non-flag argument)
    for arg in args:
        if not arg.startswith("--"):
            model_name = arg
            break

    svc = _get_local_service(registry)

    if model_name or run_all:
        skip_existing = not fresh
        console.print(
            Panel(
                f"[bold]Benchmarking {'all models' if run_all else model_name}...[/bold]\n"
                f"[dim]This may take several minutes per model.[/dim]\n"
                f"[dim]{'Skipping already-benchmarked models.' if skip_existing else 'Running fresh benchmarks.'}[/dim]",
                title="[bold cyan]Benchmark Engine[/bold cyan]",
                border_style="cyan",
            )
        )

        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            console=console,
        ) as progress:
            if run_all:
                models = svc.discover_models()
                chat_models = [m.name for m in models if not m.is_embedding_model]
                for mname in chat_models:
                    task = progress.add_task(f"Benchmarking {mname}...", total=None)
                    try:
                        svc.benchmark_engine.benchmark_model(mname, unload_after=True)
                    except Exception as exc:
                        console.print(f"[red]  ✗ {mname}: {exc}[/red]")
                    finally:
                        progress.remove_task(task)
                svc._apply_benchmark_scores_to_registry()
            else:
                task = progress.add_task(f"Benchmarking {model_name}...", total=None)
                try:
                    svc.benchmark_engine.benchmark_model(model_name, unload_after=True)
                    svc._apply_benchmark_scores_to_registry()
                except Exception as exc:
                    console.print(f"[red]✗ Benchmark failed: {exc}[/red]")
                finally:
                    progress.remove_task(task)

    # Display results
    results = svc.get_benchmark_results()
    if not results:
        console.print("[yellow]No benchmark results yet. Run:[/yellow] aios models benchmark --all")
        return

    ranked = sorted(results.values(), key=lambda r: r.composite_score, reverse=True)

    table = Table(
        title="[bold cyan]Benchmark Results[/bold cyan]",
        border_style="cyan",
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("Rank", justify="center", style="bold yellow")
    table.add_column("Model", style="bold white", min_width=25)
    table.add_column("Score", justify="right", style="bold green")
    table.add_column("Latency (avg)", justify="right")
    table.add_column("Latency (p95)", justify="right")
    table.add_column("TPS", justify="right")
    table.add_column("Quality", justify="right")
    table.add_column("Success Rate", justify="right")

    for rank, result in enumerate(ranked, 1):
        score_color = (
            "green"
            if result.composite_score >= 50
            else ("yellow" if result.composite_score >= 25 else "red")
        )
        table.add_row(
            f"#{rank}",
            result.model_name,
            f"[{score_color}]{result.composite_score:.1f}[/{score_color}]",
            f"{result.avg_latency_ms:.0f}ms",
            f"{result.p95_latency_ms:.0f}ms",
            f"{result.avg_tokens_per_second:.1f}",
            f"{result.avg_quality_score:.2%}",
            f"{result.success_rate:.1%}",
        )

    console.print()
    console.print(table)
    console.print()


def cmd_models_doctor(args: List[str], registry: Any = None) -> None:
    """
    aios models doctor

    Runs comprehensive health diagnostics.
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]Running diagnostics..."),
        transient=True,
        console=console,
    ) as progress:
        progress.add_task("doctor", total=None)
        svc = _get_local_service(registry)
        report = svc.run_doctor()

    ollama_icon = (
        "[bold green]✓ ONLINE[/bold green]"
        if report["ollama_online"]
        else "[bold red]✗ OFFLINE[/bold red]"
    )

    console.print()
    console.print(
        Panel(
            f"Ollama Daemon: {ollama_icon}\n"
            f"Models Installed: [bold]{report['installed_count']}[/bold]\n"
            f"Models Running: [bold green]{report['running_count']}[/bold green]",
            title="[bold cyan]AI OS Health Report[/bold cyan]",
            border_style="cyan",
        )
    )

    if report.get("missing_expected"):
        console.print(
            Panel(
                "\n".join(f"[red]✗ {m}[/red]" for m in report["missing_expected"]),
                title="[bold red]Missing Expected Models[/bold red]",
                border_style="red",
            )
        )

    if report.get("model_health"):
        table = Table(
            title="[bold]Per-Model Diagnostics[/bold]",
            border_style="blue",
            header_style="bold",
        )
        table.add_column("Model", style="bold white", min_width=20)
        table.add_column("Status")
        table.add_column("Score", justify="right")
        table.add_column("Failures", justify="right")
        table.add_column("Success Rate", justify="right")

        for name, h in sorted(report["model_health"].items()):
            s = h["status"]
            status_icon = {
                "running": "[bold green]● running[/bold green]",
                "installed": "[blue]installed[/blue]",
                "unloaded": "[dim]unloaded[/dim]",
                "missing": "[bold red]MISSING[/bold red]",
            }.get(s, s)
            score = h["health_score"]
            score_color = "green" if score >= 70 else ("yellow" if score >= 40 else "red")
            failures = h["failure_count"]
            fail_str = f"[red]{failures}[/red]" if failures > 0 else "0"
            sr = h["success_rate"]
            sr_color = "green" if sr >= 0.9 else ("yellow" if sr >= 0.7 else "red")

            table.add_row(
                name,
                status_icon,
                f"[{score_color}]{score:.0f}[/{score_color}]",
                fail_str,
                f"[{sr_color}]{sr:.1%}[/{sr_color}]",
            )

        console.print(table)

    if report.get("recommendations"):
        console.print(
            Panel(
                "\n".join(report["recommendations"]),
                title="[bold yellow]Recommendations[/bold yellow]",
                border_style="yellow",
            )
        )
    else:
        console.print("[bold green]✓ All systems healthy[/bold green]\n")


def cmd_models_load(args: List[str], registry: Any = None) -> None:
    """
    aios models load <model_name>

    Loads a model into memory.
    """
    if not args:
        console.print("[red]Usage: aios models load <model_name>[/red]")
        return

    model_name = args[0]
    svc = _get_local_service(registry)

    with Progress(
        SpinnerColumn(),
        TextColumn(f"[bold blue]Loading {model_name}..."),
        transient=True,
        console=console,
    ) as progress:
        progress.add_task("load", total=None)
        result = svc.load_model(model_name)

    if result.success:
        console.print(
            f"[bold green]✓ Model loaded:[/bold green] {model_name} "
            f"[dim]({result.load_time_ms:.0f} ms)[/dim]"
        )
    else:
        console.print(
            Panel(
                f"[red]Failed to load model: {model_name}[/red]\n[dim]Error: {result.error}[/dim]",
                border_style="red",
            )
        )


def cmd_models_unload(args: List[str], registry: Any = None) -> None:
    """
    aios models unload [model_name]

    Unloads the active model (or a specified model) from memory.
    """
    svc = _get_local_service(registry)
    model_name = args[0] if args else None

    active = svc.loader.active_model
    target = model_name or active

    if not target:
        console.print("[yellow]No model is currently loaded.[/yellow]")
        return

    with Progress(
        SpinnerColumn(),
        TextColumn(f"[bold blue]Unloading {target}..."),
        transient=True,
        console=console,
    ) as progress:
        progress.add_task("unload", total=None)
        success = svc.unload_model(target)

    if success:
        console.print(f"[bold green]✓ Model unloaded:[/bold green] {target}")
    else:
        console.print(f"[red]✗ Failed to unload model: {target}[/red]")


def cmd_models_registry(args: List[str], registry: Any = None) -> None:
    """
    aios models registry

    Shows the full model capability registry.
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]Loading registry..."),
        transient=True,
        console=console,
    ) as progress:
        progress.add_task("registry", total=None)
        svc = _get_local_service(registry)
        info = svc.get_model_registry_info()

    table = Table(
        title="[bold cyan]Model Capability Registry[/bold cyan]",
        border_style="cyan",
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("Model", style="bold white", min_width=25)
    table.add_column("Type", justify="center")
    table.add_column("Size", justify="right")
    table.add_column("Context", justify="right")
    table.add_column("Priority", justify="center")
    table.add_column("Score", justify="right")
    table.add_column("Capabilities", style="dim")
    table.add_column("Description", style="italic", max_width=35)

    for item in sorted(info, key=lambda x: x.get("priority", 50)):
        type_icon = "[yellow]EMBED[/yellow]" if item["type"] == "embedding" else "[blue]CHAT[/blue]"
        score = item.get("benchmark_score")
        score_str = f"{score:.1f}" if score is not None else "[dim]—[/dim]"
        caps = ", ".join(item["capabilities"][:4])
        if len(item["capabilities"]) > 4:
            caps += f" +{len(item['capabilities']) - 4}"

        table.add_row(
            item["name"],
            type_icon,
            f"{item['size_gb']} GB",
            f"{item['context_length']:,}",
            str(item["priority"]),
            score_str,
            caps or "—",
            item["description"] or "—",
        )

    console.print()
    console.print(table)
    console.print()


def cmd_models_main(args: List[str], registry: Any = None) -> None:
    """
    aios models [subcommand]

    Dispatches to the appropriate models subcommand.
    Without a subcommand, defaults to 'list'.
    """
    if not args:
        cmd_models_list([], registry)
        return

    subcommand = args[0].lower()
    subargs = args[1:]

    handlers = {
        "list": cmd_models_list,
        "status": cmd_models_status,
        "benchmark": cmd_models_benchmark,
        "doctor": cmd_models_doctor,
        "load": cmd_models_load,
        "unload": cmd_models_unload,
        "registry": cmd_models_registry,
    }

    handler = handlers.get(subcommand)
    if handler:
        handler(subargs, registry)
    else:
        console.print(
            Panel(
                "[bold]Available commands:[/bold]\n"
                "  [cyan]aios models[/cyan]              — List all installed models\n"
                "  [cyan]aios models list[/cyan]         — List all installed models\n"
                "  [cyan]aios models status[/cyan]       — Show health status for all models\n"
                "  [cyan]aios models benchmark[/cyan]    — Benchmark models (--all, --fresh, <name>)\n"
                "  [cyan]aios models doctor[/cyan]       — Run full health diagnostics\n"
                "  [cyan]aios models load <name>[/cyan]  — Load a specific model\n"
                "  [cyan]aios models unload[/cyan]       — Unload the active model\n"
                "  [cyan]aios models registry[/cyan]     — Show the capability registry",
                title="[bold cyan]aios models — Local Model Commands[/bold cyan]",
                border_style="cyan",
            )
        )
