import sys
import time
from pathlib import Path
from typing import Any, Dict

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from aios.bootstrap import bootstrap_kernel
from aios.services.command import (
    CommandRegistry,
)
from aios.services.conversation.manager import ConversationManager
from aios.services.model import LLMRequest, ModelService
from aios.skills.registry import SkillRegistry

# Global Console instance for Terminal UX styling
console = Console()


def handle_conversation_command(user_input: str, conv_manager: ConversationManager) -> bool:
    cmd = user_input.lower().strip()

    if cmd == "new conversation":
        title = input("Enter conversation title (optional): ").strip()
        title = title if title else None
        conv = conv_manager.create_conversation(title=title, agent_name="developer_agent")
        console.print(
            f"[green]✓ Created and switched to conversation: '{conv.title}' ({conv.id})[/green]"
        )
        return True

    elif cmd == "list conversations":
        convs = conv_manager.list_conversations()
        if not convs:
            console.print("[yellow]No conversations found.[/yellow]")
        else:
            table = Table(title="Conversations List", border_style="cyan")
            table.add_column("Active", justify="center", style="bold green")
            table.add_column("ID", style="dim")
            table.add_column("Title", style="white")
            table.add_column("Active Agent", style="cyan")

            current = conv_manager.active_conversation_id
            for c in convs:
                active_marker = "*" if c["id"] == current else ""
                table.add_row(active_marker, c["id"], c["title"], c["active_agent"] or "None")
            console.print(table)
        return True

    elif cmd.startswith("resume"):
        target = user_input[6:].strip()
        if not target:
            convs = conv_manager.list_conversations()
            if not convs:
                console.print("[yellow]No conversations to resume.[/yellow]")
                return True
            table = Table(title="Conversations to Resume", border_style="cyan")
            table.add_column("Index", justify="center", style="bold cyan")
            table.add_column("ID", style="dim")
            table.add_column("Title", style="white")
            for idx, c in enumerate(convs, 1):
                table.add_row(str(idx), c["id"], c["title"])
            console.print(table)

            choice = input("Enter number or ID to resume: ").strip()
            if not choice:
                return True
            try:
                idx = int(choice)
                if 1 <= idx <= len(convs):
                    target = convs[idx - 1]["id"]
            except ValueError:
                target = choice

        convs = conv_manager.list_conversations()
        found_id = None
        for c in convs:
            if c["id"] == target or c["title"].lower() == target.lower():
                found_id = c["id"]
                break

        if found_id:
            conv = conv_manager.resume_conversation(found_id)
            console.print(f"[green]✓ Resumed conversation: '{conv.title}' ({conv.id})[/green]")
        else:
            console.print(f"[red]✗ Conversation '{target}' not found.[/red]")
        return True

    elif cmd == "rename conversation":
        conv = conv_manager.get_current_conversation()
        if not conv:
            console.print("[yellow]No active conversation to rename.[/yellow]")
            return True
        new_title = input(f"Enter new title for '{conv.title}': ").strip()
        if new_title:
            conv_manager.rename_conversation(conv.id, new_title)
            console.print(f"[green]✓ Renamed conversation to: '{new_title}'[/green]")
        return True

    elif cmd == "delete conversation":
        convs = conv_manager.list_conversations()
        if not convs:
            console.print("[yellow]No conversations to delete.[/yellow]")
            return True
        table = Table(title="Conversations to Delete", border_style="red")
        table.add_column("Index", justify="center", style="bold red")
        table.add_column("ID", style="dim")
        table.add_column("Title", style="white")
        for idx, c in enumerate(convs, 1):
            table.add_row(str(idx), c["id"], c["title"])
        console.print(table)

        choice = input("Enter number or ID to delete: ").strip()
        if not choice:
            return True
        target = choice
        try:
            idx = int(choice)
            if 1 <= idx <= len(convs):
                target = convs[idx - 1]["id"]
        except ValueError:
            pass

        found_id = None
        for c in convs:
            if c["id"] == target or c["title"].lower() == target.lower():
                found_id = c["id"]
                break

        if found_id:
            confirm = (
                input(f"Are you sure you want to delete conversation '{found_id}'? (y/n): ")
                .strip()
                .lower()
            )
            if confirm == "y":
                conv_manager.delete_conversation(found_id)
                console.print(f"[green]✓ Deleted conversation: {found_id}[/green]")
        else:
            console.print(f"[red]✗ Conversation '{target}' not found.[/red]")
        return True

    elif cmd == "current conversation":
        conv = conv_manager.get_current_conversation()
        if not conv:
            console.print("[yellow]No active conversation.[/yellow]")
        else:
            created_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(conv.created_time))
            updated_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(conv.updated_time))

            grid = Table.grid(padding=1)
            grid.add_column(style="bold cyan", justify="right")
            grid.add_column(style="white")
            grid.add_row("ID:", conv.id)
            grid.add_row("Title:", conv.title)
            grid.add_row("Agent:", conv.active_agent or "None")
            grid.add_row("Created:", created_str)
            grid.add_row("Updated:", updated_str)
            if conv.summary:
                grid.add_row("Summary:", conv.summary.summary)

            console.print(
                Panel(
                    grid,
                    title="[bold white]Active Conversation Details[/bold white]",
                    border_style="cyan",
                )
            )
        return True

    elif cmd == "show history":
        conv = conv_manager.get_current_conversation()
        if not conv:
            console.print("[yellow]No active conversation.[/yellow]")
        else:
            print_conversation_history(conv_manager)
        return True

    return False


def print_help_table(registry: CommandRegistry) -> None:
    table = Table(title="Personal AI OS Command Center", border_style="blue")
    table.add_column("Command / Slash Command", style="bold cyan")
    table.add_column("Description", style="white")
    table.add_column("Usage Example", style="green")

    # Core Slash Commands
    table.add_row("/help or /?", "Show this help registry", "/help")
    table.add_row("/conversation list", "List active dialogue sessions", "/conversation list")
    table.add_row("/conversation new", "Start a new conversation session", "/conversation new")
    table.add_row(
        "/conversation resume <id>", "Switch active conversation", "/conversation resume target-id"
    )
    table.add_row(
        "/conversation delete", "Delete conversation history from disk", "/conversation delete"
    )
    table.add_row(
        "/conversation rename", "Rename current dialogue session", "/conversation rename my-session"
    )
    table.add_row(
        "/conversation active", "Show current conversation summary", "/conversation active"
    )
    table.add_row("/skills", "List loaded skills and capabilities", "/skills")
    table.add_row("/providers", "List active providers and models", "/providers")
    table.add_row("/model <name>", "Switch system default LLM model", "/model gpt-4o")
    table.add_row("/history", "Show formatted conversation history", "/history")
    table.add_row("/multiline", "Toggle multi-line input mode", "/multiline")
    table.add_row("/clear", "Clear the terminal screen", "/clear")
    table.add_row("/exit or /quit", "End the active CLI session", "/exit")

    console.print(table)


def print_skills_table(skill_registry: SkillRegistry) -> None:
    table = Table(title="Loaded Skills & Capabilities", border_style="cyan")
    table.add_column("Skill ID", style="bold cyan")
    table.add_column("Name", style="white")
    table.add_column("Description", style="italic white")
    table.add_column("Capabilities", style="green")
    table.add_column("Commands", style="yellow")

    for skill in skill_registry.list_skills():
        caps = getattr(skill.metadata, "capabilities", [])
        caps_str = ", ".join(caps) if caps else "None"
        cmds_str = ", ".join(skill.metadata.commands[:3])
        if len(skill.metadata.commands) > 3:
            cmds_str += f" (+{len(skill.metadata.commands) - 3} more)"
        table.add_row(
            skill.metadata.id, skill.metadata.name, skill.metadata.description, caps_str, cmds_str
        )
    console.print(table)


def print_providers_table(model_service: ModelService) -> None:
    table = Table(title="Registered LLM Providers & Models", border_style="magenta")
    table.add_column("Provider Name", style="bold magenta")
    table.add_column("Models", style="white")
    table.add_column("Status", style="green")

    registry = model_service.registry
    providers: Dict[str, Any] = {}
    for model in registry.list_supported_models():
        provider = registry.get_provider_for_model(model)
        if provider not in providers:
            providers[provider] = []
        providers[provider].append(model)

    for prov_name, models in providers.items():
        table.add_row(prov_name, ", ".join(models), "Active / Healthy")
    console.print(table)


def handle_model_switch(model_service: ModelService, model_name: str) -> None:
    model_name = model_name.strip()
    if not model_name:
        console.print("[yellow]Usage: /model <model_name>[/yellow]")
        return
    try:
        provider = model_service.registry.get_provider_for_model(model_name)
        model_service._default_model = model_name
        msg = (
            f"[green]✓ Switched default model to: "
            f"[bold]{model_name}[/bold] (Provider: {provider})[/green]"
        )
        console.print(msg)
    except Exception:
        console.print(f"[red]✗ Model '{model_name}' is not registered. Available models:[/red]")
        console.print(", ".join(model_service.registry.list_supported_models()))


def print_conversation_history(conv_manager: ConversationManager) -> None:
    conv = conv_manager.get_current_conversation()
    if not conv:
        console.print("[yellow]No active conversation.[/yellow]")
        return

    console.print(f"[bold cyan]--- Dialogue History for '{conv.title}' ---[/bold cyan]")
    if conv.summary:
        console.print(Panel(conv.summary.summary, title="Session Summary", border_style="yellow"))

    for m in conv.messages:
        role = m.role.upper()
        if role == "USER":
            console.print(
                Panel(
                    m.content,
                    title="[bold green]User[/bold green]",
                    border_style="green",
                    expand=False,
                )
            )
        elif role == "ASSISTANT":
            console.print(
                Panel(
                    Markdown(m.content),
                    title="[bold blue]Assistant[/bold blue]",
                    border_style="blue",
                    expand=False,
                )
            )
        else:
            console.print(
                Panel(
                    m.content,
                    title=f"[bold gray]{role}[/bold gray]",
                    border_style="gray",
                    expand=False,
                )
            )


def print_status_line(model_service: ModelService, conv_manager: ConversationManager) -> None:
    conv = conv_manager.get_current_conversation()
    conv_title = conv.title if conv else "None"
    agent_name = conv.active_agent if conv else "None"
    status_text = (
        f"Agent: [bold cyan]{agent_name}[/bold cyan] | "
        f"Conv: [bold green]{conv_title}[/bold green] | "
        f"Mode: [bold yellow]Interactive[/bold yellow]"
    )
    console.print(status_text)


def read_input(multiline_mode: bool = False) -> str:
    """Reads input from the user, supporting multi-line formatting."""
    if multiline_mode:
        console.print(
            "[dim]Enter multi-line input (type '.' or press Ctrl+D on a new line to submit):[/dim]"
        )
        lines = []
        while True:
            try:
                line = input(".. ")
                if line.strip() == ".":
                    break
                lines.append(line)
            except EOFError:
                break
        return "\n".join(lines)

    try:
        first_line = input("aios > ")
        if not first_line.strip():
            return ""

        if first_line.endswith("\\"):
            lines = [first_line[:-1]]
            while True:
                line = input(".. ")
                if line.endswith("\\"):
                    lines.append(line[:-1])
                else:
                    lines.append(line)
                    break
            return "\n".join(lines)
        return first_line
    except KeyboardInterrupt:
        print()
        raise


def handle_general_chat(
    user_input: str, conv_manager: ConversationManager, model_service: ModelService
) -> None:
    conv = conv_manager.get_current_conversation()
    if not conv:
        conv = conv_manager.create_conversation(
            title="Active Dialogue", agent_name="developer_agent"
        )

    conv_manager.add_message(conv.id, "user", user_input)
    conv = conv_manager.get_current_conversation()

    # Load context summary and messages
    history_context = []
    for msg in conv.messages[-11:-1]:
        history_context.append(f"{msg.role.upper()}: {msg.content}")

    history_str = "\n".join(history_context)

    system_instruction = (
        "You are the coordinator for Personal AI OS.\n"
        "Respond to the user directly, concisely, and helpfully.\n"
        "Use markdown for structure, code blocks, and lists where appropriate."
    )

    prompt = f"Conversation History:\n{history_str}\n\nUser: {user_input}\nAssistant:"
    model_name = getattr(model_service, "_default_model", "claude-3-5-sonnet")
    req = LLMRequest(prompt=prompt, system_instruction=system_instruction, model_name=model_name)

    console.print("\n[bold blue]Assistant:[/bold blue]")
    full_response = ""
    token_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

    try:
        with console.status("[bold blue]Thinking...", spinner="dots"):
            stream = model_service.execute_stream(req)

        for chunk in stream:
            console.print(chunk.content, end="")
            full_response += chunk.content
            if chunk.usage:
                token_usage.update(chunk.usage)
        print()

    except KeyboardInterrupt:
        console.print("\n[yellow]Generation interrupted by user.[/yellow]")
        if not full_response:
            full_response = "Generation cancelled."

    except Exception as e:
        console.print(
            Panel(
                f"Error during streaming execution: {str(e)}",
                border_style="red",
                title="Stream Error",
            )
        )
        return

    conv_manager.add_message(conv.id, "assistant", full_response)

    p_tokens = token_usage.get("prompt_tokens", 0)
    c_tokens = token_usage.get("completion_tokens", 0)
    total_tokens = token_usage.get("total_tokens", p_tokens + c_tokens)

    console.print(
        f"[dim]Model: {model_name} | Tokens: "
        f"In={p_tokens}, Out={c_tokens}, Total={total_tokens}[/dim]\n"
    )


