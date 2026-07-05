from aios.services.command.metadata import CommandCategory, CommandMetadata
from aios.services.intent import IntentType
from aios.services.command.discovery import execute_agent_intent

def register_commands(registry, kernel, conv_manager) -> None:
    registry.register_command(
        CommandMetadata(
            name="remember",
            description="Adds a fact or note to persistent workspace memory.",
            category=CommandCategory.MEMORY,
            required_agent="mock_agent",
            required_tools=[],
            example_usage="remember this project is built in python",
        ),
        lambda args: execute_agent_intent(
            kernel,
            IntentType.MEMORY,
            "Add",
            {"content": args.strip() if args else "Remembered note"},
        ),
    )
