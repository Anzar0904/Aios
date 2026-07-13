from aios.services.command.discovery import (
    handle_current_conversation,
    handle_delete_conversation,
    handle_list_conversations,
    handle_new_conversation,
    handle_rename_conversation,
    handle_resume_conversation,
    handle_show_history,
)
from aios.services.command.metadata import CommandCategory, CommandMetadata


def register_commands(registry, kernel, conv_manager) -> None:
    registry.register_command(
        CommandMetadata(
            name="new conversation",
            description="Creates and switches to a new conversation.",
            category=CommandCategory.CONVERSATION,
            required_agent="None",
            required_tools=[],
            example_usage="new conversation",
        ),
        lambda args: handle_new_conversation(conv_manager, args),
    )

    registry.register_command(
        CommandMetadata(
            name="list conversations",
            description="Lists all persisted conversations.",
            category=CommandCategory.CONVERSATION,
            required_agent="None",
            required_tools=[],
            example_usage="list conversations",
        ),
        lambda args: handle_list_conversations(conv_manager),
    )

    registry.register_command(
        CommandMetadata(
            name="resume conversation",
            description="Resumes a specific conversation.",
            category=CommandCategory.CONVERSATION,
            required_agent="None",
            required_tools=[],
            example_usage="resume conversation <id>",
        ),
        lambda args: handle_resume_conversation(conv_manager, args),
    )

    registry.register_command(
        CommandMetadata(
            name="resume",
            description="Resumes a specific conversation.",
            category=CommandCategory.CONVERSATION,
            required_agent="None",
            required_tools=[],
            example_usage="resume <id>",
        ),
        lambda args: handle_resume_conversation(conv_manager, args),
    )

    registry.register_command(
        CommandMetadata(
            name="rename conversation",
            description="Renames the active conversation.",
            category=CommandCategory.CONVERSATION,
            required_agent="None",
            required_tools=[],
            example_usage="rename conversation",
        ),
        lambda args: handle_rename_conversation(conv_manager),
    )

    registry.register_command(
        CommandMetadata(
            name="delete conversation",
            description="Deletes a conversation.",
            category=CommandCategory.CONVERSATION,
            required_agent="None",
            required_tools=[],
            example_usage="delete conversation",
        ),
        lambda args: handle_delete_conversation(conv_manager, args),
    )

    registry.register_command(
        CommandMetadata(
            name="current conversation",
            description="Displays active conversation metadata.",
            category=CommandCategory.CONVERSATION,
            required_agent="None",
            required_tools=[],
            example_usage="current conversation",
        ),
        lambda args: handle_current_conversation(conv_manager),
    )

    registry.register_command(
        CommandMetadata(
            name="show history",
            description="Shows the history and summary of the active conversation.",
            category=CommandCategory.CONVERSATION,
            required_agent="None",
            required_tools=[],
            example_usage="show history",
        ),
        lambda args: handle_show_history(conv_manager),
    )