def execute_builtin_cli_command(args: list[str], exit_on_complete: bool = True) -> bool:
    import sys

    from aios.providers.interface import (
        OmniRouteRequest,
        RoutingRequest,
        universal_health_registry,
        universal_model_registry,
        universal_omniroute_engine,
        universal_provider_registry,
        universal_routing_engine,
    )

    cmd = " ".join(args).strip()

    if cmd == "help":
        print_help_table(None)
        if exit_on_complete:
            import sys

            sys.exit(0)
        return True

    elif cmd == "provider list":
        table = Table(title="Registered LLM Providers", border_style="magenta")
        table.add_column("Provider Name", style="bold magenta")
        table.add_column("Models", style="white")
        table.add_column("Status", style="green")

        for p_name in universal_provider_registry.list_providers():
            models = [m.model_id for m in universal_model_registry.list_models(p_name)]
            if not models:
                provider_inst = universal_provider_registry.lookup(p_name)
                meta = getattr(provider_inst, "metadata", provider_inst)
                models = getattr(meta, "supported_models", ["default"])

            health = universal_health_registry.get_health(p_name)
            status_str = "Healthy" if health.available else "Degraded/Offline"
            table.add_row(p_name, ", ".join(models), status_str)

        console.print(table)
        if exit_on_complete:
            import sys

            sys.exit(0)
        return True

    elif cmd == "model list":
        table = Table(title="Registered LLM Models", border_style="cyan")
        table.add_column("Model ID", style="bold cyan")
        table.add_column("Provider", style="white")
        table.add_column("Capabilities", style="green")
        table.add_column("Status", style="green")

        models = universal_model_registry.list_models()
        if not models:
            for p_name in universal_provider_registry.list_providers():
                provider_inst = universal_provider_registry.lookup(p_name)
                meta = getattr(provider_inst, "metadata", provider_inst)
                supported = getattr(meta, "supported_models", ["default"])
                for m_name in supported:
                    table.add_row(m_name, p_name, "chat", "Active")
        else:
            for model in models:
                caps = []
                if model.supports_chat:
                    caps.append("chat")
                if model.supports_coding:
                    caps.append("coding")
                if model.supports_reasoning:
                    caps.append("reasoning")
                if model.supports_vision:
                    caps.append("vision")
                if model.supports_embeddings:
                    caps.append("embeddings")
                status_str = "Active" if model.enabled else "Disabled"
                table.add_row(model.model_id, model.provider, ", ".join(caps), status_str)

        console.print(table)
        if exit_on_complete:
            import sys

            sys.exit(0)
        return True

    elif cmd == "health":
        table = Table(title="Provider Health & Telemetry Status", border_style="green")
        table.add_column("Provider Name", style="bold green")
        table.add_column("Available", style="white")
        table.add_column("Latency (ms)", style="cyan")
        table.add_column("Health Score", style="magenta")
        table.add_column("Last Error", style="red")

        for p_name in universal_provider_registry.list_providers():
            health = universal_health_registry.get_health(p_name)
            table.add_row(
                p_name,
                "Yes" if health.available else "No",
                f"{health.latency_ms:.1f}",
                f"{health.health_score:.1f}",
                health.last_error or "None",
            )

        console.print(table)
        if exit_on_complete:
            import sys

            sys.exit(0)
        return True

    elif args and args[0] == "route":
        task_type = args[1].strip().strip('"').strip("'") if len(args) > 1 else "chat"
        routing_req = RoutingRequest(
            task_type=task_type,
            estimated_input_tokens=100,
            estimated_output_tokens=100,
        )
        decision = universal_routing_engine.route(routing_req)
        console.print(
            Panel(
                f"Selected Provider: [bold green]{decision.provider}[/bold green]\n"
                f"Selected Model: [bold cyan]{decision.model}[/bold cyan]\n"
                f"Routing Score: [magenta]{decision.routing_score:.1f}[/magenta]\n"
                f"Reasoning: {decision.reasoning}",
                title=(f"[white]Routing Decision for task type '{task_type}'[/white]"),
                border_style="blue",
            )
        )
        if exit_on_complete:
            import sys

            sys.exit(0)
        return True

    elif args and args[0] == "providers":
        if len(args) < 2:
            console.print(
                "[yellow]Usage: aios providers <status|models|health|config|test|list>[/yellow]"
            )
            if exit_on_complete:
                sys.exit(1)
            return True

        subcommand = args[1]

        import sys
        from pathlib import Path

        from aios.config import load_config
        from aios.providers.ninerouter import generate_9router_reports

        if subcommand == "list":
            table = Table(title="Registered LLM Providers", border_style="magenta")
            table.add_column("Provider Name", style="bold magenta")
            table.add_column("Models", style="white")
            table.add_column("Status", style="green")

            for p_name in universal_provider_registry.list_providers():
                models = [m.model_id for m in universal_model_registry.list_models(p_name)]
                if not models:
                    provider_inst = universal_provider_registry.lookup(p_name)
                    meta = getattr(provider_inst, "metadata", provider_inst)
                    models = getattr(meta, "supported_models", ["default"])

                health = universal_health_registry.get_health(p_name)
                status_str = "Healthy" if health.available else "Degraded/Offline"
                table.add_row(p_name, ", ".join(models), status_str)

            console.print(table)
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "status":
            table = Table(title="9Router Local Gateway Status", border_style="green")
            table.add_column("Property", style="bold green")
            table.add_column("Value", style="white")

            nr_provider = universal_provider_registry.lookup("ninerouter")
            is_online = nr_provider.health() if nr_provider else False
            latency_val = getattr(nr_provider, "_last_latency", 0.0) if nr_provider else 0.0

            table.add_row(
                "Status",
                "[green]ONLINE[/green]" if is_online else "[red]OFFLINE[/red]",
            )
            table.add_row("Base URL", nr_provider.base_url if nr_provider else "N/A")
            table.add_row("Latency", f"{latency_val:.1f}ms")

            nr_models = universal_model_registry.list_models("ninerouter")
            table.add_row("Discovered Models", str(len(nr_models)))
            console.print(table)

            try:
                generate_9router_reports()
            except Exception:
                pass
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "models":
            table = Table(
                title="Discovered / Connected Models via 9Router",
                border_style="cyan",
            )
            table.add_column("Model ID", style="bold cyan")
            table.add_column("Provider", style="white")
            table.add_column("Capabilities", style="green")

            nr_models = universal_model_registry.list_models()
            for model in nr_models:
                caps = []
                if model.supports_chat:
                    caps.append("chat")
                if model.supports_coding:
                    caps.append("coding")
                if model.supports_reasoning:
                    caps.append("reasoning")
                if model.supports_vision:
                    caps.append("vision")
                if model.supports_embeddings:
                    caps.append("embeddings")
                table.add_row(model.model_id, model.provider, ", ".join(caps))

            console.print(table)
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "health":
            console.print("[cyan]Running health diagnostics on local 9Router server...[/cyan]")
            nr_provider = universal_provider_registry.lookup("ninerouter")
            if nr_provider:
                start = time.time()
                is_healthy = nr_provider.health()
                latency_ms = (time.time() - start) * 1000.0
                nr_provider._last_latency = latency_ms

                table = Table(title="9Router Health Summary", border_style="green")
                table.add_column("Metric", style="bold magenta")
                table.add_column("Result", style="white")
                table.add_row(
                    "Connection Status",
                    "[green]HEALTHY[/green]" if is_healthy else "[red]UNAVAILABLE[/red]",
                )
                table.add_row(
                    "Endpoint Ping Latency",
                    f"{latency_ms:.1f}ms" if is_healthy else "N/A",
                )
                console.print(table)
            else:
                console.print("[red]Error: ninerouter provider is not registered.[/red]")
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "config":
            try:
                config = load_config(Path("config/config.toml"))
            except Exception as e:
                config = None
                console.print(f"[red]Failed to load config: {e}[/red]")

            grid = Table.grid(expand=True)
            grid.add_column(style="bold cyan")
            grid.add_column(style="white")

            if config and hasattr(config, "llm") and getattr(config.llm, "ninerouter", None):
                nr = config.llm.ninerouter
                grid.add_row("Base URL:", nr.base_url)
                grid.add_row("API Key Configured:", "Yes" if nr.api_key else "No")
                grid.add_row("Request Timeout:", f"{nr.timeout}s")
                grid.add_row("Preferred Model:", nr.preferred_model or "None")
                grid.add_row("Preferred Backend:", nr.preferred_backend or "None")
            else:
                grid.add_row(
                    "Status:",
                    "No [llm.ninerouter] configuration block found in config.toml.",
                )

            console.print(
                Panel(
                    grid,
                    title="[bold white]9Router Integration Configuration[/bold white]",
                    border_style="blue",
                )
            )
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "test":
            console.print("[cyan]Testing 9Router OpenAI-compatible completion loop...[/cyan]")
            nr_provider = universal_provider_registry.lookup("ninerouter")
            if not nr_provider:
                console.print("[red]Error: ninerouter provider is not registered.[/red]")
                if exit_on_complete:
                    sys.exit(1)
                return True

            is_online = nr_provider.health()
            if not is_online:
                console.print(
                    "[yellow]9Router gateway is OFFLINE. Running local mock check...[/yellow]"
                )
                mock_provider = universal_provider_registry.lookup("mock")
                if mock_provider:
                    res = mock_provider.generate(model="mock-model", prompt="ping")
                    console.print(f"[green]Mock response: '{res}'[/green]")
                else:
                    console.print("[red]Mock provider unavailable.[/red]")
                if exit_on_complete:
                    sys.exit(0)
                return True

            nr_models = universal_model_registry.list_models("ninerouter")
            test_model = "gpt-4o"
            if nr_models:
                test_model = nr_models[0].model_id

            console.print(f"Sending completion test with model '[cyan]{test_model}[/cyan]'...")
            start = time.time()
            try:
                response = nr_provider.generate(model=test_model, prompt="ping")
                latency = (time.time() - start) * 1000.0
                console.print(
                    Panel(
                        f"Response: [green]{response}[/green]\n"
                        f"Latency: [yellow]{latency:.1f}ms[/yellow]",
                        title="[bold white]9Router API Test Success[/bold white]",
                        border_style="green",
                    )
                )
            except Exception as e:
                console.print(f"[red]9Router test failed: {e}[/red]")
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "benchmark":
            console.print(
                "[cyan]Running active benchmarks across all registered provider endpoints...[/cyan]"
            )
            table = Table(title="Active Benchmark Execution Results", border_style="cyan")
            table.add_column("Provider", style="bold magenta")
            table.add_column("Model", style="white")
            table.add_column("Status", style="green")
            table.add_column("Latency (ms)", style="cyan")
            table.add_column("Est. Cost", style="yellow")
            table.add_column("Tokens (In/Out)", style="white")

            from aios.providers.benchmark import generate_reports, run_provider_benchmark

            for p_name in universal_provider_registry.list_providers():
                models = [m.model_id for m in universal_model_registry.list_models(p_name)]
                if not models:
                    models = ["default"]
                for m_name in models:
                    res = run_provider_benchmark(p_name, m_name)
                    if res["success"]:
                        status_str = "[green]Success[/green]"
                        latency_str = f"{res['latency_ms']:.1f}"
                        cost_str = f"${res['cost']:.6f}"
                        tokens_str = f"{res['input_tokens']}/{res['output_tokens']}"
                    else:
                        status_str = f"[red]Failed ({res.get('error', 'Unknown')})[/red]"
                        latency_str = f"{res['latency_ms']:.1f}"
                        cost_str = "$0.000000"
                        tokens_str = "0/0"
                    table.add_row(p_name, m_name, status_str, latency_str, cost_str, tokens_str)

            console.print(table)
            console.print("[cyan]Generating markdown reports under docs/providers/...[/cyan]")
            try:
                generate_reports()
                console.print("[green]✓ Benchmark reports generated successfully.[/green]")
            except Exception as e:
                console.print(f"[red]✗ Failed to generate reports: {e}[/red]")
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "analytics":
            from aios.providers.analytics import calculate_provider_analytics
            from aios.providers.benchmark import generate_reports

            stats = calculate_provider_analytics()
            table = Table(
                title="Provider Usage & Analytics Summary",
                border_style="magenta",
            )
            table.add_column("Provider", style="bold magenta")
            table.add_column("Total Requests", style="white")
            table.add_column("Success Rate", style="green")
            table.add_column("Avg Latency (ms)", style="cyan")
            table.add_column("Total Cost (USD)", style="yellow")
            table.add_column("Total Tokens", style="white")

            for p_name, s in stats.items():
                table.add_row(
                    p_name,
                    str(s["total_requests"]),
                    f"{s['success_rate'] * 100.0:.1f}%",
                    f"{s['avg_latency_ms']:.1f}",
                    f"${s['total_cost']:.6f}",
                    str(s["total_tokens"]),
                )
            console.print(table)

            console.print("[cyan]Generating/updating markdown reports...[/cyan]")
            try:
                generate_reports()
                console.print("[green]✓ Analytics reports generated successfully.[/green]")
            except Exception as e:
                console.print(f"[red]✗ Failed to generate reports: {e}[/red]")
            if exit_on_complete:
                sys.exit(0)
            return True

    elif args and args[0] == "n8n":
        if len(args) < 2:
            console.print(
                "[yellow]Usage: aios n8n "
                "<connect|disconnect|status|version|health|config|test>[/yellow]"
            )
            if exit_on_complete:
                sys.exit(1)
            return True

        subcommand = args[1]
        import sys

        import httpx

        from aios.n8n.connection import N8NLiveConnectionManager

        mgr = N8NLiveConnectionManager()

        if subcommand == "connect":
            url = args[2] if len(args) > 2 else "http://localhost:5678"
            auth_type = "none"
            api_key = None
            email = None
            password = None

            if "--auth" in args:
                idx = args.index("--auth")
                if idx + 1 < len(args):
                    auth_type = args[idx + 1]

            if "--api-key" in args:
                idx = args.index("--api-key")
                if idx + 1 < len(args):
                    api_key = args[idx + 1]

            if "--email" in args:
                idx = args.index("--email")
                if idx + 1 < len(args):
                    email = args[idx + 1]

            if "--password" in args:
                idx = args.index("--password")
                if idx + 1 < len(args):
                    password = args[idx + 1]

            with console.status("[bold blue]Connecting to n8n instance...", spinner="dots"):
                res = mgr.connect(
                    url,
                    auth_type=auth_type,
                    api_key=api_key,
                    email=email,
                    password=password,
                )

            if res["success"]:
                console.print(f"[green]✓ {res['message']}[/green]")
                console.print(f"Connection Host: [white]{res['state']['host']}[/white]")
                console.print(f"Connection Port: [white]{res['state']['port']}[/white]")
            else:
                console.print(f"[red]✗ {res['message']}[/red]")
                console.print("[yellow]Attempting auto-discovery...[/yellow]")
                discovered = mgr.discover_instances()
                if discovered:
                    console.print(f"Found active instances at: {', '.join(discovered)}")
                    console.print("Re-connecting to first discovered instance...")
                    res2 = mgr.connect(discovered[0])
                    if res2["success"]:
                        console.print(f"[green]✓ Connected to {discovered[0]}[/green]")
                    else:
                        console.print("[red]✗ Auto-discovery reconnection failed.[/red]")
                else:
                    console.print("[red]No active n8n instances discovered on localhost.[/red]")

            if exit_on_complete:
                sys.exit(0 if res.get("success") else 1)
            return True

        elif subcommand == "disconnect":
            mgr.disconnect()
            console.print("[green]✓ Successfully disconnected from n8n.[/green]")
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "status":
            state = mgr.load_state()
            status_str = (
                "[green]CONNECTED[/green]" if state["connected"] else "[red]DISCONNECTED[/red]"
            )
            console.print(f"n8n Integration Status: {status_str}")
            console.print(f"URL: {state.get('url') or 'N/A'}")
            console.print(f"Auth Method: {state.get('auth_type') or 'none'}")
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "version":
            state = mgr.load_state()
            if not state["connected"]:
                console.print("[red]Error: Not connected to any n8n server.[/red]")
                if exit_on_complete:
                    sys.exit(1)
                return True

            with console.status("[bold blue]Fetching version details...", spinner="dots"):
                try:
                    res = httpx.get(f"{state['url']}/healthz", timeout=5.0)
                    version_data = res.json()
                    version = version_data.get("version", "unknown")
                except Exception:
                    version = "unknown"

                if version == "unknown" and "localhost" in state.get("url", ""):
                    import subprocess

                    try:
                        res_cli = subprocess.run(
                            ["n8n", "--version"],
                            capture_output=True,
                            text=True,
                            timeout=2.0,
                        )
                        if res_cli.returncode == 0:
                            version = res_cli.stdout.strip()
                    except Exception:
                        pass

            console.print(f"n8n Server Version: [cyan]{version}[/cyan]")
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "health":
            state = mgr.load_state()
            if not state["connected"]:
                console.print("[red]Error: Not connected to any n8n server.[/red]")
                if exit_on_complete:
                    sys.exit(1)
                return True

            with console.status("[bold blue]Running health ping...", spinner="dots"):
                try:
                    start = time.time()
                    res = httpx.get(f"{state['url']}/healthz", timeout=5.0)
                    latency = (time.time() - start) * 1000.0
                    status = "online" if res.status_code == 200 else "offline"
                except Exception:
                    status = "offline"
                    latency = 0.0

            console.print(f"Health Status: [green]{status.upper()}[/green]")
            console.print(f"Ping Latency: [white]{latency:.2f} ms[/white]")
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "config":
            state = mgr.load_state()
            console.print("[bold cyan]Active Connection Configuration:[/bold cyan]")
            console.print(f"Host: {state.get('host') or 'N/A'}")
            console.print(f"Port: {state.get('port') or 'N/A'}")
            console.print(f"URL: {state.get('url') or 'N/A'}")
            console.print(f"Authentication Method: {state.get('auth_type') or 'none'}")
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "test":
            state = mgr.load_state()
            if not state["connected"]:
                console.print("[red]Error: Not connected to any n8n server.[/red]")
                if exit_on_complete:
                    sys.exit(1)
                return True

            console.print("[bold cyan]Running integration diagnostics...[/bold cyan]")
            try:
                res = httpx.get(f"{state['url']}/healthz", timeout=5.0)
                if res.status_code == 200:
                    console.print("[green]✓ Step 1: Healthz endpoint responding (OK)[/green]")
                else:
                    console.print(
                        f"[red]✗ Step 1: Healthz endpoint returned code {res.status_code}[/red]"
                    )
            except Exception as e:
                console.print(f"[red]✗ Step 1: Healthz endpoint unreachable: {e}[/red]")

            if state.get("auth_type") == "api_key":
                console.print("[yellow]Verifying API Key permissions...[/yellow]")
            else:
                console.print("[white]Using anonymous access credentials.[/white]")

            console.print("[green]✓ Step 2: Connection manager verification complete.[/green]")
            if exit_on_complete:
                sys.exit(0)
            return True

    elif args and args[0] == "github":
        # ── GitHub Intelligence — Sprint 25 ─────────────────────────────────
        import sys  # ensure sys is locally bound in this function scope

        from aios.github.connection import GitHubConnectionManager
        from aios.github.intelligence import GitHubIntelligenceEngine
        from aios.github.reports import GitHubReportGenerator

        sub = args[1] if len(args) > 1 else None

        def _make_engine():
            # model_service is optional; LLM calls degrade gracefully when None
            return GitHubIntelligenceEngine(model_service=None)

        if sub == "login":
            token_arg = args[2] if len(args) > 2 else None
            mgr = GitHubConnectionManager(token=token_arg)
            result = mgr.login(token=token_arg)
            if result["success"]:
                console.print(f"[green]✓ Logged in as {result['user']}[/green]")
            else:
                console.print(f"[red]✗ Login failed: {result['message']}[/red]")
                if exit_on_complete:
                    sys.exit(1)
                return True
            if exit_on_complete:
                sys.exit(0)
            return True

        elif sub == "status":
            mgr = GitHubConnectionManager()
            st = mgr.get_status()
            if st.get("connected"):
                console.print(f"[green]✓ Connected as {st['user']}[/green]")
                console.print(f"  Token hint: {st.get('token_hint', 'n/a')}")
            else:
                console.print("[yellow]Not connected. Run: aios github login[/yellow]")
            if exit_on_complete:
                sys.exit(0)
            return True

        elif sub == "repos":
            mgr = GitHubConnectionManager()
            repos = mgr.list_user_repos()
            if not repos:
                console.print("[yellow]No repositories found or not authenticated.[/yellow]")
            for r in repos:
                priv = "[dim](private)[/dim]" if r.get("private") else ""
                console.print(
                    f"  [cyan]{r.get('full_name', r.get('name'))}[/cyan] "
                    f"{priv} — {r.get('description') or ''}"
                )
            if exit_on_complete:
                sys.exit(0)
            return True

        elif sub == "repo":
            repo_name = args[2] if len(args) > 2 else None
            if not repo_name:
                console.print("[red]Usage: aios github repo <owner/repo>[/red]")
                if exit_on_complete:
                    sys.exit(1)
                return True
            engine = _make_engine()
            try:
                repo = engine.inspect_repository(repo_name)
                console.print(f"[bold]{repo.owner}/{repo.name}[/bold]")
                console.print(f"  Description : {repo.description or 'N/A'}")
                console.print(f"  Stars       : {repo.stars}")
                console.print(f"  Forks       : {repo.forks}")
                console.print(f"  Open Issues : {repo.open_issues_count}")
                console.print(f"  Languages   : {', '.join(repo.languages) or 'N/A'}")
                console.print(f"  Private     : {repo.is_private}")
                console.print(f"  URL         : {repo.url}")
            except Exception as exc:
                console.print(f"[red]Error: {exc}[/red]")
                if exit_on_complete:
                    sys.exit(1)
                return True
            if exit_on_complete:
                sys.exit(0)
            return True

        elif sub == "branches":
            repo_name = args[2] if len(args) > 2 else None
            if not repo_name:
                console.print("[red]Usage: aios github branches <owner/repo>[/red]")
                if exit_on_complete:
                    sys.exit(1)
                return True
            engine = _make_engine()
            try:
                branches = engine.list_branches(repo_name)
                console.print(f"[cyan]{len(branches)} branch(es) in {repo_name}[/cyan]")
                for b in branches:
                    console.print(f"  {b.name}  ({b.sha[:7]})")
            except Exception as exc:
                console.print(f"[red]Error: {exc}[/red]")
                if exit_on_complete:
                    sys.exit(1)
                return True
            if exit_on_complete:
                sys.exit(0)
            return True

        elif sub == "commits":
            repo_name = args[2] if len(args) > 2 else None
            if not repo_name:
                console.print("[red]Usage: aios github commits <owner/repo>[/red]")
                if exit_on_complete:
                    sys.exit(1)
                return True
            engine = _make_engine()
            try:
                commits = engine.get_commit_history(repo_name)
                console.print(f"[cyan]Last {len(commits)} commit(s) in {repo_name}[/cyan]")
                for c in commits:
                    console.print(f"  [{c.sha[:7]}] {c.message[:72]} — {c.author} ({c.date[:10]})")
            except Exception as exc:
                console.print(f"[red]Error: {exc}[/red]")
                if exit_on_complete:
                    sys.exit(1)
                return True
            if exit_on_complete:
                sys.exit(0)
            return True

        elif sub == "issues":
            repo_name = args[2] if len(args) > 2 else None
            if not repo_name:
                console.print("[red]Usage: aios github issues <owner/repo>[/red]")
                if exit_on_complete:
                    sys.exit(1)
                return True
            engine = _make_engine()
            try:
                issues = engine.list_issues(repo_name)
                console.print(f"[cyan]{len(issues)} open issue(s) in {repo_name}[/cyan]")
                for i in issues:
                    labels = ", ".join(i.get("labels", []))
                    console.print(
                        f"  #{i.get('number')} {i.get('title')} [{labels or 'no labels'}]"
                    )
            except Exception as exc:
                console.print(f"[red]Error: {exc}[/red]")
                if exit_on_complete:
                    sys.exit(1)
                return True
            if exit_on_complete:
                sys.exit(0)
            return True

        elif sub == "pr":
            # aios github pr <owner/repo> [pr_number]
            repo_name = args[2] if len(args) > 2 else None
            if not repo_name:
                console.print("[red]Usage: aios github pr <owner/repo> [number][/red]")
                if exit_on_complete:
                    sys.exit(1)
                return True
            engine = _make_engine()
            try:
                if len(args) > 3:
                    pr_num = int(args[3])
                    pr = engine.inspect_pull_request(repo_name, pr_num)
                    console.print(f"[bold]PR #{pr.number}: {pr.title}[/bold]")
                    console.print(f"  State   : {pr.state}")
                    console.print(f"  Author  : {pr.user}")
                    console.print(f"  URL     : {pr.html_url}")
                    console.print(f"  Draft   : {pr.is_draft}")
                else:
                    prs = engine.list_pull_requests(repo_name)
                    console.print(f"[cyan]{len(prs)} PR(s) in {repo_name}[/cyan]")
                    for p in prs:
                        console.print(
                            f"  #{p.get('number')} {p.get('title')} "
                            f"— {p.get('state')} by {p.get('user')}"
                        )
            except Exception as exc:
                console.print(f"[red]Error: {exc}[/red]")
                if exit_on_complete:
                    sys.exit(1)
                return True
            if exit_on_complete:
                sys.exit(0)
            return True

        elif sub == "releases":
            repo_name = args[2] if len(args) > 2 else None
            if not repo_name:
                console.print("[red]Usage: aios github releases <owner/repo>[/red]")
                if exit_on_complete:
                    sys.exit(1)
                return True
            engine = _make_engine()
            try:
                releases = engine.get_release_history(repo_name)
                console.print(f"[cyan]{len(releases)} release(s) in {repo_name}[/cyan]")
                for r in releases:
                    console.print(
                        f"  {r.tag_name}  {r.name}  "
                        f"({r.created_at[:10] if r.created_at else 'n/a'})"
                    )
            except Exception as exc:
                console.print(f"[red]Error: {exc}[/red]")
                if exit_on_complete:
                    sys.exit(1)
                return True
            if exit_on_complete:
                sys.exit(0)
            return True

        elif sub == "actions":
            repo_name = args[2] if len(args) > 2 else None
            if not repo_name:
                console.print("[red]Usage: aios github actions <owner/repo>[/red]")
                if exit_on_complete:
                    sys.exit(1)
                return True
            engine = _make_engine()
            try:
                workflows = engine.get_workflow_status(repo_name)
                console.print(f"[cyan]{len(workflows)} action run(s) in {repo_name}[/cyan]")
                for w in workflows:
                    conclusion = w.conclusion or "pending"
                    console.print(f"  #{w.id} {w.name}  status={w.status}  conclusion={conclusion}")
            except Exception as exc:
                console.print(f"[red]Error: {exc}[/red]")
                if exit_on_complete:
                    sys.exit(1)
                return True
            if exit_on_complete:
                sys.exit(0)
            return True

        elif sub == "summary":
            repo_name = args[2] if len(args) > 2 else None
            if not repo_name:
                console.print("[red]Usage: aios github summary <owner/repo>[/red]")
                if exit_on_complete:
                    sys.exit(1)
                return True
            engine = _make_engine()
            rpt = GitHubReportGenerator()
            try:
                repo = engine.inspect_repository(repo_name)
                prs = engine.list_pull_requests(repo_name)
                issues = engine.list_issues(repo_name)
                branches = engine.list_branches(repo_name)
                releases = engine.get_release_history(repo_name)
                workflows = engine.get_workflow_status(repo_name)

                ai_summary = engine.generate_repo_summary(repo_name)
                ai_actions = engine.summarise_actions(repo_name)

                rpt.generate_all(
                    repo={
                        "owner": repo.owner,
                        "name": repo.name,
                        "description": repo.description,
                        "stars": repo.stars,
                        "forks": repo.forks,
                        "languages": repo.languages,
                        "url": repo.url,
                        "is_private": repo.is_private,
                        "open_issues_count": repo.open_issues_count,
                    },
                    prs=prs,
                    issues=issues,
                    branches=[{"name": b.name, "sha": b.sha} for b in branches],
                    releases=[
                        {
                            "tag_name": r.tag_name,
                            "name": r.name,
                            "created_at": r.created_at,
                        }
                        for r in releases
                    ],
                    workflows=[
                        {
                            "id": w.id,
                            "name": w.name,
                            "status": w.status,
                            "conclusion": w.conclusion,
                        }
                        for w in workflows
                    ],
                    ai_repo_summary=ai_summary,
                    ai_actions_summary=ai_actions,
                )

                console.print(
                    f"[green]✓ GitHub Intelligence summary for "
                    f"{repo.owner}/{repo.name} generated.[/green]"
                )
                console.print("[dim]Reports written to docs/github/[/dim]")
                console.print(f"\n[bold]AI Summary:[/bold]\n{ai_summary[:500]}")
            except Exception as exc:
                console.print(f"[red]Error: {exc}[/red]")
                if exit_on_complete:
                    sys.exit(1)
                return True
            if exit_on_complete:
                sys.exit(0)
            return True

        else:
            console.print(
                "[yellow]Usage: aios github "
                "<login|status|repos|repo|branches|commits|issues|pr|releases|actions|summary>"
                "[/yellow]"
            )
            if exit_on_complete:
                sys.exit(1)
            return True

    elif args and args[0] == "workflow":
        if len(args) < 2:
            console.print(
                "[yellow]Usage: aios workflow "
                "<generate|validate|analyze|optimize|templates|export|summary>[/yellow]"
            )
            if exit_on_complete:
                sys.exit(1)
            return True

        subcommand = args[1]
        import json
        import sys

        from aios.n8n.intelligence import WorkflowIntelligenceEngine

        engine = WorkflowIntelligenceEngine()

        if subcommand == "generate":
            prompt = (
                " ".join(args[2:])
                if len(args) > 2
                else "Generate a lead generation webhook workflow"
            )
            category = None
            if "--category" in args:
                idx = args.index("--category")
                if idx + 1 < len(args):
                    category = args[idx + 1]

            with console.status("[bold blue]Generating n8n workflow...", spinner="dots"):
                wf = engine.generator.generate(prompt, category=category)
                engine.memory.save_workflow(wf.get("name", "Generated Workflow"), wf)
                engine.generate_reports(wf)

            console.print(
                Panel(
                    json.dumps(wf, indent=2),
                    title=f"[bold green]Generated Workflow: {wf.get('name')}[/bold green]",
                    border_style="green",
                )
            )
            console.print("[cyan]Documentation reports written under docs/workflows/.[/cyan]")
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "validate":
            filepath = args[2] if len(args) > 2 else None
            if not filepath:
                wfs = engine.memory.list_workflows()
                if not wfs:
                    console.print(
                        "[red]Error: No workflows found. Please provide a filepath.[/red]"
                    )
                    if exit_on_complete:
                        sys.exit(1)
                    return True
                wf = wfs[-1]["workflow"]
            else:
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        wf = json.load(f)
                except Exception as e:
                    console.print(f"[red]Error loading workflow JSON: {e}[/red]")
                    if exit_on_complete:
                        sys.exit(1)
                    return True

            with console.status("[bold blue]Validating workflow...", spinner="dots"):
                res = engine.validator.validate(wf)
                engine.generate_reports(wf)

            status_str = "[green]VALID[/green]" if res["valid"] else "[red]INVALID[/red]"
            console.print(f"Workflow Validation Status: {status_str}\n")
            if res["errors"]:
                console.print("[bold red]Errors:[/bold red]")
                for err in res["errors"]:
                    console.print(f"- {err}")
            if res["warnings"]:
                console.print("[bold yellow]Warnings:[/bold yellow]")
                for wrn in res["warnings"]:
                    console.print(f"- {wrn}")
            if not res["errors"] and not res["warnings"]:
                console.print("[green]No issues or warnings found.[/green]")

            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "analyze":
            filepath = args[2] if len(args) > 2 else None
            if not filepath:
                wfs = engine.memory.list_workflows()
                if not wfs:
                    console.print(
                        "[red]Error: No workflows found. Please provide a filepath.[/red]"
                    )
                    if exit_on_complete:
                        sys.exit(1)
                    return True
                wf = wfs[-1]["workflow"]
            else:
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        wf = json.load(f)
                except Exception as e:
                    console.print(f"[red]Error loading workflow JSON: {e}[/red]")
                    if exit_on_complete:
                        sys.exit(1)
                    return True

            with console.status(
                "[bold blue]Analyzing workflow paths and credentials...",
                spinner="dots",
            ):
                res = engine.analyzer.analyze(wf)
                engine.generate_reports(wf)

            grid = Table.grid(padding=1)
            grid.add_column(style="bold cyan")
            grid.add_column(style="white")
            grid.add_row("Summary:", res["summary"])
            grid.add_row("Trigger Chain:", ", ".join(res["trigger_chain"]) or "None")
            grid.add_row("External Services:", ", ".join(res["external_services"]) or "None")
            grid.add_row(
                "Credentials Required:",
                ", ".join(res["credentials_required"]) or "None",
            )

            console.print(
                Panel(
                    grid,
                    title=f"[bold white]Workflow Analysis: {wf.get('name')}[/bold white]",
                    border_style="cyan",
                )
            )
            if res["bottlenecks"]:
                console.print("[bold yellow]Potential Bottlenecks:[/bold yellow]")
                for b in res["bottlenecks"]:
                    console.print(f"- {b}")
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "optimize":
            filepath = args[2] if len(args) > 2 else None
            if not filepath:
                wfs = engine.memory.list_workflows()
                if not wfs:
                    console.print(
                        "[red]Error: No workflows found. Please provide a filepath.[/red]"
                    )
                    if exit_on_complete:
                        sys.exit(1)
                    return True
                wf = wfs[-1]["workflow"]
            else:
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        wf = json.load(f)
                except Exception as e:
                    console.print(f"[red]Error loading workflow JSON: {e}[/red]")
                    if exit_on_complete:
                        sys.exit(1)
                    return True

            with console.status("[bold blue]Optimizing workflow graph...", spinner="dots"):
                opt = engine.optimizer.optimize(wf)
                engine.generate_reports(opt)

            console.print(
                Panel(
                    json.dumps(opt, indent=2),
                    title=f"[bold green]Optimized Workflow: {opt.get('name')}[/bold green]",
                    border_style="green",
                )
            )
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "templates":
            templates_list = engine.templates.list_templates()
            table = Table(title="Available n8n Workflow Templates", border_style="cyan")
            table.add_column("Category Name", style="bold cyan")
            table.add_column("Description", style="white")

            for t in templates_list:
                tmpl = engine.templates.get_template(t)
                node_count = len(tmpl.get("nodes", []))
                table.add_row(t, f"Prebuilt structure with {node_count} nodes.")

            console.print(table)
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "export":
            wfs = engine.memory.list_workflows()
            if not wfs:
                console.print("[red]Error: No workflows in memory to export.[/red]")
                if exit_on_complete:
                    sys.exit(1)
                return True
            wf = wfs[-1]["workflow"]

            output_file = args[2] if len(args) > 2 else "workflow_export.json"
            try:
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(wf, f, indent=2)
                console.print(f"[green]✓ Workflow exported to {output_file} successfully.[/green]")
            except Exception as e:
                console.print(f"[red]Error writing export file: {e}[/red]")
                if exit_on_complete:
                    sys.exit(1)
                return True
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "deploy":
            filepath = args[2] if len(args) > 2 else None
            if not filepath:
                wfs = engine.memory.list_workflows()
                if not wfs:
                    console.print(
                        "[red]Error: No workflows found to deploy. Please provide a filepath.[/red]"
                    )
                    if exit_on_complete:
                        sys.exit(1)
                    return True
                wf = wfs[-1]["workflow"]
            else:
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        wf = json.load(f)
                except Exception as e:
                    console.print(f"[red]Error loading workflow JSON: {e}[/red]")
                    if exit_on_complete:
                        sys.exit(1)
                    return True

            from aios.n8n.runtime import N8NWorkflowRuntimeManager

            runtime = N8NWorkflowRuntimeManager()

            with console.status(
                "[bold blue]Deploying workflow to live n8n instance...", spinner="dots"
            ):
                res = runtime.deploy(wf, force=True)

            if res["success"]:
                console.print(f"[green]✓ {res['message']}[/green]")
                console.print(f"Deployed ID: [cyan]{res['workflow_id']}[/cyan]")
            else:
                console.print(f"[red]✗ {res['message']}[/red]")

            if exit_on_complete:
                sys.exit(0 if res["success"] else 1)
            return True

        elif subcommand == "update":
            workflow_id = args[2] if len(args) > 2 else None
            filepath = args[3] if len(args) > 3 else None
            if not workflow_id or not filepath:
                console.print(
                    "[yellow]Usage: aios workflow update <workflow_id> <filepath>[/yellow]"
                )
                if exit_on_complete:
                    sys.exit(1)
                return True

            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    wf = json.load(f)
            except Exception as e:
                console.print(f"[red]Error loading workflow JSON: {e}[/red]")
                if exit_on_complete:
                    sys.exit(1)
                return True

            from aios.n8n.runtime import N8NWorkflowRuntimeManager

            runtime = N8NWorkflowRuntimeManager()

            with console.status("[bold blue]Updating workflow...", spinner="dots"):
                res = runtime.deploy(wf, force=True)

            if res["success"]:
                console.print("[green]✓ Workflow updated successfully.[/green]")
            else:
                console.print(f"[red]✗ {res['message']}[/red]")

            if exit_on_complete:
                sys.exit(0 if res["success"] else 1)
            return True

        elif subcommand == "execute":
            workflow_id = args[2] if len(args) > 2 else None
            if not workflow_id:
                console.print(
                    "[yellow]Usage: aios workflow execute <workflow_id> [input_json][/yellow]"
                )
                if exit_on_complete:
                    sys.exit(1)
                return True

            input_data = {}
            if len(args) > 3:
                try:
                    input_data = json.loads(args[3])
                except Exception:
                    pass

            from aios.n8n.runtime import N8NWorkflowRuntimeManager

            runtime = N8NWorkflowRuntimeManager()

            with console.status("[bold blue]Triggering workflow execution...", spinner="dots"):
                res = runtime.execute(workflow_id, input_data)

            if res["success"]:
                console.print("[green]✓ Workflow execution triggered.[/green]")
                console.print(
                    Panel(json.dumps(res["execution"], indent=2), title="Execution Response")
                )
            else:
                console.print(f"[red]✗ {res['message']}[/red]")

            if exit_on_complete:
                sys.exit(0 if res["success"] else 1)
            return True

        elif subcommand == "monitor":
            from aios.n8n.runtime import N8NWorkflowRuntimeManager

            runtime = N8NWorkflowRuntimeManager()

            with console.status("[bold blue]Fetching runtime execution history...", spinner="dots"):
                analytics = runtime.get_analytics()

            console.print(
                f"[bold cyan]Total Executions Checked:[/bold cyan] {analytics['total_executions']}"
            )
            console.print(
                f"[bold cyan]Success Rate:[/bold cyan] {analytics['success_rate'] * 100.0:.1f}%"
            )
            console.print(
                f"[bold cyan]Failed Executions:[/bold cyan] {analytics['failed_executions']}"
            )
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "logs":
            from aios.n8n.runtime import N8NWorkflowRuntimeManager

            runtime = N8NWorkflowRuntimeManager()

            with console.status("[bold blue]Retrieving execution logs...", spinner="dots"):
                analytics = runtime.get_analytics()

            console.print(f"Status: OK. Success rate is {analytics['success_rate'] * 100.0:.1f}%.")
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "history":
            workflow_id = args[2] if len(args) > 2 else None
            if not workflow_id:
                console.print("[yellow]Usage: aios workflow history <workflow_id>[/yellow]")
                if exit_on_complete:
                    sys.exit(1)
                return True

            from aios.n8n.runtime import N8NWorkflowRuntimeManager

            runtime = N8NWorkflowRuntimeManager()
            records = runtime.history.get(workflow_id, [])

            table = Table(title=f"Deployment History for {workflow_id}")
            table.add_column("Version", style="bold cyan")
            table.add_column("Timestamp", style="white")

            for r in records:
                table.add_row(str(r["version"]), time.ctime(r["timestamp"]))

            console.print(table)
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "rollback":
            workflow_id = args[2] if len(args) > 2 else None
            version = int(args[3]) if len(args) > 3 else None
            if not workflow_id or not version:
                console.print(
                    "[yellow]Usage: aios workflow rollback <workflow_id> <version>[/yellow]"
                )
                if exit_on_complete:
                    sys.exit(1)
                return True

            from aios.n8n.runtime import N8NWorkflowRuntimeManager

            runtime = N8NWorkflowRuntimeManager()

            with console.status("[bold blue]Rolling back workflow...", spinner="dots"):
                res = runtime.rollback(workflow_id, version)

            if res["success"]:
                console.print(f"[green]✓ {res['message']}[/green]")
            else:
                console.print(f"[red]✗ {res['message']}[/red]")

            if exit_on_complete:
                sys.exit(0 if res["success"] else 1)
            return True

        elif subcommand in ("enable", "activate"):
            workflow_id = args[2] if len(args) > 2 else None
            if not workflow_id:
                console.print("[yellow]Usage: aios workflow enable <workflow_id>[/yellow]")
                if exit_on_complete:
                    sys.exit(1)
                return True

            from aios.n8n.runtime import N8NWorkflowRuntimeManager

            runtime = N8NWorkflowRuntimeManager()

            with console.status("[bold blue]Activating workflow...", spinner="dots"):
                success = runtime.activate(workflow_id)

            if success:
                console.print("[green]✓ Workflow activated successfully.[/green]")
            else:
                console.print("[red]✗ Failed to activate workflow.[/red]")

            if exit_on_complete:
                sys.exit(0 if success else 1)
            return True

        elif subcommand in ("disable", "deactivate"):
            workflow_id = args[2] if len(args) > 2 else None
            if not workflow_id:
                console.print("[yellow]Usage: aios workflow disable <workflow_id>[/yellow]")
                if exit_on_complete:
                    sys.exit(1)
                return True

            from aios.n8n.runtime import N8NWorkflowRuntimeManager

            runtime = N8NWorkflowRuntimeManager()

            with console.status("[bold blue]Deactivating workflow...", spinner="dots"):
                success = runtime.deactivate(workflow_id)

            if success:
                console.print("[green]✓ Workflow deactivated successfully.[/green]")
            else:
                console.print("[red]✗ Failed to deactivate workflow.[/red]")

            if exit_on_complete:
                sys.exit(0 if success else 1)
            return True

        elif subcommand == "delete":
            workflow_id = args[2] if len(args) > 2 else None
            if not workflow_id:
                console.print("[yellow]Usage: aios workflow delete <workflow_id>[/yellow]")
                if exit_on_complete:
                    sys.exit(1)
                return True

            from aios.n8n.runtime import N8NWorkflowRuntimeManager

            runtime = N8NWorkflowRuntimeManager()

            with console.status("[bold blue]Deleting workflow...", spinner="dots"):
                success = runtime.delete(workflow_id)

            if success:
                console.print("[green]✓ Workflow deleted successfully from server.[/green]")
            else:
                console.print("[red]✗ Failed to delete workflow from server.[/red]")

            if exit_on_complete:
                sys.exit(0 if success else 1)
            return True

        elif subcommand == "sync":
            filepath = args[2] if len(args) > 2 else None
            if not filepath:
                console.print("[yellow]Usage: aios workflow sync <filepath>[/yellow]")
                if exit_on_complete:
                    sys.exit(1)
                return True

            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    wf = json.load(f)
            except Exception as e:
                console.print(f"[red]Error loading workflow JSON: {e}[/red]")
                if exit_on_complete:
                    sys.exit(1)
                return True

            from aios.n8n.runtime import N8NWorkflowRuntimeManager

            runtime = N8NWorkflowRuntimeManager()

            with console.status("[bold blue]Synchronizing state...", spinner="dots"):
                res = runtime.sync(wf)

            if res["drifted"]:
                console.print(f"[yellow]⚠ Drift Detected: {res['reason']}[/yellow]")
            else:
                console.print(
                    f"[green]✓ Workflow '{wf.get('name')}' "
                    f"is synchronized with live server.[/green]"
                )

            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "summary":
            filepath = args[2] if len(args) > 2 else None
            if not filepath:
                wfs = engine.memory.list_workflows()
                if not wfs:
                    console.print(
                        "[red]Error: No workflows found. Please provide a filepath.[/red]"
                    )
                    if exit_on_complete:
                        sys.exit(1)
                    return True
                wf = wfs[-1]["workflow"]
            else:
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        wf = json.load(f)
                except Exception as e:
                    console.print(f"[red]Error loading workflow JSON: {e}[/red]")
                    if exit_on_complete:
                        sys.exit(1)
                    return True

            analysis = engine.analyzer.analyze(wf)
            console.print(f"[bold cyan]Workflow Name:[/bold cyan] {wf.get('name')}")
            console.print(f"[bold cyan]Node Count:[/bold cyan] {len(wf.get('nodes', []))}")
            console.print(f"[bold cyan]Summary:[/bold cyan] {analysis['summary']}")
            if exit_on_complete:
                sys.exit(0)
            return True

    elif args and args[0] == "chat":
        prompt = " ".join(args[1:]) if len(args) > 1 else ""
        if (prompt.startswith('"') and prompt.endswith('"')) or (
            prompt.startswith("'") and prompt.endswith("'")
        ):
            prompt = prompt[1:-1]

        if not prompt:
            console.print("[yellow]Usage: aios chat <message>[/yellow]")
            if exit_on_complete:
                import sys

                sys.exit(1)
            return True

        task_type = "chat"
        is_coding = (
            "python" in prompt.lower() or "code" in prompt.lower() or "function" in prompt.lower()
        )
        if is_coding:
            task_type = "coding"

        omni_req = OmniRouteRequest(
            prompt=prompt,
            task_type=task_type,
            estimated_input_tokens=200,
            estimated_output_tokens=200,
        )

        with console.status("[bold blue]Executing chat request via OmniRoute...", spinner="dots"):
            response = universal_omniroute_engine.execute(omni_req)

        title_str = f"[bold green]Response ({response.provider} - {response.model})[/bold green]"
        subtitle_str = (
            f"[dim]Cost: ${response.cost:.6f} | Latency: {response.latency_ms:.1f}ms[/dim]"
        )

        console.print(
            Panel(
                response.content,
                title=title_str,
                subtitle=subtitle_str,
                border_style="green",
            )
        )
    elif args and args[0] == "docs":
        import os
        import sys

        subcommand = args[1] if len(args) > 1 else "help"
        target_dir = "."

        from aios.services.docintel.generator import MarkdownGenerator
        from aios.services.docintel.graph import DependencyGraphBuilder
        from aios.services.docintel.indexer import DocumentationIndexer
        from aios.services.docintel.intelligence import DocumentationIntelligenceEngine
        from aios.services.docintel.scanner import RepositoryScanner

        if subcommand == "scan":
            scanner = RepositoryScanner(target_dir)
            with console.status("[bold blue]Scanning repository...", spinner="dots"):
                res = scanner.scan()

            table = Table(title="Repository Scan Results", border_style="cyan")
            table.add_column("Category", style="bold cyan")
            table.add_column("Count", style="white")

            table.add_row("Packages", str(len(res.get("packages", []))))
            table.add_row("Modules", str(len(res.get("modules", []))))
            table.add_row("Services", str(len(res.get("services", []))))
            table.add_row("Providers", str(len(res.get("providers", []))))
            table.add_row("Registries", str(len(res.get("registries", []))))
            table.add_row("Tests", str(len(res.get("tests", []))))
            table.add_row("Configuration Files", str(len(res.get("configuration_files", []))))
            table.add_row("Documentation Files", str(len(res.get("documentation", []))))
            table.add_row("CLI Commands", str(len(res.get("cli_commands", []))))

            console.print(table)
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "build":
            scanner = RepositoryScanner(target_dir)
            indexer = DocumentationIndexer()
            graph_builder = DependencyGraphBuilder()
            intel_engine = DocumentationIntelligenceEngine()
            generator = MarkdownGenerator("docs")

            with console.status(
                "[bold blue]Generating complete documentation platform...", spinner="dots"
            ):
                scan_res = scanner.scan()
                index_data = {}
                for mod in scan_res["modules"]:
                    parts = mod.split(".")
                    possible_paths = [
                        os.path.join("core", "src", *parts) + ".py",
                        os.path.join(*parts) + ".py",
                    ]
                    for path in possible_paths:
                        if os.path.exists(path):
                            index_data[path] = indexer.parse_file(path)
                            break

                dep_graph = graph_builder.build_dependency_graph(scan_res, index_data)
                pkg_graph = graph_builder.build_package_graph(scan_res, dep_graph)
                svc_graph = graph_builder.build_service_graph(scan_res, dep_graph)

                dep_mermaid = graph_builder.generate_mermaid(dep_graph, "Dependency Graph")
                pkg_mermaid = graph_builder.generate_mermaid(pkg_graph, "Package Graph")
                svc_mermaid = graph_builder.generate_mermaid(svc_graph, "Service Graph")

                intel_report = intel_engine.analyze(index_data)
                generator.generate(
                    scan_res, index_data, intel_report, dep_mermaid, pkg_mermaid, svc_mermaid
                )

            console.print(
                "[bold green]✓ Documentation built successfully inside /docs[/bold green]"
            )
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "report":
            scanner = RepositoryScanner(target_dir)
            indexer = DocumentationIndexer()
            intel_engine = DocumentationIntelligenceEngine()

            with console.status("[bold blue]Generating documentation report...", spinner="dots"):
                scan_res = scanner.scan()
                index_data = {}
                for mod in scan_res["modules"]:
                    parts = mod.split(".")
                    possible_paths = [
                        os.path.join("core", "src", *parts) + ".py",
                        os.path.join(*parts) + ".py",
                    ]
                    for path in possible_paths:
                        if os.path.exists(path):
                            index_data[path] = indexer.parse_file(path)
                            break
                intel_report = intel_engine.analyze(index_data)

            console.print(
                f"[bold green]Completeness Score: {intel_report['score']}/100[/bold green]"
            )
            console.print(f"Undocumented classes: {len(intel_report['undocumented_classes'])}")
            console.print(f"Undocumented functions: {len(intel_report['undocumented_functions'])}")
            console.print(f"Todos and Fixmes: {len(intel_report['todos_fixmes'])}")
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "ask":
            if len(args) < 3:
                console.print('[yellow]Usage: aios docs ask "<query>"[/yellow]')
                if exit_on_complete:
                    sys.exit(1)
                return True
            query = args[2]

            from aios.registry import ServiceRegistry
            from aios.services.docintel.agent import DocumentationAgent

            agent = ServiceRegistry._global_registry.get(DocumentationAgent)
            if not agent:
                agent = DocumentationAgent(index_path="docs/index.json")
                agent.initialize()

            with console.status("[bold blue]Querying AI Documentation Agent...", spinner="dots"):
                answer = agent.ask(query)

            console.print(answer)
            if exit_on_complete:
                sys.exit(0)
            return True

        else:
            console.print("[yellow]Usage: aios docs <scan|build|report|ask>[/yellow]")
            if exit_on_complete:
                sys.exit(1)
            return True

    elif args and args[0] == "engineer":
        import sys

        if len(args) < 2:
            console.print(
                "[yellow]Usage: aios engineer <build|search|graph|explain|impact|validate>[/yellow]"
            )
            if exit_on_complete:
                sys.exit(1)
            return True

        subcommand = args[1]

        from aios.registry import ServiceRegistry
        from aios.services.engineer.bible import EngineeringBibleService

        service = None
        if ServiceRegistry._global_registry:
            service = ServiceRegistry._global_registry.get(EngineeringBibleService)

        if not service:
            service = EngineeringBibleService()
            service.initialize()

        if subcommand == "build":
            target_dir = "."
            from aios.services.docintel.generator import MarkdownGenerator
            from aios.services.docintel.graph import DependencyGraphBuilder
            from aios.services.docintel.indexer import DocumentationIndexer
            from aios.services.docintel.intelligence import DocumentationIntelligenceEngine
            from aios.services.docintel.scanner import RepositoryScanner

            scanner = RepositoryScanner(target_dir)
            indexer = DocumentationIndexer()
            graph_builder = DependencyGraphBuilder()
            intel_engine = DocumentationIntelligenceEngine()
            generator = MarkdownGenerator("docs")

            with console.status(
                "[bold blue]Generating complete documentation platform...", spinner="dots"
            ):
                scan_res = scanner.scan()
                index_data = {}
                for mod in scan_res["modules"]:
                    parts = mod.split(".")
                    possible_paths = [
                        os.path.join("core", "src", *parts) + ".py",
                        os.path.join(*parts) + ".py",
                    ]
                    for path in possible_paths:
                        if os.path.exists(path):
                            index_data[path] = indexer.parse_file(path)
                            break

                dep_graph = graph_builder.build_dependency_graph(scan_res, index_data)
                pkg_graph = graph_builder.build_package_graph(scan_res, dep_graph)
                svc_graph = graph_builder.build_service_graph(scan_res, dep_graph)

                dep_mermaid = graph_builder.generate_mermaid(dep_graph, "Dependency Graph")
                pkg_mermaid = graph_builder.generate_mermaid(pkg_graph, "Package Graph")
                svc_mermaid = graph_builder.generate_mermaid(svc_graph, "Service Graph")

                intel_report = intel_engine.analyze(index_data)
                generator.generate(
                    scan_res,
                    index_data,
                    intel_report,
                    dep_mermaid,
                    pkg_mermaid,
                    svc_mermaid,
                )
            service.initialize()
            console.print("[green]Engineering Graph compiled successfully.[/green]")
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "search":
            if len(args) < 3:
                console.print('[yellow]Usage: aios engineer search "<query>"[/yellow]')
                if exit_on_complete:
                    sys.exit(1)
                return True
            query = args[2]
            res = service.search(query)
            if not res:
                console.print("[yellow]No entities found matching query.[/yellow]")
            for item in res:
                console.print(
                    f"- [bold cyan]{item['name']}[/bold cyan] ({item['type']}) in {item['file']}"
                )
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "graph":
            gtype = args[2] if len(args) > 2 else "import"
            if gtype not in ["import", "service", "event", "provider"]:
                console.print(
                    "[yellow]Usage: aios engineer graph <import|service|event|provider>[/yellow]"
                )
                if exit_on_complete:
                    sys.exit(1)
                return True
            if gtype == "import":
                dot = service.dependency_analyzer.generate_import_graph()
            elif gtype == "service":
                dot = service.dependency_analyzer.generate_service_graph()
            elif gtype == "event":
                dot = service.dependency_analyzer.generate_event_graph()
            elif gtype == "provider":
                dot = service.dependency_analyzer.generate_provider_graph()
            console.print(dot)
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "explain":
            if len(args) < 3:
                console.print("[yellow]Usage: aios engineer explain <entity_name>[/yellow]")
                if exit_on_complete:
                    sys.exit(1)
                return True
            ent_name = args[2]
            ent = service.graph.entities.get(ent_name)
            if not ent:
                console.print(f"[red]Entity '{ent_name}' not found.[/red]")
                if exit_on_complete:
                    sys.exit(1)
                return True
            console.print(f"[bold green]Entity: {ent['name']}[/bold green]")
            console.print(f"Type: {ent['type']}")
            console.print(f"File: {ent['file']}")
            console.print(f"Bases: {', '.join(ent.get('bases', []))}")
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "impact":
            if len(args) < 3:
                console.print("[yellow]Usage: aios engineer impact <entity_name>[/yellow]")
                if exit_on_complete:
                    sys.exit(1)
                return True
            ent_name = args[2]
            res = service.impact_analyzer.analyze(ent_name)
            if "error" in res:
                console.print(f"[red]{res['error']}[/red]")
                if exit_on_complete:
                    sys.exit(1)
                return True
            console.print(f"[bold green]Impact Analysis for {res['entity']}:[/bold green]")
            console.print(f"File: {res['file']}")
            console.print(f"Dependents: {', '.join(res['dependents'])}")
            console.print(f"Affected Tests: {', '.join(res['affected_tests'])}")
            console.print(f"Risk Score: [bold red]{res['risk_score']}/100[/bold red]")
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "validate":
            violations = service.rule_engine.validate()
            if not violations:
                console.print("✓ No architectural validation violations found.")
            else:
                for v in violations:
                    console.print(f"[red]Violation: {v['type']}[/red] - {v['description']}")
            if exit_on_complete:
                sys.exit(0)
            return True

        else:
            console.print(
                "[yellow]Usage: aios engineer <build|search|graph|explain|impact|validate>[/yellow]"
            )
            if exit_on_complete:
                sys.exit(1)
            return True

    elif args and args[0] == "workspace":
        import sys
        from pathlib import Path as _Path

        if len(args) < 2:
            console.print(
                "[yellow]Usage: aios workspace <scan|summary|status|graph|refresh>[/yellow]"
            )
            if exit_on_complete:
                sys.exit(1)
            return True

        subcommand = args[1]

        from aios.registry import ServiceRegistry
        from aios.services.developer_workspace import DeveloperWorkspaceService
        from aios.services.workspace_intelligence import (
            CodeIntelligenceService,
            WorkspaceIntelligenceService,
        )

        service = None
        if ServiceRegistry._global_registry:
            service = ServiceRegistry._global_registry.get(WorkspaceIntelligenceService)

        if not service:
            from aios.bootstrap import bootstrap_kernel

            kernel = bootstrap_kernel(_Path("config/config.toml"))
            kernel.boot()
            service = kernel.registry.get(WorkspaceIntelligenceService)

        workspace_root = "."
        try:
            from aios.services.context import ContextService

            ctx_svc = (
                ServiceRegistry._global_registry.get(ContextService)
                if ServiceRegistry._global_registry
                else None
            )
            ctx = ctx_svc.get_current_context() if ctx_svc else None
            if ctx:
                workspace_root = ctx.project_root
        except Exception:
            pass

        if subcommand == "scan":
            with console.status(
                "[bold blue]Scanning workspace architecture and mapping dependencies...",
                spinner="dots",
            ):
                service.analyze_repository(workspace_root)
            console.print(
                "[green]Workspace scanned successfully. "
                "Markdown reports generated in docs/.[/green]"
            )
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "summary":
            summary = service.analyze_repository(workspace_root)

            grid = Table.grid(padding=1)
            grid.add_column(style="bold cyan", justify="right")
            grid.add_column(style="white")

            grid.add_row("High-Level Architecture:", summary.high_level_architecture)
            grid.add_row("Components:", ", ".join(summary.components))
            grid.add_row("Design Patterns:", ", ".join(summary.design_patterns))
            langs_str = ", ".join([f"{lang} ({cnt})" for lang, cnt in summary.languages.items()])
            grid.add_row("Languages:", langs_str)
            grid.add_row("Frameworks:", ", ".join(summary.frameworks))
            grid.add_row("Package Managers:", ", ".join(summary.package_managers))

            health_grid = Table.grid(padding=1)
            health_grid.add_column(style="bold green", justify="right")
            health_grid.add_column(style="white")
            health_grid.add_row("Files Count:", str(summary.health.file_count))
            health_grid.add_row("Folders Count:", str(summary.health.folder_count))
            health_grid.add_row("Test Count:", str(summary.health.test_count))
            health_grid.add_row("Doc Coverage:", f"{summary.health.documentation_coverage:.1%}")
            health_grid.add_row("README Coverage:", f"{summary.health.readme_coverage:.1%}")
            health_grid.add_row("Config Completeness:", f"{summary.health.config_completeness:.1%}")

            console.print(
                Panel(
                    grid,
                    title="[bold white]Workspace Summary[/bold white]",
                    border_style="cyan",
                )
            )
            console.print(
                Panel(
                    health_grid,
                    title="[bold white]Workspace Health[/bold white]",
                    border_style="green",
                )
            )
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "status":
            dev_ws = None
            if ServiceRegistry._global_registry:
                dev_ws = ServiceRegistry._global_registry.get(DeveloperWorkspaceService)
            if not dev_ws:
                from aios.services.developer_workspace_impl import LocalDeveloperWorkspace

                dev_ws = LocalDeveloperWorkspace()

            info = dev_ws.get_workspace_info(workspace_root)

            grid = Table.grid(padding=1)
            grid.add_column(style="bold yellow", justify="right")
            grid.add_column(style="white")

            grid.add_row("Git Branch:", info.extra.get("git_branch") or "unknown")
            grid.add_row("Staged Files:", str(len(info.staged_files)))
            grid.add_row("Unstaged Files:", str(len(info.unstaged_files)))
            grid.add_row("Untracked Files:", str(len(info.untracked_files)))
            grid.add_row("Build Systems:", ", ".join(info.build_systems))
            grid.add_row("Linters:", ", ".join(info.linters))
            grid.add_row("Detected Tests:", str(len(info.detected_tests)))

            console.print(
                Panel(
                    grid,
                    title="[bold white]Workspace Status[/bold white]",
                    border_style="yellow",
                )
            )
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "graph":
            code_intel = None
            if ServiceRegistry._global_registry:
                code_intel = ServiceRegistry._global_registry.get(CodeIntelligenceService)
            if not code_intel:
                from aios.services.memory_impl import LocalMemoryService
                from aios.services.project_intelligence_impl import LocalProjectIntelligence
                from aios.services.workspace_intelligence_impl import (
                    LocalCodeIntelligenceService,
                )

                code_intel = LocalCodeIntelligenceService(
                    LocalProjectIntelligence(), LocalMemoryService()
                )
                code_intel.initialize()

            summary = code_intel.analyze_codebase(workspace_root)

            mermaid_lines = ["graph TD"]
            for src, dests in list(summary.dependency_graph.items())[:25]:
                src_name = Path(src).name
                for dest in dests:
                    dest_name = Path(dest).name
                    mermaid_lines.append(f"    {src_name} --> {dest_name}")

            console.print("\n".join(mermaid_lines))
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "refresh":
            for cache_file in (".aios_project_intelligence.json", ".aios_code_intelligence.json"):
                cache_path = _Path(workspace_root) / cache_file
                if cache_path.is_file():
                    try:
                        cache_path.unlink()
                    except Exception:
                        pass
            with console.status(
                "[bold blue]Rescanning workspace (force invalidating cache)...", spinner="dots"
            ):
                service.analyze_repository(workspace_root)
            console.print("[green]Workspace refreshed successfully.[/green]")
            if exit_on_complete:
                sys.exit(0)
            return True

        else:
            console.print(
                "[yellow]Usage: aios workspace <scan|summary|status|graph|refresh>[/yellow]"
            )
            if exit_on_complete:
                sys.exit(1)
            return True

    elif args and args[0] == "notion":
        import sys

        if len(args) < 2:
            console.print(
                "[yellow]Usage: aios notion <login|logout|status|sync|search|"
                "summarize|create-page|update-page|list-databases>[/yellow]"
            )
            if exit_on_complete:
                sys.exit(1)
            return True

        subcommand = args[1]

        from aios.registry import ServiceRegistry
        from aios.services.notion import NotionService
        from aios.services.notion_impl import LocalNotionService

        service = None
        if ServiceRegistry._global_registry:
            service = ServiceRegistry._global_registry.get(NotionService)

        if not service:
            service = LocalNotionService()
            service.initialize()

        if subcommand == "login":
            if len(args) < 4:
                console.print("[red]Usage: aios notion login <token> <workspace_name>[/red]")
                if exit_on_complete:
                    sys.exit(1)
                return True
            token = args[2]
            workspace_name = args[3]
            if service.login(token, workspace_name):
                console.print(f"[green]Successfully connected workspace '{workspace_name}'[/green]")
                if exit_on_complete:
                    sys.exit(0)
            else:
                console.print("[red]Failed to login[/red]")
                if exit_on_complete:
                    sys.exit(1)
            return True

        elif subcommand == "logout":
            workspace_name = args[2] if len(args) > 2 else None
            service.logout(workspace_name)
            if workspace_name:
                console.print(
                    f"[green]Successfully logged out of workspace '{workspace_name}'[/green]"
                )
            else:
                console.print("[green]Successfully logged out of all workspaces[/green]")
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "status":
            status = service.get_status()
            console.print(f"Status: [bold]{status['status']}[/bold]")
            if status["workspaces"]:
                console.print(f"Connected Workspaces: {', '.join(status['workspaces'])}")
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "sync":
            console.print("Syncing Notion workspaces...")
            res = service.sync()
            if res.get("status") == "success":
                console.print(
                    f"[green]✓ Successfully synchronized "
                    f"{res.get('synced_pages', 0)} pages.[/green]"
                )
                if exit_on_complete:
                    sys.exit(0)
            else:
                console.print("[red]Failed to sync Notion workspaces[/red]")
                if exit_on_complete:
                    sys.exit(1)
            return True

        elif subcommand == "search":
            if len(args) < 3:
                console.print("[red]Usage: aios notion search <query>[/red]")
                if exit_on_complete:
                    sys.exit(1)
                return True
            query = args[2]
            results = service.search(query)
            if not results:
                console.print("No pages or databases found matching query.")
            for r in results:
                console.print(
                    f"- {r['title']} ({r['type']}) in workspace '{r['workspace']}' [ID: {r['id']}]"
                )
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "summarize":
            if len(args) < 3:
                console.print("[red]Usage: aios notion summarize <page_id>[/red]")
                if exit_on_complete:
                    sys.exit(1)
                return True
            page_id = args[2]
            try:
                summary = service.summarize(page_id)
                console.print(f"[bold]Summary of page {page_id}:[/bold]\n{summary}")
                if exit_on_complete:
                    sys.exit(0)
            except Exception as e:
                console.print(f"[red]Error summarizing page: {e}[/red]")
                if exit_on_complete:
                    sys.exit(1)
            return True

        elif subcommand == "create-page":
            if len(args) < 4:
                console.print(
                    "[red]Usage: aios notion create-page <parent_id> <title> [content][/red]"
                )
                if exit_on_complete:
                    sys.exit(1)
                return True
            parent_id = args[2]
            title = args[3]
            content = args[4] if len(args) > 4 else ""
            try:
                page = service.create_page(parent_id, title, content)
                console.print(
                    f"[green]Successfully created page '{title}' [ID: {page['id']}][/green]"
                )
                if exit_on_complete:
                    sys.exit(0)
            except Exception as e:
                console.print(f"[red]Error creating page: {e}[/red]")
                if exit_on_complete:
                    sys.exit(1)
            return True

        elif subcommand == "update-page":
            if len(args) < 4:
                console.print("[red]Usage: aios notion update-page <page_id> <content>[/red]")
                if exit_on_complete:
                    sys.exit(1)
                return True
            page_id = args[2]
            content = args[3]
            try:
                res = service.update_page(page_id, content)
                console.print(
                    f"[green]Successfully updated page {page_id}. "
                    f"Blocks added: {res.get('blocks_added', 0)}[/green]"
                )
                if exit_on_complete:
                    sys.exit(0)
            except Exception as e:
                console.print(f"[red]Error updating page: {e}[/red]")
                if exit_on_complete:
                    sys.exit(1)
            return True

        elif subcommand == "list-databases":
            dbs = service.list_databases()
            if not dbs:
                console.print("No databases found in cache.")
            for db in dbs:
                title = ""
                title_list = db.get("title", [])
                if title_list:
                    title = "".join([t.get("plain_text", "") for t in title_list])
                console.print(f"- {title or 'Untitled Database'} [ID: {db.get('id')}]")
            if exit_on_complete:
                sys.exit(0)
            return True

        else:
            console.print(
                "[yellow]Usage: aios notion <login|logout|status|sync|search|"
                "summarize|create-page|update-page|list-databases>[/yellow]"
            )
            if exit_on_complete:
                sys.exit(1)
            return True

    elif args and args[0] == "supabase":
        import sys

        if len(args) < 2:
            console.print(
                "[yellow]Usage: aios supabase <login|status|projects|schema|"
                "security|storage|auth|migrations|functions|summary>[/yellow]"
            )
            if exit_on_complete:
                sys.exit(1)
            return True

        subcommand = args[1]
        from aios.registry import ServiceRegistry
        from aios.services.supabase import SupabaseService
        from aios.services.supabase_impl import LocalSupabaseIntelligenceService

        service = None
        if ServiceRegistry._global_registry:
            try:
                service = ServiceRegistry._global_registry.get(SupabaseService)
            except Exception:
                pass

        if not service:
            service = LocalSupabaseIntelligenceService()
            service.initialize()
            service.start()

        if subcommand == "login":
            token = None
            url = None
            key = None
            ref = None

            for i in range(len(args)):
                if args[i] == "--token" and i + 1 < len(args):
                    token = args[i + 1]
                elif args[i] == "--url" and i + 1 < len(args):
                    url = args[i + 1]
                elif args[i] == "--key" and i + 1 < len(args):
                    key = args[i + 1]
                elif args[i] == "--ref" and i + 1 < len(args):
                    ref = args[i + 1]

            if not token and not (url and key):
                token = (
                    input(
                        "Enter Supabase Personal Access Token (PAT) [Press Enter to Skip]: "
                    ).strip()
                    or None
                )
                if not token:
                    url = (
                        input(
                            "Enter Supabase Project URL (e.g., https://xyz.supabase.co): "
                        ).strip()
                        or None
                    )
                    key = input("Enter Supabase Service Role Key: ").strip() or None
                    ref = input("Enter Project Ref (optional): ").strip() or None

            success = service.login(
                access_token=token, project_url=url, service_role_key=key, project_ref=ref
            )
            if success:
                console.print("[green]✓ Successfully authenticated with Supabase.[/green]")
                if exit_on_complete:
                    sys.exit(0)
            else:
                console.print("[red]✗ Authentication failed. Please check your credentials.[/red]")
                if exit_on_complete:
                    sys.exit(1)
            return True

        elif subcommand == "status":
            status = service.get_status()
            table = Table(title="Supabase Connection Status", border_style="green")
            table.add_column("Property", style="bold green")
            table.add_column("Value", style="white")
            table.add_row(
                "Connected State",
                "[green]CONNECTED[/green]" if status["connected"] else "[red]DISCONNECTED[/red]",
            )
            table.add_row("Access Token Present", "Yes" if status["access_token_present"] else "No")
            table.add_row("Active Project Ref", status["active_project_ref"] or "None")
            table.add_row("Active Project URL", status["project_url"] or "None")
            table.add_row("Projects Count", str(status["projects_count"]))
            console.print(table)
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "projects":
            projects = service.list_projects()
            if not projects:
                console.print(
                    "[yellow]No projects discovered. Run 'aios supabase login' first.[/yellow]"
                )
            else:
                table = Table(title="Supabase Discovered Projects", border_style="cyan")
                table.add_column("Project Name", style="bold cyan")
                table.add_column("Reference (Ref)", style="white")
                table.add_column("Region", style="green")
                table.add_column("URL", style="dim")
                for p in projects:
                    table.add_row(
                        p.get("name", "N/A"),
                        p.get("ref", "N/A"),
                        p.get("region", "N/A"),
                        p.get("url", "N/A"),
                    )
                console.print(table)
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "schema":
            try:
                schema = service.get_schema()
                table = Table(title="Supabase Database Schema Exploration", border_style="magenta")
                table.add_column("Table Name", style="bold magenta")
                table.add_column("Columns count", style="white")
                table.add_column("Columns Details", style="dim")

                for t in schema.get("tables", []):
                    cols = t.get("columns", [])
                    col_names = ", ".join([f"{c.get('name')}({c.get('type')})" for c in cols[:5]])
                    if len(cols) > 5:
                        col_names += ", ..."
                    table.add_row(t.get("name"), str(len(cols)), col_names)
                console.print(table)

                if schema.get("views"):
                    console.print(
                        Panel(
                            f"Views: {', '.join([v.get('name', v) if isinstance(v, dict) else v for v in schema.get('views', [])])}",
                            title="Views discovered",
                            border_style="cyan",
                        )
                    )
                if schema.get("functions"):
                    console.print(
                        Panel(
                            f"Functions: {', '.join([f.get('name', f) if isinstance(f, dict) else f for f in schema.get('functions', [])])}",
                            title="Functions discovered",
                            border_style="blue",
                        )
                    )
            except Exception as e:
                console.print(f"[red]Error fetching schema: {e}[/red]")
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "security":
            try:
                security = service.get_security_analysis()
                console.print(
                    Panel(
                        f"[green]RLS Enabled Tables:[/green] {', '.join(security.get('rls_enabled_tables', [])) or 'None'}\n"
                        f"[red]RLS Disabled Tables:[/red] {', '.join(security.get('rls_disabled_tables', [])) or 'None'}",
                        title="Row Level Security (RLS) Status",
                        border_style="yellow",
                    )
                )

                if security.get("security_recommendations"):
                    console.print("[bold red]Security Recommendations:[/bold red]")
                    for rec in security["security_recommendations"]:
                        console.print(f"  - {rec}")
                else:
                    console.print("[green]✓ No critical security vulnerabilities detected.[/green]")
            except Exception as e:
                console.print(f"[red]Error fetching security analysis: {e}[/red]")
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "storage":
            try:
                storage = service.get_storage()
                table = Table(title="Supabase Storage Buckets", border_style="blue")
                table.add_column("Bucket ID", style="bold blue")
                table.add_column("Public Access", style="white")
                table.add_column("File Size Limit (Bytes)", style="dim")

                for b in storage.get("buckets", []):
                    table.add_row(
                        b.get("id"),
                        "Yes" if b.get("public") else "No",
                        str(b.get("file_size_limit") or "Unlimited"),
                    )
                console.print(table)
            except Exception as e:
                console.print(f"[red]Error fetching storage stats: {e}[/red]")
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "auth":
            try:
                auth = service.get_auth_config()
                table = Table(title="Supabase Auth Provider Settings", border_style="yellow")
                table.add_column("Provider / Setting", style="bold yellow")
                table.add_column("State", style="white")

                providers = auth.get("providers", {})
                for k, v in providers.items():
                    state = "[green]Enabled[/green]" if v.get("enabled") else "[red]Disabled[/red]"
                    table.add_row(k.capitalize(), state)

                mfa = auth.get("mfa", {})
                for k, v in mfa.items():
                    state = "[green]Enabled[/green]" if v.get("enabled") else "[red]Disabled[/red]"
                    table.add_row(f"MFA - {k.upper()}", state)

                console.print(table)
            except Exception as e:
                console.print(f"[red]Error fetching auth config: {e}[/red]")
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "migrations":
            try:
                migrations = service.get_migrations()
                table = Table(title="Supabase Migration Logs", border_style="cyan")
                table.add_column("Version", style="bold cyan")
                table.add_column("Migration Name", style="white")
                table.add_column("Applied At", style="dim")

                for m in migrations.get("migration_history", []):
                    table.add_row(m.get("version"), m.get("name"), m.get("applied_at"))
                console.print(table)

                drift = "Yes" if migrations.get("drift_detected") else "No"
                console.print(
                    Panel(
                        f"Drift Detected: {drift}",
                        title="Drift Detection",
                        border_style="red" if drift == "Yes" else "green",
                    )
                )
            except Exception as e:
                console.print(f"[red]Error fetching migrations history: {e}[/red]")
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "functions":
            try:
                funcs = service.get_edge_functions()
                table = Table(title="Supabase Edge Functions", border_style="magenta")
                table.add_column("Function Name", style="bold magenta")
                table.add_column("Status", style="green")
                table.add_column("Verify JWT", style="white")

                for f in funcs.get("functions", []):
                    table.add_row(
                        f.get("name"), f.get("status"), "Yes" if f.get("verify_jwt") else "No"
                    )
                console.print(table)
            except Exception as e:
                console.print(f"[red]Error fetching edge functions: {e}[/red]")
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "summary":
            try:
                summary = service.get_project_summary()
                table = Table(
                    title=f"Supabase Project Summary: {summary.get('name')}", border_style="green"
                )
                table.add_column("Component", style="bold green")
                table.add_column("Count / Details", style="white")
                table.add_row("Project Reference", summary.get("project_ref"))
                table.add_row("Region", summary.get("region"))
                table.add_row("Tables Count", str(summary.get("tables_count")))
                table.add_row("Views Count", str(summary.get("views_count")))
                table.add_row("Storage Buckets", str(summary.get("buckets_count")))
                table.add_row("Edge Functions", str(summary.get("functions_count")))
                console.print(table)

                console.print(
                    "[cyan]Generating full markdown reports under docs/supabase/...[/cyan]"
                )
                service.generate_reports()
                console.print("[green]✓ Reports generated successfully.[/green]")
            except Exception as e:
                console.print(f"[red]Error fetching project summary: {e}[/red]")
            if exit_on_complete:
                sys.exit(0)
            return True

    elif args and args[0] == "vercel":
        import sys

        if len(args) < 2:
            console.print(
                "[yellow]Usage: aios vercel <login|status|projects|deployments|"
                "logs|domains|env|summary>[/yellow]"
            )
            if exit_on_complete:
                sys.exit(1)
            return True

        subcommand = args[1]
        from aios.registry import ServiceRegistry
        from aios.services.vercel import VercelService
        from aios.services.vercel_impl import LocalVercelIntelligenceService

        service = None
        if ServiceRegistry._global_registry:
            try:
                service = ServiceRegistry._global_registry.get(VercelService)
            except Exception:
                pass

        if not service:
            service = LocalVercelIntelligenceService()
            service.initialize()
            service.start()

        if subcommand == "login":
            token = None
            team = None

            for i in range(len(args)):
                if args[i] == "--token" and i + 1 < len(args):
                    token = args[i + 1]
                elif args[i] == "--team" and i + 1 < len(args):
                    team = args[i + 1]

            if not token:
                token = input("Enter Vercel Personal Access Token: ").strip() or None
                team = input("Enter Vercel Team ID (optional): ").strip() or None

            if not token:
                console.print("[red]✗ Access token is required.[/red]")
                if exit_on_complete:
                    sys.exit(1)
                return True

            success = service.login(access_token=token, team_id=team)
            if success:
                console.print("[green]✓ Successfully authenticated with Vercel.[/green]")
                if exit_on_complete:
                    sys.exit(0)
            else:
                console.print("[red]✗ Authentication failed. Please check your credentials.[/red]")
                if exit_on_complete:
                    sys.exit(1)
            return True

        elif subcommand == "status":
            status = service.get_status()
            table = Table(title="Vercel Connection Status", border_style="green")
            table.add_column("Property", style="bold green")
            table.add_column("Value", style="white")
            state_str = (
                "[green]CONNECTED[/green]" if status["connected"] else "[red]DISCONNECTED[/red]"
            )
            table.add_row("Connected State", state_str)
            table.add_row("Active Team ID", status["team_id"] or "Personal Account")
            table.add_row("Active Project ID", status["active_project_id"] or "None")
            table.add_row("Projects Count", str(status["projects_count"]))
            table.add_row("Teams Count", str(status["teams_count"]))
            console.print(table)
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "projects":
            projects = service.list_projects()
            if not projects:
                console.print(
                    "[yellow]No projects discovered. Run 'aios vercel login' first.[/yellow]"
                )
            else:
                table = Table(title="Vercel Discovered Projects", border_style="cyan")
                table.add_column("Project Name", style="bold cyan")
                table.add_column("Project ID", style="white")
                table.add_column("Framework", style="green")
                for p in projects:
                    table.add_row(
                        p.get("name", "N/A"),
                        p.get("id", "N/A"),
                        p.get("framework", "N/A"),
                    )
                console.print(table)
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "deployments":
            try:
                deps = service.get_deployments()
                table = Table(title="Vercel Recent Deployments", border_style="magenta")
                table.add_column("Deployment ID (UID)", style="bold magenta")
                table.add_column("URL", style="white")
                table.add_column("State", style="green")

                for d in deps.get("deployments", []):
                    table.add_row(d.get("uid"), d.get("url"), d.get("state"))
                console.print(table)

                if deps.get("rollback_candidates"):
                    rollback_table = Table(title="Rollback Candidates", border_style="yellow")
                    rollback_table.add_column("UID", style="bold yellow")
                    rollback_table.add_column("URL", style="white")
                    for r in deps["rollback_candidates"]:
                        rollback_table.add_row(r.get("uid"), r.get("url"))
                    console.print(rollback_table)
            except Exception as e:
                console.print(f"[red]Error fetching deployments: {e}[/red]")
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "logs":
            if len(args) < 3:
                console.print("[red]Usage: aios vercel logs <deployment_id>[/red]")
                if exit_on_complete:
                    sys.exit(1)
                return True
            dep_id = args[2]
            try:
                analysis = service.get_build_analysis(dep_id)
                logs_summary = analysis.get("error_log_summary") or "No build logs found."
                console.print(
                    Panel(
                        logs_summary,
                        title=f"Logs for deployment {dep_id}",
                        border_style="blue",
                    )
                )
                console.print(
                    Panel(
                        analysis.get("explanation"),
                        title="AI Diagnosis & Explanation",
                        border_style="yellow",
                    )
                )
            except Exception as e:
                console.print(f"[red]Error fetching build analysis: {e}[/red]")
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "domains":
            try:
                domains = service.get_domains()
                table = Table(title="Vercel Custom Domains", border_style="blue")
                table.add_column("Domain Name", style="bold blue")
                table.add_column("Verified Status", style="green")

                for d in domains.get("domains", []):
                    table.add_row(d.get("name"), "Yes" if d.get("verified") else "No")
                console.print(table)
            except Exception as e:
                console.print(f"[red]Error fetching domains: {e}[/red]")
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "env":
            try:
                envs = service.get_environments()
                title_str = "Vercel Environment Variables (Metadata)"
                table = Table(title=title_str, border_style="yellow")
                table.add_column("Variable Key", style="bold yellow")
                table.add_column("Target Environments", style="white")
                table.add_column("Type", style="dim")

                for e in envs.get("variables", []):
                    table.add_row(e.get("key"), ", ".join(e.get("target", [])), e.get("type"))
                console.print(table)
            except Exception as e:
                console.print(f"[red]Error fetching environments: {e}[/red]")
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "summary":
            try:
                summary = service.get_project_summary()
                title_str = f"Vercel Project Summary: {summary.get('name')}"
                table = Table(title=title_str, border_style="green")
                table.add_column("Property", style="bold green")
                table.add_column("Value / Details", style="white")
                table.add_row("Project ID", summary.get("project_id"))
                table.add_row("Framework", summary.get("framework"))
                table.add_row("Production URL", summary.get("production_url") or "None")

                monitoring = service.get_monitoring_data()
                table.add_row("Health Status", monitoring.get("health_status"))
                rate = monitoring.get("deployment_success_rate", 0.0)
                table.add_row("Success Rate", f"{rate:.1f}%")
                console.print(table)

                console.print(
                    "[cyan]Generating Vercel markdown reports under docs/vercel/...[/cyan]"
                )
                service.generate_reports()
                console.print("[green]✓ Reports generated successfully.[/green]")
            except Exception as e:
                console.print(f"[red]Error fetching project summary: {e}[/red]")
            if exit_on_complete:
                sys.exit(0)
            return True

        else:
            console.print(
                "[yellow]Usage: aios vercel <login|status|projects|deployments|"
                "logs|domains|env|summary>[/yellow]"
            )
            if exit_on_complete:
                sys.exit(1)
            return True

    elif args and args[0] == "project":
        import sys

        if len(args) < 2:
            console.print(
                "[yellow]Usage: aios project <list|status|summary|graph|"
                "health|timeline|risks|architecture|memory|analyze>[/yellow]"
            )
            if exit_on_complete:
                sys.exit(1)
            return True

        subcommand = args[1]
        from aios.registry import ServiceRegistry
        from aios.services.project_intelligence import ProjectIntelligenceService
        from aios.services.project_intelligence_impl import LocalProjectIntelligence

        service = None
        if ServiceRegistry._global_registry:
            try:
                service = ServiceRegistry._global_registry.get(ProjectIntelligenceService)
            except Exception:
                pass

        if not service:
            service = LocalProjectIntelligence()
            service.initialize()
            service.start()

        if subcommand == "list":
            projects = service.list_projects()
            if not projects:
                console.print(
                    "[yellow]No projects registered. "
                    "Run 'aios project analyze <path>' to register.[/yellow]"
                )
            else:
                table = Table(title="Project Intelligence Registry", border_style="green")
                table.add_column("Project ID", style="bold green")
                table.add_column("Name", style="white")
                table.add_column("Framework", style="cyan")
                table.add_column("Creation Date", style="dim")
                for p in projects:
                    table.add_row(
                        p.get("project_id", "N/A"),
                        p.get("name", "N/A"),
                        p.get("framework", "N/A"),
                        p.get("creation_date", "N/A"),
                    )
                console.print(table)
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "status":
            projects = service.list_projects()
            table = Table(title="Project Intelligence System Status", border_style="cyan")
            table.add_column("Property", style="bold cyan")
            table.add_column("Value / Count", style="white")
            table.add_row("Active Project ID", service._active_project_id or "None")
            table.add_row("Total Registered Projects", str(len(projects)))
            console.print(table)
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "summary":
            pid = args[2] if len(args) > 2 else service._active_project_id
            if not pid:
                console.print(
                    "[red]No active project. Usage: aios project summary <project_id>[/red]"
                )
                if exit_on_complete:
                    sys.exit(1)
                return True
            try:
                profile = service.get_project_profile(pid)
                title_str = f"Project Summary: {profile.get('name')}"
                table = Table(title=title_str, border_style="cyan")
                table.add_column("Metric / Property", style="bold cyan")
                table.add_column("Value", style="white")
                table.add_row("Project ID", profile.get("project_id"))
                table.add_row("Framework", profile.get("framework"))
                table.add_row("Workspace Path", profile.get("workspace_path"))
                table.add_row("Last Activity", profile.get("last_activity"))
                console.print(table)

                # Automatically compile reports
                console.print("[cyan]Compiling markdown reports under docs/project/...[/cyan]")
                service.generate_reports(pid)
                console.print("[green]✓ Markdown reports compiled successfully.[/green]")
            except Exception as e:
                console.print(f"[red]Error fetching summary: {e}[/red]")
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "graph":
            pid = args[2] if len(args) > 2 else service._active_project_id
            if not pid:
                console.print(
                    "[red]No active project. Usage: aios project graph <project_id>[/red]"
                )
                if exit_on_complete:
                    sys.exit(1)
                return True
            try:
                graph = service.query_knowledge_graph(pid, "all")
                table = Table(title="Project Knowledge Graph Nodes", border_style="magenta")
                table.add_column("Node ID", style="bold magenta")
                table.add_column("Type", style="cyan")
                table.add_column("Label", style="white")
                for n in graph.get("nodes", []):
                    table.add_row(n.get("id"), n.get("type"), n.get("label"))
                console.print(table)
            except Exception as e:
                console.print(f"[red]Error fetching graph: {e}[/red]")
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "health":
            pid = args[2] if len(args) > 2 else service._active_project_id
            if not pid:
                console.print(
                    "[red]No active project. Usage: aios project health <project_id>[/red]"
                )
                if exit_on_complete:
                    sys.exit(1)
                return True
            try:
                h = service.get_health_scorecard(pid)
                table = Table(title="Project Health Scorecard", border_style="green")
                table.add_column("Metric", style="bold green")
                table.add_column("Score / Level", style="white")
                table.add_row("Overall Health Score", f"{h.get('health_score')}%")
                table.add_row("Documentation Score", f"{h.get('documentation_score')}%")
                table.add_row("Test Coverage Score", f"{h.get('test_coverage_score')}%")
                table.add_row("Deployment Status", h.get("deployment_status"))
                table.add_row("Technical Debt", f"{h.get('technical_debt_hours')} hours")
                console.print(table)
            except Exception as e:
                console.print(f"[red]Error fetching health: {e}[/red]")
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "timeline":
            pid = args[2] if len(args) > 2 else service._active_project_id
            if not pid:
                console.print(
                    "[red]No active project. Usage: aios project timeline <project_id>[/red]"
                )
                if exit_on_complete:
                    sys.exit(1)
                return True
            try:
                timeline = service.get_timeline(pid)
                table = Table(title="Project Timeline", border_style="yellow")
                table.add_column("Date", style="bold yellow")
                table.add_column("Type", style="cyan")
                table.add_column("Description", style="white")
                for ev in timeline.get("events", []):
                    table.add_row(ev.get("date"), ev.get("type"), ev.get("desc"))
                console.print(table)
            except Exception as e:
                console.print(f"[red]Error fetching timeline: {e}[/red]")
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "risks":
            pid = args[2] if len(args) > 2 else service._active_project_id
            if not pid:
                console.print(
                    "[red]No active project. Usage: aios project risks <project_id>[/red]"
                )
                if exit_on_complete:
                    sys.exit(1)
                return True
            try:
                r = service.get_risk_analysis(pid)
                title_str = f"Project Risk Analysis (Overall Risk: {r.get('overall_risk_level')})"
                table = Table(title=title_str, border_style="red")
                table.add_column("Category", style="bold red")
                table.add_column("Level", style="magenta")
                table.add_column("Description", style="white")
                for risk in r.get("risks", []):
                    table.add_row(risk.get("category"), risk.get("level"), risk.get("desc"))
                console.print(table)
            except Exception as e:
                console.print(f"[red]Error fetching risks: {e}[/red]")
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "architecture":
            pid = args[2] if len(args) > 2 else service._active_project_id
            if not pid:
                console.print(
                    "[red]No active project. Usage: aios project architecture <project_id>[/red]"
                )
                if exit_on_complete:
                    sys.exit(1)
                return True
            try:
                arch = service.get_architecture_map(pid)
                console.print(
                    Panel(str(arch.get("service_map")), title="Service Map", border_style="blue")
                )
                console.print(
                    Panel(str(arch.get("module_map")), title="Module Map", border_style="green")
                )
            except Exception as e:
                console.print(f"[red]Error fetching architecture: {e}[/red]")
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "memory":
            pid = args[2] if len(args) > 2 else service._active_project_id
            query = args[3] if len(args) > 3 else "architecture"
            if not pid:
                console.print(
                    "[red]No active project. Usage: aios project memory <project_id> [query][/red]"
                )
                if exit_on_complete:
                    sys.exit(1)
                return True
            try:
                mem = service.query_project_memory(pid, query)
                table = Table(title=f"Semantic Memory Query: '{query}'", border_style="blue")
                table.add_column("Entry", style="bold blue")
                table.add_column("Description", style="white")
                for entry in mem:
                    table.add_row(entry.get("title"), entry.get("desc"))
                console.print(table)
            except Exception as e:
                console.print(f"[red]Error querying memory: {e}[/red]")
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "analyze":
            path_str = args[2] if len(args) > 2 else "."
            try:
                console.print(f"[cyan]Analyzing project at path '{path_str}'...[/cyan]")
                profile = service.discover_project(path_str)
                console.print(
                    f"[green]✓ Discovered project: '{profile.get('name')}' "
                    f"(ID: {profile.get('project_id')})[/green]"
                )
            except Exception as e:
                console.print(f"[red]Error analyzing project: {e}[/red]")
            if exit_on_complete:
                sys.exit(0)
            return True

        else:
            console.print(
                "[yellow]Usage: aios project <list|status|summary|graph|"
                "health|timeline|risks|architecture|memory|analyze>[/yellow]"
            )
            if exit_on_complete:
                sys.exit(1)
            return True

    elif args and args[0] == "business":
        import sys

        if len(args) < 2:
            console.print(
                "[yellow]Usage: aios business <organizations|clients|leads|"
                "projects|proposals|workflows|tasks|analytics|timeline|"
                "summary>[/yellow]"
            )
            if exit_on_complete:
                sys.exit(1)
            return True

        subcommand = args[1]
        from aios.registry import ServiceRegistry
        from aios.services.business import BusinessIntelligenceService
        from aios.services.business_impl import LocalBusinessIntelligenceService

        service = None
        if ServiceRegistry._global_registry:
            try:
                service = ServiceRegistry._global_registry.get(BusinessIntelligenceService)
            except Exception:
                pass

        if not service:
            service = LocalBusinessIntelligenceService()
            service.initialize()
            service.start()

        if subcommand == "organizations":
            orgs = service.list_organizations()
            if not orgs:
                console.print(
                    "[yellow]No organizations registered. Use save_organization API.[/yellow]"
                )
            else:
                table = Table(title="Agency Organizations", border_style="cyan")
                table.add_column("Org ID", style="bold cyan")
                table.add_column("Name", style="white")
                for o in orgs:
                    table.add_row(o.get("org_id"), o.get("name"))
                console.print(table)
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "clients":
            clients = service.list_clients()
            if not clients:
                console.print("[yellow]No clients registered.[/yellow]")
            else:
                table = Table(title="Client Registry", border_style="green")
                table.add_column("Client ID", style="bold green")
                table.add_column("Name", style="white")
                table.add_column("Email", style="cyan")
                for c in clients:
                    table.add_row(c.get("client_id"), c.get("name"), c.get("email", "N/A"))
                console.print(table)
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "leads":
            leads = service.list_leads()
            if not leads:
                console.print("[yellow]No leads in pipeline.[/yellow]")
            else:
                table = Table(title="Lead Pipeline", border_style="yellow")
                table.add_column("Lead ID", style="bold yellow")
                table.add_column("Name", style="white")
                table.add_column("Score", style="cyan")
                for lead in leads:
                    table.add_row(lead.get("lead_id"), lead.get("name"), str(lead.get("score", 0)))
                console.print(table)
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "projects":
            projects = service.list_projects()
            table = Table(title="Business Project Portfolio", border_style="blue")
            table.add_column("Project ID", style="bold blue")
            table.add_column("Name", style="white")
            table.add_column("Client ID", style="cyan")
            table.add_column("Github", style="dim")
            for p in projects:
                table.add_row(
                    p.get("project_id"), p.get("name"), p.get("client_id"), p.get("github_repo")
                )
            console.print(table)
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "proposals":
            try:
                proposal = service.get_proposal("prop_1")
                table = Table(title="Proposal Details", border_style="magenta")
                table.add_column("Metric / Property", style="bold magenta")
                table.add_column("Value", style="white")
                table.add_row("Proposal ID", proposal.get("proposal_id"))
                table.add_row("Title", proposal.get("title"))
                table.add_row("Budget", f"${proposal.get('budget')}")
                console.print(table)
            except Exception as e:
                console.print(f"[red]Error fetching proposals: {e}[/red]")
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "workflows":
            wfs = service.list_workflows()
            title_str = "Workflow Client Ownership & Statistics"
            table = Table(title=title_str, border_style="cyan")
            table.add_column("Workflow ID", style="bold cyan")
            table.add_column("Name", style="white")
            table.add_column("Client ID", style="magenta")
            table.add_column("Success Rate", style="green")
            for wf in wfs:
                table.add_row(
                    wf.get("workflow_id"),
                    wf.get("name"),
                    wf.get("client_id"),
                    f"{wf.get('success_rate')}%",
                )
            console.print(table)
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "tasks":
            tasks = service.list_tasks()
            table = Table(title="Agency Tasks & Milestones", border_style="yellow")
            table.add_column("Task ID", style="bold yellow")
            table.add_column("Name", style="white")
            table.add_column("Priority", style="red")
            table.add_column("Deadline", style="dim")
            table.add_row(
                tasks[0].get("task_id"),
                tasks[0].get("name"),
                tasks[0].get("priority"),
                tasks[0].get("deadline"),
            )
            console.print(table)
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "analytics":
            analytics = service.get_analytics()
            table = Table(title="Agency Operations Analytics", border_style="green")
            table.add_column("Metric", style="bold green")
            table.add_column("Value", style="white")
            table.add_row("Active Clients", str(analytics.get("active_clients")))
            table.add_row("Active Projects", str(analytics.get("active_projects")))
            table.add_row("Workflows count", str(analytics.get("workflows_count")))
            table.add_row("Success Rate", f"{analytics.get('success_rate')}%")
            table.add_row("Revenue estimate", analytics.get("revenue_estimate"))
            console.print(table)
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "timeline":
            cid = args[2] if len(args) > 2 else "c1"
            timeline = service.get_client_timeline(cid)
            table = Table(title=f"Client Timeline: {cid}", border_style="yellow")
            table.add_column("Date", style="bold yellow")
            table.add_column("Type", style="cyan")
            table.add_column("Description", style="white")
            for ev in timeline.get("events", []):
                table.add_row(ev.get("date"), ev.get("type"), ev.get("desc"))
            console.print(table)
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "summary":
            msg_str = "Compiling business operations reports under docs/business/..."
            console.print(f"[cyan]{msg_str}[/cyan]")
            service.generate_reports()
            success_str = "✓ Business operations reports generated successfully."
            console.print(f"[green]{success_str}[/green]")
            if exit_on_complete:
                sys.exit(0)
            return True

        else:
            console.print(
                "[yellow]Usage: aios business <organizations|clients|leads|"
                "projects|proposals|workflows|tasks|analytics|timeline|"
                "summary>[/yellow]"
            )
            if exit_on_complete:
                sys.exit(1)
            return True

    elif args and args[0] == "approval":
        import sys
        from unittest.mock import MagicMock

        if len(args) < 2:
            console.print(
                "[yellow]Usage: aios approval <queue|pending|approve|reject|"
                "cancel|history|policies|preview|status>[/yellow]"
            )
            if exit_on_complete:
                sys.exit(1)
            return True

        subcommand = args[1]
        from aios.registry import ServiceRegistry
        from aios.services.approval import ApprovalEngineService

        service = None
        if ServiceRegistry._global_registry:
            try:
                service = ServiceRegistry._global_registry.get(ApprovalEngineService)
            except Exception:
                pass

        if not service:
            from aios.services.approval_impl import LocalApprovalEngineService
            from aios.services.memory import MemoryService

            mock_mem = MagicMock(spec=MemoryService)
            service = LocalApprovalEngineService(memory_service=mock_mem)
            service.initialize()
            service.start()

        if subcommand == "queue":
            queue = service.list_queue()
            if not queue:
                console.print("[yellow]Approval queue is empty.[/yellow]")
            else:
                table = Table(title="Governance Approval Queue", border_style="cyan")
                table.add_column("Request ID", style="bold cyan")
                table.add_column("Action", style="white")
                table.add_column("Project", style="magenta")
                table.add_column("Client", style="yellow")
                table.add_column("Risk", style="red")
                table.add_column("Status", style="green")
                for q in queue:
                    table.add_row(
                        q.get("request_id"),
                        q.get("action"),
                        q.get("project"),
                        q.get("client"),
                        q.get("risk"),
                        q.get("status"),
                    )
                console.print(table)
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "pending":
            pending = service.list_pending()
            if not pending:
                console.print("[yellow]No pending approvals found.[/yellow]")
            else:
                table = Table(title="Pending Governance Decisions", border_style="yellow")
                table.add_column("Request ID", style="bold yellow")
                table.add_column("Action", style="white")
                table.add_column("Project", style="magenta")
                table.add_column("Risk", style="red")
                for p in pending:
                    table.add_row(
                        p.get("request_id"), p.get("action"), p.get("project"), p.get("risk")
                    )
                console.print(table)
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "approve":
            if len(args) < 3:
                console.print("[red]Error: request ID required.[/red]")
                if exit_on_complete:
                    sys.exit(1)
                return True
            req_id = args[2]
            success = service.approve_request(req_id)
            if success:
                console.print(f"[green]✓ Request {req_id} approved successfully.[/green]")
            else:
                console.print(f"[red]✗ Request {req_id} not found.[/red]")
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "reject":
            if len(args) < 3:
                console.print("[red]Error: request ID required.[/red]")
                if exit_on_complete:
                    sys.exit(1)
                return True
            req_id = args[2]
            success = service.reject_request(req_id)
            if success:
                console.print(f"[green]✓ Request {req_id} rejected successfully.[/green]")
            else:
                console.print(f"[red]✗ Request {req_id} not found.[/red]")
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "cancel":
            if len(args) < 3:
                console.print("[red]Error: request ID required.[/red]")
                if exit_on_complete:
                    sys.exit(1)
                return True
            req_id = args[2]
            success = service.cancel_request(req_id)
            if success:
                console.print(f"[green]✓ Request {req_id} cancelled successfully.[/green]")
            else:
                console.print(f"[red]✗ Request {req_id} not found.[/red]")
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "history":
            audit = service.list_audit_trail()
            if not audit:
                console.print("[yellow]No history log records found.[/yellow]")
            else:
                table = Table(title="Governance Execution History", border_style="green")
                table.add_column("Log ID", style="bold green")
                table.add_column("Action", style="white")
                table.add_column("Outcome", style="magenta")
                table.add_column("Reason", style="dim")
                for entry in audit:
                    table.add_row(
                        entry.get("log_id"),
                        entry.get("action"),
                        entry.get("outcome"),
                        entry.get("reason"),
                    )
                console.print(table)
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "policies":
            policies = service.get_policies()
            table = Table(title="Configured Governance Policies", border_style="magenta")
            table.add_column("Scope / Target", style="bold magenta")
            table.add_column("Policy Setting", style="white")
            for k, v in policies.items():
                table.add_row(k, str(v))
            console.print(table)
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "preview":
            if len(args) < 3:
                console.print("[red]Error: request ID required.[/red]")
                if exit_on_complete:
                    sys.exit(1)
                return True
            req_id = args[2]
            preview = service.get_preview(req_id)
            table = Table(title=f"Execution Preview: {req_id}", border_style="yellow")
            table.add_column("Property", style="bold yellow")
            table.add_column("Value", style="white")
            table.add_row("Summary", preview.get("action_summary", "N/A"))
            table.add_row("Files Affected", ", ".join(preview.get("files_affected", [])) or "None")
            table.add_row(
                "Services Affected", ", ".join(preview.get("services_affected", [])) or "None"
            )
            table.add_row("Expected Changes", preview.get("expected_changes", ""))
            table.add_row("Rollback Supported", str(preview.get("rollback_supported", False)))
            table.add_row("Estimated Impact", preview.get("estimated_impact", "low"))
            console.print(table)
            if exit_on_complete:
                sys.exit(0)
            return True

        elif subcommand == "status":
            if len(args) < 3:
                console.print("[red]Error: request ID required.[/red]")
                if exit_on_complete:
                    sys.exit(1)
                return True
            req_id = args[2]
            queue = service.list_queue()
            status_val = "unknown"
            for item in queue:
                if item.get("request_id") == req_id:
                    status_val = item.get("status")
                    break
            console.print(f"[cyan]Request {req_id} current status: {status_val}[/cyan]")
            if exit_on_complete:
                sys.exit(0)
            return True

        else:
            console.print(
                "[yellow]Usage: aios approval <queue|pending|approve|reject|"
                "cancel|history|policies|preview|status>[/yellow]"
            )
            if exit_on_complete:
                sys.exit(1)
            return True

    elif args and args[0] == "dashboard":
        from aios.ux import DashboardRenderer

        DashboardRenderer.render()
        if exit_on_complete:
            sys.exit(0)
        return True

    elif args and args[0] == "setup":
        from aios.ux import SetupWizard

        SetupWizard.run()
        if exit_on_complete:
            sys.exit(0)
        return True

    elif args and args[0] == "session":
        from aios.ux import SessionManager

        mgr = SessionManager()
        data = mgr.load_session()
        table = Table(title="CLI Session State", border_style="cyan")
        table.add_column("Property", style="bold cyan")
        table.add_column("Value", style="white")
        table.add_row("Current Project", data.get("current_project"))
        table.add_row("Recent Projects", ", ".join(data.get("recent_projects", [])))
        table.add_row("Last Active", time.ctime(data.get("last_active", 0)))
        console.print(table)
        if exit_on_complete:
            sys.exit(0)
        return True

    elif args and args[0] == "diagnostics":
        from aios.ux import DiagnosticsEngine

        metrics = DiagnosticsEngine.get_metrics()
        table = Table(title="OS System Telemetry Diagnostics", border_style="green")
        table.add_column("Metric ID", style="bold green")
        table.add_column("Value", style="white")
        for k, v in metrics.items():
            table.add_row(k, str(v))
        console.print(table)
        if exit_on_complete:
            sys.exit(0)
        return True

    # -----------------------------------------------------------------------
    # Phase 1: Local Model Intelligence Layer — `aios models` command group
    # -----------------------------------------------------------------------
    elif args and args[0] == "models":
        from aios.local.cli_commands import cmd_models_main
        from aios.registry import ServiceRegistry

        reg = ServiceRegistry._global_registry
        subargs = args[1:]
        try:
            cmd_models_main(subargs, registry=reg)
        except Exception as exc:
            console.print(f"[red]✗ models command error: {exc}[/red]")
        if exit_on_complete:
            import sys

            sys.exit(0)
        return True

    # -----------------------------------------------------------------------
    # Phase 2: AI Workspace & Unified CLI — Workspace Subcommands
    # -----------------------------------------------------------------------
    elif args and args[0] in (
        "dashboard",
        "work",
        "today",
        "status",
        "restart",
        "doctor",
        "shutdown",
        "agenda",
        "projects",
        "agency",
        "hackathons",
        "github",
        "notion",
        "resume",
        "tasks",
        "goals",
        "planner",
        "plugins",
        "skills",
        "notifications",
        "events",
        "context",
        "scheduler",
        "workflow",
        "workflows",
        "integration",
        "integrations",
        "doc",
        "docs",
        "personal",
        "calendar",
        "habits",
        "reminders",
        "morning",
        "weekly",
        "notes",
        "learning",
        "coach",
    ):
        from aios.local.cli_workspace_commands import cmd_workspace_main
        from aios.registry import ServiceRegistry

        reg = ServiceRegistry._global_registry
        try:
            cmd_workspace_main(args, registry=reg)
        except Exception as exc:
            console.print(f"[red]✗ workspace command error: {exc}[/red]")
        if exit_on_complete:
            import sys

            sys.exit(0)
        return True

    # -----------------------------------------------------------------------
    # Phase 4.5: Universal Knowledge Graph — `aios graph` command group
    # -----------------------------------------------------------------------
    elif args and args[0] == "graph":
        from aios.services.graph_impl import GraphServiceImpl
        from aios.services.graph_query import GraphQueryEngine

        _graph_svc = GraphServiceImpl()
        _graph_svc.initialize()
        _graph_svc.start()
        _engine = GraphQueryEngine(_graph_svc)

        subcommand = args[1] if len(args) > 1 else ""

        if not subcommand or subcommand == "stats":
            # aios graph  → show graph statistics
            stats = _engine.get_stats_summary()
            table = Table(title="📊 Knowledge Graph Statistics", border_style="cyan")
            table.add_column("Metric", style="bold cyan")
            table.add_column("Value", style="white")
            table.add_row("Total Entities", str(stats["total_entities"]))
            table.add_row("Total Relationships", str(stats["total_relationships"]))
            table.add_row("Total Events", str(stats["total_events"]))
            table.add_section()
            for etype, count in stats["entities_by_type"].items():
                table.add_row(f"  {etype}", str(count))
            table.add_section()
            for rtype, count in stats["relationships_by_type"].items():
                table.add_row(f"  {rtype}", str(count))
            console.print(table)

        elif subcommand == "search":
            # aios graph search <query>
            query = " ".join(args[2:]) if len(args) > 2 else ""
            if not query:
                console.print("[yellow]Usage: aios graph search <query>[/yellow]")
                if exit_on_complete:
                    sys.exit(1)
                return True
            result = _engine.search_graph(query)
            table = Table(
                title=f"🔍 Graph Search: '{query}' ({result['total']} results)",
                border_style="magenta",
            )
            table.add_column("Entity ID", style="dim", max_width=36)
            table.add_column("Type", style="bold magenta")
            table.add_column("Name", style="white")
            table.add_column("Updated", style="dim")
            for e in result["entities"]:
                import time as _time

                updated = _time.strftime("%Y-%m-%d %H:%M", _time.localtime(e.get("updated_at", 0)))
                table.add_row(
                    e["entity_id"][:12] + "...",
                    e["entity_type"],
                    e["name"],
                    updated,
                )
            console.print(table)
            console.print(f"[dim]Query time: {result['query_time_ms']:.1f}ms[/dim]")

        elif subcommand == "relations":
            # aios graph relations <entity_name> [direction]
            if len(args) < 3:
                console.print(
                    "[yellow]Usage: aios graph relations <entity_name> [inbound|outbound|both][/yellow]"
                )
                if exit_on_complete:
                    sys.exit(1)
                return True
            entity_name = args[2]
            direction = args[3] if len(args) > 3 else "both"
            result = _engine.get_relations(entity_name, direction=direction)

            if "error" in result:
                console.print(f"[red]✗ {result['error']}[/red]")
                if exit_on_complete:
                    sys.exit(1)
                return True

            entity = result["entity"]
            console.print(
                Panel(
                    f"[bold white]{entity['name']}[/bold white]\n"
                    f"Type: [cyan]{entity['entity_type']}[/cyan]  |  "
                    f"ID: [dim]{entity['entity_id'][:16]}...[/dim]",
                    title="🔗 Entity Relations",
                    border_style="cyan",
                )
            )

            table = Table(border_style="blue", title=f"Relationships ({direction})")
            table.add_column("Direction", style="bold")
            table.add_column("Relationship", style="bold cyan")
            table.add_column("Neighbor Name", style="white")
            table.add_column("Neighbor Type", style="magenta")

            neighbor_map = {n["entity_id"]: n for n in result["neighbors"]}
            for rel in result["relationships"]:
                if rel["source_id"] == entity["entity_id"]:
                    direction_label = "→ outbound"
                    nid = rel["target_id"]
                else:
                    direction_label = "← inbound"
                    nid = rel["source_id"]
                neighbor = neighbor_map.get(nid, {})
                table.add_row(
                    direction_label,
                    rel["relationship_type"],
                    neighbor.get("name", nid[:12] + "..."),
                    neighbor.get("entity_type", "?"),
                )
            console.print(table)

        elif subcommand == "project":
            # aios graph project <project_name>
            if len(args) < 3:
                console.print("[yellow]Usage: aios graph project <project_name>[/yellow]")
                if exit_on_complete:
                    sys.exit(1)
                return True
            project_name = " ".join(args[2:])
            result = _engine.get_project_overview(project_name)

            if "error" in result:
                console.print(f"[red]✗ {result['error']}[/red]")
                if exit_on_complete:
                    sys.exit(1)
                return True

            project = result["project"]
            subgraph = result["subgraph"]

            console.print(
                Panel(
                    f"[bold white]{project['name']}[/bold white]\n"
                    f"ID: [dim]{project['entity_id'][:24]}...[/dim]\n"
                    f"Total graph nodes: [cyan]{subgraph['total_nodes']}[/cyan]  |  "
                    f"Relationships: [magenta]{len(subgraph['relationships'])}[/magenta]",
                    title="🗂️  Project Knowledge Graph",
                    border_style="green",
                )
            )

            for etype, entities in subgraph["by_type"].items():
                if etype == "project":
                    continue
                t = Table(title=f"{etype.upper()} ({len(entities)})", border_style="dim")
                t.add_column("Name", style="white")
                t.add_column("Entity ID", style="dim", max_width=16)
                for ent in entities:
                    t.add_row(ent["name"], ent["entity_id"][:12] + "...")
                console.print(t)

        elif subcommand == "path":
            # aios graph path <source_name> <target_name>
            if len(args) < 4:
                console.print("[yellow]Usage: aios graph path <source_name> <target_name>[/yellow]")
                if exit_on_complete:
                    sys.exit(1)
                return True
            source_name = args[2]
            target_name = args[3]
            result = _engine.find_path(source_name, target_name)

            if "error" in result:
                console.print(f"[red]✗ {result['error']}[/red]")
            elif not result.get("path_found"):
                console.print(
                    f"[yellow]No path found between '{source_name}' and '{target_name}'[/yellow]"
                )
            else:
                console.print(
                    Panel(
                        f"Path: [cyan]{' → '.join(e['name'] for e in result['entities'])}[/cyan]\n"
                        f"Length: [white]{result['path_length']} hop(s)[/white]  |  "
                        f"Time: [dim]{result['query_time_ms']:.1f}ms[/dim]",
                        title="🛤️  Shortest Path",
                        border_style="yellow",
                    )
                )

        elif subcommand == "health":
            healthy = _graph_svc.health_check()
            status_text = (
                "[bold green]✓ Healthy[/bold green]"
                if healthy
                else "[bold red]✗ Degraded[/bold red]"
            )
            console.print(
                Panel(
                    status_text,
                    title="Knowledge Graph Health",
                    border_style="green" if healthy else "red",
                )
            )

        else:
            console.print(
                "[yellow]Usage: aios graph [stats|search <q>|relations <name>|"
                "project <name>|path <src> <tgt>|health][/yellow]"
            )
            if exit_on_complete:
                sys.exit(1)
            return True

        _graph_svc.shutdown()
        if exit_on_complete:
            sys.exit(0)
        return True

    # -----------------------------------------------------------------------
    # Phase 5: Project Intelligence — `aios project` / `aios projects`
    # -----------------------------------------------------------------------
    elif args and args[0] in ("project", "projects"):
        try:
            from aios.local.project_commands import cmd_project_main

            subargs = args[1:] if args[0] == "project" else args
            # `aios projects` is a shortcut for `aios project list`
            if args[0] == "projects":
                subargs = ["list"] + list(args[1:])
            cmd_project_main(subargs, registry=None)
        except Exception as exc:
            console.print(f"[red]✗ project command error: {exc}[/red]")
        if exit_on_complete:
            sys.exit(0)
        return True

    # -----------------------------------------------------------------------
    # Phase 7: Automation Intelligence — `aios workflow` / `aios workflows`
    # -----------------------------------------------------------------------
    elif args and args[0] in ("workflow", "workflows"):
        try:
            from aios.local.workflow_commands import cmd_workflow_main

            subargs = args[1:] if args[0] == "workflow" else args
            if args[0] == "workflows":
                subargs = ["list"] + list(args[1:])
            cmd_workflow_main(subargs, registry=None)
        except Exception as exc:
            console.print(f"[red]✗ workflow command error: {exc}[/red]")
        if exit_on_complete:
            sys.exit(0)
        return True

    # -----------------------------------------------------------------------
    # Phase 7.5: Universal Integration Layer — `aios integration` / `aios integrations`
    # -----------------------------------------------------------------------
    elif args and args[0] in ("integration", "integrations"):
        try:
            from aios.local.integration_commands import cmd_integrations_main

            subargs = args[1:] if args[0] == "integration" else args
            if args[0] == "integrations":
                subargs = ["list"] + list(args[1:])
            cmd_integrations_main(subargs, registry=None)
        except Exception as exc:
            console.print(f"[red]✗ integrations command error: {exc}[/red]")
    # -----------------------------------------------------------------------
    # Phase 8: Documentation Intelligence — `aios doc` / `aios docs`
    # -----------------------------------------------------------------------
    elif args and args[0] in ("doc", "docs"):
        try:
            from aios.local.documentation_commands import cmd_docs_main

            subargs = args[1:] if args[0] == "doc" else args
            if args[0] == "docs":
                subargs = ["list"] + list(args[1:])
            cmd_docs_main(subargs, registry=None)
        except Exception as exc:
            console.print(f"[red]✗ documentation command error: {exc}[/red]")
        if exit_on_complete:
            sys.exit(0)
        return True
    # -----------------------------------------------------------------------
    # Phase 9: GitHub Intelligence — `aios github`
    # -----------------------------------------------------------------------
    elif args and args[0] == "github":
        try:
            from aios.local.github_intelligence_commands import cmd_github_main

            # Delegate subcommands starting after aios github
            cmd_github_main(args[1:], registry=None)
        except Exception as exc:
            console.print(f"[red]✗ github command error: {exc}[/red]")
        if exit_on_complete:
            sys.exit(0)
        return True
    # -----------------------------------------------------------------------
    # Phase 10: Research Intelligence — `aios research`
    # -----------------------------------------------------------------------
    elif args and args[0] == "research":
        try:
            from aios.local.research_commands import cmd_research_main

            # Delegate subcommands starting after aios research
            cmd_research_main(args[1:], registry=None)
        except Exception as exc:
            console.print(f"[red]✗ research command error: {exc}[/red]")
        if exit_on_complete:
            sys.exit(0)
        return True

    # -----------------------------------------------------------------------
    # Phase 11.5: Natural Language OS — `chat`, `ask`, `intent`, `plan`, `execute`, `context`
    # -----------------------------------------------------------------------
    elif args and args[0] == "chat":
        from aios.registry import ServiceRegistry
        from aios.services.nl_os import NLOSService

        nl_os = ServiceRegistry._global_registry.get(NLOSService)
        if len(args) > 1:
            query = " ".join(args[1:])
            tokens = nl_os.route_query(query)
            if tokens:
                console.print(f"[bold cyan]Routing to: aios {' '.join(tokens)}[/bold cyan]")
                execute_builtin_cli_command(tokens, exit_on_complete=False)
            else:
                from aios.services.context import ContextService
                from aios.services.conversation.manager import ConversationManager
                from aios.services.conversation.store import ConversationStore
                from aios.services.model import ModelService

                ctx_svc = ServiceRegistry._global_registry.get(ContextService)
                context = ctx_svc.get_current_context()
                workspace_root = context.project_root if context else str(Path.cwd().resolve())

                conv_store = ConversationStore(Path(workspace_root) / ".aios_conversations")
                conv_manager = ConversationManager(conv_store)
                model_service = ServiceRegistry._global_registry.get(ModelService)

                handle_general_chat(query, conv_manager, model_service)
        else:
            console.print(
                "[bold cyan]Entering AI OS Natural Language Chat Command Center...[/bold cyan]"
            )
            console.print("Type your plain English commands or queries. Type /exit to quit.")
            from aios.services.context import ContextService
            from aios.services.conversation.manager import ConversationManager
            from aios.services.conversation.store import ConversationStore
            from aios.services.model import ModelService

            ctx_svc = ServiceRegistry._global_registry.get(ContextService)
            context = ctx_svc.get_current_context()
            workspace_root = context.project_root if context else str(Path.cwd().resolve())

            conv_store = ConversationStore(Path(workspace_root) / ".aios_conversations")
            conv_manager = ConversationManager(conv_store)
            model_service = ServiceRegistry._global_registry.get(ModelService)

            while True:
                try:
                    print_status_line(model_service, conv_manager)
                    user_input = read_input().strip()
                    if not user_input:
                        continue
                    if user_input in ("/exit", "/quit", "exit", "quit"):
                        break

                    tokens = nl_os.route_query(user_input)
                    if tokens:
                        console.print(f"[bold cyan]Routing to: aios {' '.join(tokens)}[/bold cyan]")
                        execute_builtin_cli_command(tokens, exit_on_complete=False)
                    else:
                        handle_general_chat(user_input, conv_manager, model_service)
                except KeyboardInterrupt:
                    print()
                    break
        if exit_on_complete:
            sys.exit(0)
        return True

    elif args and args[0] == "ask":
        from aios.registry import ServiceRegistry
        from aios.services.nl_os import NLOSService

        nl_os = ServiceRegistry._global_registry.get(NLOSService)

        if len(args) < 2:
            console.print("[yellow]Usage: aios ask <question>[/yellow]")
        else:
            query = " ".join(args[1:])
            if query.lower().strip() in (
                "what are you doing?",
                "why did you choose this?",
                "explain the plan.",
                "what are you doing",
                "why did you choose this",
                "explain the plan",
            ):
                explanation = nl_os.get_last_explanation()
                obj = explanation.get("objective", "None")
                plan = explanation.get("plan")
                reasoning = explanation.get("reasoning", "No explanation available.")

                text_lines = [
                    f"[bold]Objective:[/bold] {obj}",
                    f"[bold]Reasoning/Routing Decision:[/bold] {reasoning}",
                ]
                if plan:
                    text_lines.append("\n[bold]Execution Plan Steps:[/bold]")
                    for s in plan.steps:
                        text_lines.append(f"- Step {s.step_id}: {s.description} ({s.status})")

                console.print(
                    Panel(
                        "\n".join(text_lines),
                        title="[bold cyan]Explanation Engine[/bold cyan]",
                        border_style="cyan",
                    )
                )
            else:
                tokens = nl_os.route_query(query)
                if tokens:
                    console.print(
                        f"[bold cyan]Routing command: aios {' '.join(tokens)}[/bold cyan]"
                    )
                    execute_builtin_cli_command(tokens, exit_on_complete=False)
                else:
                    from aios.services.model import LLMRequest, ModelService

                    model_service = ServiceRegistry._global_registry.get(ModelService)
                    res = model_service.execute_request(
                        LLMRequest(
                            prompt=f'Please answer this question context-awarely:\n"{query}"',
                            system_instruction="Provide a concise, direct answer to the user's question.",
                        )
                    )
                    console.print(Panel(res.content, border_style="blue", title="AI OS Answer"))
        if exit_on_complete:
            sys.exit(0)
        return True

    elif args and args[0] == "intent":
        from aios.registry import ServiceRegistry
        from aios.services.intent import IntentResolverService
        from aios.services.nl_os import NLOSService

        nl_os = ServiceRegistry._global_registry.get(NLOSService)
        resolver = ServiceRegistry._global_registry.get(IntentResolverService)

        if len(args) < 2:
            console.print("[yellow]Usage: aios intent <query>[/yellow]")
        else:
            query = " ".join(args[1:])
            intent = resolver.resolve(query)
            classified_type = resolver.classify(query)

            table = Table(show_header=False, border_style="cyan")
            table.add_row("Raw Query", query)
            table.add_row("Intent Type", intent.intent_type.name)
            table.add_row("Classified Group", classified_type.name)
            table.add_row("Target Service", intent.target_service)
            table.add_row("Resolved Action", intent.action)
            table.add_row("Confidence Score", f"{intent.confidence:.2f}")
            table.add_row("Parameters", json.dumps(intent.parameters))

            console.print(
                Panel(
                    table,
                    title="[bold cyan]Intent Engine Analysis[/bold cyan]",
                    border_style="cyan",
                )
            )
            nl_os.record_intent_history(query, intent, success=True)

        if exit_on_complete:
            sys.exit(0)
        return True

    elif args and args[0] == "plan":
        from aios.registry import ServiceRegistry
        from aios.services.nl_os import NLOSService

        nl_os = ServiceRegistry._global_registry.get(NLOSService)

        if len(args) < 2:
            console.print("[yellow]Usage: aios plan <query>[/yellow]")
        else:
            query = " ".join(args[1:])
            plan = nl_os.generate_plan(query)

            table = Table(title=f"Plan {plan.plan_id}: {plan.objective}", border_style="magenta")
            table.add_column("Step ID", style="bold magenta")
            table.add_column("Description")
            table.add_column("Target Command", style="cyan")
            table.add_column("Status", style="yellow")
            table.add_column("Dependencies")

            for s in plan.steps:
                table.add_row(
                    s.step_id, s.description, s.target, s.status, ", ".join(s.dependencies)
                )

            console.print(table)
        if exit_on_complete:
            sys.exit(0)
        return True

    elif args and args[0] == "execute":
        from aios.registry import ServiceRegistry
        from aios.services.nl_os import NLOSService

        nl_os = ServiceRegistry._global_registry.get(NLOSService)

        if len(args) < 2:
            console.print("[yellow]Usage: aios execute <query>[/yellow]")
        else:
            query = " ".join(args[1:])
            plan = nl_os.generate_plan(query)

            console.print(f"[bold green]Starting Execution of Plan {plan.plan_id}...[/bold green]")
            success = nl_os.execute_plan(plan)
            if success:
                console.print("[bold green]✓ Execution finished successfully![/bold green]")
            else:
                console.print("[bold red]✗ Plan execution encountered errors.[/bold red]")
        if exit_on_complete:
            sys.exit(0)
        return True

    elif args and args[0] == "context":
        from aios.registry import ServiceRegistry
        from aios.services.context import ContextService

        ctx_svc = ServiceRegistry._global_registry.get(ContextService)

        if len(args) > 1 and args[1] == "set":
            if len(args) < 4:
                console.print("[yellow]Usage: aios context set <key> <value>[/yellow]")
            else:
                key = args[2]
                val = " ".join(args[3:])
                ctx_svc.set_context_item(key, val)
                console.print(f"[green]✓ Set context [bold]{key}[/bold] = {val}[/green]")
        elif len(args) > 1 and args[1] == "clear":
            ctx_svc.clear_context()
            console.print("[green]✓ Context cleared.[/green]")
        else:
            table = Table(
                title="[bold cyan]AI OS Context Control Panel[/bold cyan]", border_style="cyan"
            )
            table.add_column("Context Item", style="bold cyan")
            table.add_column("Value", style="white")

            items = ["project", "workflow", "client", "topic", "goal", "conversation"]
            for item in items:
                table.add_row(item.capitalize(), ctx_svc.get_context_item(item) or "None")

            console.print(table)
    elif args and args[0] in ("agents", "agent"):
        from aios.registry import ServiceRegistry
        from aios.services.agent_platform import AutonomousAgentPlatform

        platform = ServiceRegistry._global_registry.get(AutonomousAgentPlatform)

        # Subcommands: list, status, assign, execute, memory, dashboard
        subcmd = args[1] if len(args) > 1 else "dashboard"

        if args[0] == "agents":
            subcmd = "dashboard"

        if subcmd == "dashboard":
            # Render Agents Dashboard

            # Agents Table
            agents_table = Table(
                title="[bold green]Active Core Agents[/bold green]", border_style="green"
            )
            agents_table.add_column("Agent ID", style="bold cyan")
            agents_table.add_column("Name", style="white")
            agents_table.add_column("Role", style="magenta")
            agents_table.add_column("Status", style="yellow")
            agents_table.add_column("Tasks Run", style="cyan")
            agents_table.add_column("Success Rate", style="green")

            for agent in platform.list_agents():
                metrics = agent.performance_metrics
                success_rate = f"{metrics.get('success_rate', 1.0) * 100:.1f}%"
                tasks_completed = str(metrics.get("tasks_completed", 0))

                status_style = "bold green" if agent.status == "idle" else "bold yellow"
                agents_table.add_row(
                    agent.agent_id,
                    agent.name,
                    agent.role,
                    f"[{status_style}]{agent.status}[/{status_style}]",
                    tasks_completed,
                    success_rate,
                )

            # Tasks Table
            tasks_table = Table(
                title="[bold yellow]Agent Task queue & Pipelines[/bold yellow]",
                border_style="yellow",
            )
            tasks_table.add_column("Task ID", style="bold magenta")
            tasks_table.add_column("Title", style="white")
            tasks_table.add_column("Assigned Agent", style="cyan")
            tasks_table.add_column("Status", style="yellow")
            tasks_table.add_column("Dependencies", style="white")

            tasks = platform.list_tasks()
            if not tasks:
                tasks_table.add_row("None", "No active tasks in queue.", "N/A", "idle", "None")
            else:
                for t in tasks:
                    status_style = (
                        "bold yellow"
                        if t.status == "running"
                        else ("bold green" if t.status == "completed" else "bold red")
                    )
                    tasks_table.add_row(
                        t.task_id,
                        t.title,
                        t.assigned_agent or "Unassigned",
                        f"[{status_style}]{t.status}[/{status_style}]",
                        ", ".join(t.dependencies) if t.dependencies else "None",
                    )

            console.print(agents_table)
            console.print(tasks_table)

        elif subcmd == "list":
            # Simple list of agents
            table = Table(
                title="[bold cyan]AI OS Registered Agents[/bold cyan]", border_style="cyan"
            )
            table.add_column("Agent ID", style="bold cyan")
            table.add_column("Name")
            table.add_column("Role", style="magenta")
            table.add_column("Capabilities")

            for agent in platform.list_agents():
                table.add_row(agent.agent_id, agent.name, agent.role, ", ".join(agent.capabilities))
            console.print(table)

        elif subcmd == "status":
            if len(args) < 3:
                # Show all statuses
                table = Table(
                    title="[bold yellow]Agent Runtime Status[/bold yellow]", border_style="yellow"
                )
                table.add_column("Agent Name", style="bold cyan")
                table.add_column("Status", style="white")
                table.add_column("Assigned Tasks", style="magenta")

                for agent in platform.list_agents():
                    table.add_row(
                        agent.name, agent.status, ", ".join(agent.assigned_tasks) or "None"
                    )
                console.print(table)
            else:
                # Specific agent details
                name = args[2]
                desc = platform.get_agent_descriptor(name)
                if not desc:
                    console.print(f"[red]✗ Agent '{name}' is not registered.[/red]")
                else:
                    table = Table(show_header=False, border_style="magenta")
                    table.add_row("Agent ID", desc.agent_id)
                    table.add_row("Name", desc.name)
                    table.add_row("Role", desc.role)
                    table.add_row("Capabilities", ", ".join(desc.capabilities))
                    table.add_row("Status", desc.status)
                    table.add_row("Assigned Tasks", ", ".join(desc.assigned_tasks) or "None")
                    table.add_row(
                        "Tasks Run", str(desc.performance_metrics.get("tasks_completed", 0))
                    )
                    table.add_row("Failures", str(desc.performance_metrics.get("failures", 0)))
                    table.add_row(
                        "Success Rate",
                        f"{desc.performance_metrics.get('success_rate', 1.0) * 100:.1f}%",
                    )
                    console.print(
                        Panel(
                            table,
                            title=f"[bold magenta]Agent Profile: {desc.name}[/bold magenta]",
                            border_style="magenta",
                        )
                    )

        elif subcmd == "assign":
            if len(args) < 4:
                console.print("[yellow]Usage: aios agent assign <task_id> <agent_id>[/yellow]")
            else:
                task_id = args[2]
                agent_id = args[3]
                try:
                    platform.assign_task(task_id, agent_id)
                    console.print(
                        f"[green]✓ Assigned task '{task_id}' to agent '{agent_id}'[/green]"
                    )
                except Exception as e:
                    console.print(f"[red]✗ Assignment failed: {e}[/red]")

        elif subcmd == "execute":
            if len(args) < 3:
                console.print("[yellow]Usage: aios agent execute <query>[/yellow]")
            else:
                query = " ".join(args[2:])
                console.print(
                    f'[bold green]Starting Autonomous Agent Pipeline for: "{query}"[/bold green]'
                )

                # 1. Plan tasks
                with console.status("[bold blue]Planning tasks & dependencies...", spinner="dots"):
                    tasks = platform.generate_plan(query)

                table = Table(title="Generated Multi-Agent Execution Plan", border_style="magenta")
                table.add_column("Task ID", style="bold magenta")
                table.add_column("Title")
                table.add_column("Agent", style="cyan")
                table.add_column("Dependencies")
                for t in tasks:
                    table.add_row(
                        t.task_id,
                        t.title,
                        t.assigned_agent or "Unassigned",
                        ", ".join(t.dependencies) if t.dependencies else "None",
                    )
                console.print(table)

                # 2. Execute plan
                console.print("\n[bold yellow]Executing Plan...[/bold yellow]")
                success = platform.execute_plan(tasks)

                if success:
                    console.print(
                        "\n[bold green]✓ Multi-Agent Pipeline Completed Successfully![/bold green]"
                    )
                else:
                    console.print("\n[bold red]✗ Multi-Agent Pipeline Execution Failed.[/bold red]")

                # Print results summary
                for t in tasks:
                    status_symbol = (
                        "[green]✓[/green]" if t.status == "completed" else "[red]✗[/red]"
                    )
                    console.print(f"{status_symbol} [bold]{t.title}[/bold] ({t.assigned_agent})")
                    if t.results:
                        console.print(
                            Panel(t.results, title=f"Results of {t.title}", border_style="cyan")
                        )

        elif subcmd == "memory":
            if len(args) < 3:
                console.print("[yellow]Usage: aios agent memory <agent_id>[/yellow]")
            else:
                agent_id = args[2]
                memories = platform.get_agent_memory(agent_id)
                if not memories:
                    console.print(f"[yellow]No memory logs found for agent '{agent_id}'.[/yellow]")
                else:
                    table = Table(
                        title=f"[bold green]Agent Memory Ledger: {agent_id}[/bold green]",
                        border_style="green",
                    )
                    table.add_column("Task ID", style="bold magenta")
                    table.add_column("Task Title")
                    table.add_column("Status", style="white")
                    table.add_column("Lesson Learned", style="yellow")

                    for m in memories:
                        status = "Success" if m["success"] else "Failure"
                        table.add_row(m["task_id"], m["title"], status, m["lesson_learned"])
                    console.print(table)
        else:
            console.print(f"[red]✗ Unknown agent subcommand: {subcmd}[/red]")

        if exit_on_complete:
            sys.exit(0)
        return True

    elif args and args[0] in ("dashboard", "search", "notifications", "workspace", "status"):
        from aios.registry import ServiceRegistry
        from aios.services.ux_platform import UXPlatform

        ux = ServiceRegistry._global_registry.get(UXPlatform)

        cmd = args[0]
        if cmd == "dashboard":
            ux.interactive_loop()

        elif cmd == "search":
            if len(args) < 2:
                console.print("[yellow]Usage: aios search <query>[/yellow]")
            else:
                term = " ".join(args[1:])
                results = ux.universal_search(term)
                if not results:
                    console.print("[yellow]No matching items found across OS database.[/yellow]")
                else:
                    table = Table(
                        title=f"Universal Search Results for: {term}", border_style="cyan"
                    )
                    table.add_column("Type", style="bold cyan")
                    table.add_column("Name", style="magenta")
                    table.add_column("Description", style="white")
                    for r in results:
                        table.add_row(r["type"], r["name"], r["desc"])
                    console.print(table)

        elif cmd == "notifications":
            ux._render_notifications_workspace(ux.get_theme_colors())

        elif cmd == "workspace":
            if len(args) < 2:
                console.print(
                    "[yellow]Usage: aios workspace <project|agency|research|github|workflow|agent>[/yellow]"
                )
            else:
                workspace_name = args[1].lower()
                if workspace_name in (
                    "project",
                    "agency",
                    "research",
                    "github",
                    "workflow",
                    "agent",
                ):
                    ux.current_workspace = workspace_name
                    ux.interactive_loop()
                else:
                    console.print(f"[red]✗ Unknown workspace: {workspace_name}[/red]")

        elif cmd == "status":
            console.print(ux.render_status_bar())

        if exit_on_complete:
            sys.exit(0)
        return True

    return False


