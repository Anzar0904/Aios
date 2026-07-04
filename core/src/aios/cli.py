import atexit
import contextlib
import io
import readline
import signal
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.markdown import Markdown

from aios.bootstrap import bootstrap_kernel
from aios.services.conversation.manager import ConversationManager
from aios.services.conversation.store import ConversationStore
from aios.services.intent import IntentResolverService, IntentType
from aios.services.model import LLMRequest, ModelService
from aios.skills.registry import SkillRegistry
from aios.skills.manager import SkillManager
from aios.services.command import (
    CommandRegistry,
    DocumentationGenerator,
    match_command,
    register_default_commands,
)

# Global Console instance for Terminal UX styling
console = Console()


def handle_conversation_command(user_input: str, conv_manager: ConversationManager) -> bool:
    cmd = user_input.lower().strip()

    if cmd == "new conversation":
        title = input("Enter conversation title (optional): ").strip()
        title = title if title else None
        conv = conv_manager.create_conversation(title=title, agent_name="developer_agent")
        console.print(f"[green]✓ Created and switched to conversation: '{conv.title}' ({conv.id})[/green]")
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
                table.add_row(
                    active_marker,
                    c["id"],
                    c["title"],
                    c["active_agent"] or "None"
                )
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
            confirm = input(f"Are you sure you want to delete conversation '{found_id}'? (y/n): ").strip().lower()
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

            console.print(Panel(grid, title="[bold white]Active Conversation Details[/bold white]", border_style="cyan"))
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
    table.add_row("/conversation resume <id>", "Switch active conversation", "/conversation resume target-id")
    table.add_row("/conversation delete", "Delete conversation history from disk", "/conversation delete")
    table.add_row("/conversation rename", "Rename current dialogue session", "/conversation rename my-session")
    table.add_row("/conversation active", "Show current conversation summary", "/conversation active")
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
            cmds_str += f" (+{len(skill.metadata.commands)-3} more)"
        table.add_row(
            skill.metadata.id,
            skill.metadata.name,
            skill.metadata.description,
            caps_str,
            cmds_str
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
        table.add_row(
            prov_name,
            ", ".join(models),
            "Active / Healthy"
        )
    console.print(table)


def handle_model_switch(model_service: ModelService, model_name: str) -> None:
    model_name = model_name.strip()
    if not model_name:
        console.print("[yellow]Usage: /model <model_name>[/yellow]")
        return
    try:
        provider = model_service.registry.get_provider_for_model(model_name)
        model_service._default_model = model_name
        console.print(f"[green]✓ Switched default model to: [bold]{model_name}[/bold] (Provider: {provider})[/green]")
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
            console.print(Panel(m.content, title="[bold green]User[/bold green]", border_style="green", expand=False))
        elif role == "ASSISTANT":
            console.print(Panel(Markdown(m.content), title="[bold blue]Assistant[/bold blue]", border_style="blue", expand=False))
        else:
            console.print(Panel(m.content, title=f"[bold gray]{role}[/bold gray]", border_style="gray", expand=False))


def print_status_line(model_service: ModelService, conv_manager: ConversationManager) -> None:
    model_name = getattr(model_service, "_default_model", "claude-3-5-sonnet")
    conv = conv_manager.get_current_conversation()
    conv_title = conv.title if conv else "None"
    status_str = f"Model: [bold cyan]{model_name}[/bold cyan] | Conv: [bold green]{conv_title}[/bold green] | Mode: [bold yellow]Interactive[/bold yellow]"
    console.print(f"[dim]{status_str}[/dim]")


def read_input(multiline_mode: bool = False) -> str:
    """Reads input from the user, supporting multi-line formatting."""
    if multiline_mode:
        console.print("[dim]Enter multi-line input (type '.' or press Ctrl+D on a new line to submit):[/dim]")
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


def handle_general_chat(user_input: str, conv_manager: ConversationManager, model_service: ModelService) -> None:
    conv = conv_manager.get_current_conversation()
    if not conv:
        conv = conv_manager.create_conversation(title="Active Dialogue", agent_name="developer_agent")

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
    req = LLMRequest(
        prompt=prompt,
        system_instruction=system_instruction,
        model_name=model_name
    )

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
        console.print(Panel(f"Error during streaming execution: {str(e)}", border_style="red", title="Stream Error"))
        return

    conv_manager.add_message(conv.id, "assistant", full_response)

    p_tokens = token_usage.get("prompt_tokens", 0)
    c_tokens = token_usage.get("completion_tokens", 0)
    total_tokens = token_usage.get("total_tokens", p_tokens + c_tokens)

    console.print(
        f"[dim]Model: {model_name} | Tokens: In={p_tokens}, Out={c_tokens}, Total={total_tokens}[/dim]\n"
    )


def main() -> None:
    """CLI entry point for aios."""
    console.print("[cyan]Initializing AI OS Core...[/cyan]")

    config_path = Path("config/config.toml")
    kernel = bootstrap_kernel(config_path)

    try:
        kernel.boot()

        from aios.services.context import ContextService
        context_service = kernel.registry.get(ContextService)
        context = context_service.get_current_context()
        workspace_root = context.project_root if context else str(Path.cwd().resolve())

        conv_store = ConversationStore(Path(workspace_root) / ".aios_conversations")
        conv_manager = ConversationManager(conv_store)

        registry = kernel.registry.get(CommandRegistry)
        register_default_commands(registry, kernel, conv_manager)

        # Generate documentation automatically
        doc_gen = DocumentationGenerator(registry)
        doc_gen.generate_markdown(Path(workspace_root) / "COMMANDS.md")

        # Set up readline command history file
        history_file = Path(workspace_root) / ".aios_history"
        if history_file.exists():
            try:
                readline.read_history_file(str(history_file))
            except Exception:
                pass
        readline.set_history_length(1000)
        atexit.register(lambda: readline.write_history_file(str(history_file)))

        # Initialize local SkillRegistry for command/capability tables
        skills_dir = Path(workspace_root) / "skills"
        skill_registry = SkillRegistry()
        skill_manager = SkillManager(skills_dir, skill_registry)
        skill_manager.load_all_skills()

        model_service = kernel.registry.get(ModelService)

        # Dynamic Startup Banner
        banner_text = Text()
        banner_text.append("\n █████╗ ██╗ ██████╗ ███████╗\n", style="bold cyan")
        banner_text.append("██╔══██╗██║██╔═══██╗██╔════╝\n", style="bold cyan")
        banner_text.append("███████║██║██║   ██║███████╗\n", style="bold blue")
        banner_text.append("██╔══██║██║██║   ██║╚════██║\n", style="bold blue")
        banner_text.append("██║  ██║██║╚██████╔╝███████║\n", style="bold purple")
        banner_text.append("╚═╝  ╚═╝╚═╝ ╚═════╝ ╚══════╝\n", style="bold purple")

        status_table = Table.grid(padding=1)
        status_table.add_column(style="bold white", justify="right")
        status_table.add_column(style="green")
        status_table.add_row("Platform:", sys.platform)
        status_table.add_row("Workspace:", str(workspace_root))
        status_table.add_row("Active Agent:", "developer_agent")
        status_table.add_row("Model Service:", "Online")
        status_table.add_row("Default Model:", getattr(model_service, "_default_model", "claude-3-5-sonnet"))

        panel = Panel(
            status_table,
            title="[bold white]Personal AI OS CLI Terminal[/bold white]",
            subtitle="[italic gray]Type /help or /? for options[/italic gray]",
            border_style="cyan"
        )
        console.print(banner_text)
        console.print(panel)

        multiline_mode = False

        # Global Signal handler for SIGINT/SIGTERM
        def handle_shutdown(signum, frame):
            console.print("\n[yellow]Shutting down gracefully...[/yellow]")
            kernel.shutdown()
            sys.exit(0)

        signal.signal(signal.SIGINT, handle_shutdown)
        signal.signal(signal.SIGTERM, handle_shutdown)

        while True:
            try:
                print_status_line(model_service, conv_manager)
                user_input = read_input(multiline_mode).strip()
                if not user_input:
                    continue

                # Handle Slash Commands
                if user_input.startswith("/"):
                    parts = user_input.split(maxsplit=1)
                    slash_cmd = parts[0].lower()
                    slash_args = parts[1] if len(parts) > 1 else ""

                    if slash_cmd in ("/help", "/?"):
                        print_help_table(registry)
                    elif slash_cmd == "/conversation":
                        subcmd = slash_args.strip().lower()
                        if subcmd in ("list", "ls"):
                            handle_conversation_command("list conversations", conv_manager)
                        elif subcmd.startswith("new"):
                            handle_conversation_command("new conversation", conv_manager)
                        elif subcmd.startswith("resume"):
                            target = slash_args[6:].strip()
                            handle_conversation_command(f"resume {target}", conv_manager)
                        elif subcmd == "delete":
                            handle_conversation_command("delete conversation", conv_manager)
                        elif subcmd == "rename":
                            handle_conversation_command("rename conversation", conv_manager)
                        elif subcmd == "active":
                            handle_conversation_command("current conversation", conv_manager)
                        else:
                            console.print("[yellow]Subcommands: list, new, resume, delete, rename, active[/yellow]")
                    elif slash_cmd == "/skills":
                        print_skills_table(skill_registry)
                    elif slash_cmd == "/providers":
                        print_providers_table(model_service)
                    elif slash_cmd == "/model":
                        handle_model_switch(model_service, slash_args)
                    elif slash_cmd == "/history":
                        print_conversation_history(conv_manager)
                    elif slash_cmd == "/clear":
                        console.clear()
                    elif slash_cmd == "/multiline":
                        multiline_mode = not multiline_mode
                        console.print(f"[green]✓ Multiline mode: {'ENABLED' if multiline_mode else 'DISABLED'}[/green]")
                    elif slash_cmd in ("/exit", "/quit"):
                        break
                    else:
                        console.print(f"[red]✗ Unknown slash command: {slash_cmd}. Type /help for options.[/red]")
                    continue

                # Handle Skill Commands
                matched = match_command(user_input, registry)
                if matched:
                    cmd_metadata, args = matched
                    handler = registry.get_handler(cmd_metadata.name)
                    with console.status(f"[bold green]Executing command '{cmd_metadata.name}'...", spinner="dots"):
                        handler(args)
                    continue

                # Handle General Intent or Direct Chat Routing
                intent_resolver = kernel.registry.get(IntentResolverService)
                with console.status("[bold blue]Resolving Intent...", spinner="dots"):
                    intent = intent_resolver.resolve(user_input)
                    intent.parameters["raw_query"] = user_input

                if intent.intent_type == IntentType.UNKNOWN:
                    # Fallback to direct model conversation with streaming
                    handle_general_chat(user_input, conv_manager, model_service)
                else:
                    console.print(
                        f"[dim]Resolved Intent: {intent.intent_type.name}.{intent.action} "
                        f"(Confidence: {intent.confidence:.2f})[/dim]"
                    )
                    with console.status("[bold blue]Running reasoning pipeline...", spinner="dots"):
                        result = kernel.execute_intent(intent)
                    console.print(Panel(Markdown(result.message), border_style="blue", title="System Response"))

            except KeyboardInterrupt:
                console.print("\n[yellow]Input cancelled. Press Ctrl+D or type /exit to quit.[/yellow]\n")
            except EOFError:
                break
            except Exception as e:
                console.print(Panel(f"Execution failed: {str(e)}", border_style="red", title="Runtime Exception"))

    finally:
        console.print("[yellow]Shutting down AI OS Core...[/yellow]")
        kernel.shutdown()


if __name__ == "__main__":
    main()