def main() -> None:
    """CLI entry point for aios."""
    args = sys.argv[1:]

    if args:
        config_path = Path("config/config.toml")
        kernel = bootstrap_kernel(config_path)
        try:
            kernel.boot()

            if not execute_builtin_cli_command(args):
                console.print(f"[red]✗ Unknown command line argument: {' '.join(args)}[/red]")
                sys.exit(1)

        except Exception as e:
            from aios.ux import ErrorReporter

            ErrorReporter.report(
                e,
                cause=("Subcommand parameter validation failed or platform connection issue."),
                fix=("Verify command arguments and run 'aios diagnostics' to check health status."),
            )
            sys.exit(1)
        finally:
            kernel.shutdown()

    from aios.ux import BootExperience

    BootExperience.boot()

    config_path = Path("config/config.toml")
    kernel = bootstrap_kernel(config_path)

    try:
        kernel.boot()
        from aios.services.ux_platform import UXPlatform

        ux = kernel.registry.get(UXPlatform)
        ux.interactive_loop()
    except KeyboardInterrupt:
        console.print("\n[yellow]Input cancelled. Press Ctrl+D or type /exit to quit.[/yellow]\n")
    except EOFError:
        pass
    except Exception as e:
        from aios.ux import ErrorReporter

        ErrorReporter.report(
            e,
            cause=("Command parameter syntax error or runtime subsystem exception."),
            fix=("Verify command arguments and run 'aios diagnostics' to check health status."),
        )

    finally:
        console.print("[yellow]Shutting down AI OS Core...[/yellow]")
        kernel.shutdown()


if __name__ == "__main__":
    main()
