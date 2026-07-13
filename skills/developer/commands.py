from aios.services.command.discovery import execute_agent_intent
from aios.services.command.metadata import CommandCategory, CommandMetadata
from aios.services.intent import IntentType


def register_commands(registry, kernel, conv_manager) -> None:
    registry.register_command(
        CommandMetadata(
            name="analyze repository",
            description=(
                "Performs a detailed workspace analysis, detecting "
                "languages, frameworks, and architecture."
            ),
            category=CommandCategory.DEVELOPER,
            required_agent="developer_agent",
            required_tools=["filesystem"],
            example_usage="analyze repository",
        ),
        lambda args: execute_agent_intent(
            kernel, IntentType.DEVELOPER, "AnalyzeRepository", {}
        ),
    )

    registry.register_command(
        CommandMetadata(
            name="explain file",
            description="Explains the purpose, key classes, and structure of a specific file.",
            category=CommandCategory.DEVELOPER,
            required_agent="developer_agent",
            required_tools=["filesystem"],
            example_usage="explain file core/src/aios/kernel.py",
        ),
        lambda args: execute_agent_intent(
            kernel,
            IntentType.DEVELOPER,
            "ExplainFile",
            {"path": args.strip() if args else "core/src/aios/kernel.py"},
        ),
    )

    registry.register_command(
        CommandMetadata(
            name="summarize architecture",
            description="Generates a high-level summary of the system architecture.",
            category=CommandCategory.DEVELOPER,
            required_agent="developer_agent",
            required_tools=["filesystem"],
            example_usage="summarize architecture",
        ),
        lambda args: execute_agent_intent(
            kernel, IntentType.DEVELOPER, "SummarizeArchitecture", {}
        ),
    )

    registry.register_command(
        CommandMetadata(
            name="review repository",
            description=(
                "Performs a comprehensive code quality and structure review of the repository."
            ),
            category=CommandCategory.DEVELOPER,
            required_agent="developer_agent",
            required_tools=["filesystem"],
            example_usage="review repository",
        ),
        lambda args: execute_agent_intent(kernel, IntentType.DEVELOPER, "ReviewRepository", {}),
    )

    registry.register_command(
        CommandMetadata(
            name="review architecture",
            description=(
                "Reviews architectural patterns, separations of concerns, coupling, "
                "and SOLID compliance."
            ),
            category=CommandCategory.DEVELOPER,
            required_agent="developer_agent",
            required_tools=["filesystem"],
            example_usage="review architecture",
        ),
        lambda args: execute_agent_intent(kernel, IntentType.DEVELOPER, "ReviewArchitecture", {}),
    )

    registry.register_command(
        CommandMetadata(
            name="review security",
            description=(
                "Performs a security audit of the workspace identifying potential vulnerabilities."
            ),
            category=CommandCategory.DEVELOPER,
            required_agent="developer_agent",
            required_tools=["filesystem"],
            example_usage="review security",
        ),
        lambda args: execute_agent_intent(kernel, IntentType.DEVELOPER, "ReviewSecurity", {}),
    )

    registry.register_command(
        CommandMetadata(
            name="analyze dependencies",
            description=(
                "Analyzes package and build configurations to detect dependency bloat and risks."
            ),
            category=CommandCategory.DEVELOPER,
            required_agent="developer_agent",
            required_tools=["filesystem"],
            example_usage="analyze dependencies",
        ),
        lambda args: execute_agent_intent(
            kernel, IntentType.DEVELOPER, "AnalyzeDependencies", {}
        ),
    )

    registry.register_command(
        CommandMetadata(
            name="detect dead code",
            description="Scans files and imports to detect dead or obsolete code paths.",
            category=CommandCategory.DEVELOPER,
            required_agent="developer_agent",
            required_tools=["filesystem"],
            example_usage="detect dead code",
        ),
        lambda args: execute_agent_intent(kernel, IntentType.DEVELOPER, "DetectDeadCode", {}),
    )

    registry.register_command(
        CommandMetadata(
            name="analyze todos",
            description=(
                "Scans the workspace to aggregate, prioritize, and assess unresolved "
                "TODO/FIXME items."
            ),
            category=CommandCategory.DEVELOPER,
            required_agent="developer_agent",
            required_tools=["filesystem"],
            example_usage="analyze todos",
        ),
        lambda args: execute_agent_intent(kernel, IntentType.DEVELOPER, "AnalyzeTodos", {}),
    )

    registry.register_command(
        CommandMetadata(
            name="review tests",
            description="Reviews test infrastructure, unit test coverage, gaps, and quality.",
            category=CommandCategory.DEVELOPER,
            required_agent="developer_agent",
            required_tools=["filesystem"],
            example_usage="review tests",
        ),
        lambda args: execute_agent_intent(kernel, IntentType.DEVELOPER, "ReviewTests", {}),
    )

    registry.register_command(
        CommandMetadata(
            name="review git changes",
            description="Reviews active uncommitted git changes and provides insights.",
            category=CommandCategory.DEVELOPER,
            required_agent="developer_agent",
            required_tools=["git"],
            example_usage="review git changes",
        ),
        lambda args: execute_agent_intent(kernel, IntentType.DEVELOPER, "ReviewGitChanges", {}),
    )

    registry.register_command(
        CommandMetadata(
            name="generate release notes",
            description="Drafts release notes from recent git activities and commit summaries.",
            category=CommandCategory.DEVELOPER,
            required_agent="developer_agent",
            required_tools=["git"],
            example_usage="generate release notes",
        ),
        lambda args: execute_agent_intent(
            kernel, IntentType.DEVELOPER, "GenerateReleaseNotes", {}
        ),
    )

    registry.register_command(
        CommandMetadata(
            name="generate commit message",
            description="Generates a standard git commit message for the active changes.",
            category=CommandCategory.DEVELOPER,
            required_agent="developer_agent",
            required_tools=["git"],
            example_usage="generate commit message",
        ),
        lambda args: execute_agent_intent(
            kernel, IntentType.DEVELOPER, "GenerateCommitMessage", {}
        ),
    )

    registry.register_command(
        CommandMetadata(
            name="investigate bug",
            description=(
                "Investigates a bug report or error scenario, pinpointing potential origins."
            ),
            category=CommandCategory.DEVELOPER,
            required_agent="developer_agent",
            required_tools=["filesystem"],
            example_usage="investigate bug <description>",
        ),
        lambda args: execute_agent_intent(
            kernel,
            IntentType.DEVELOPER,
            "InvestigateBug",
            {"bug_description": args.strip() if args else ""},
        ),
    )

    registry.register_command(
        CommandMetadata(
            name="explain stack trace",
            description=(
                "Explains a system stack trace, pointing to exceptions and lines of failure."
            ),
            category=CommandCategory.DEVELOPER,
            required_agent="developer_agent",
            required_tools=["filesystem"],
            example_usage="explain stack trace <error trace>",
        ),
        lambda args: execute_agent_intent(
            kernel,
            IntentType.DEVELOPER,
            "ExplainStackTrace",
            {"stack_trace": args.strip() if args else ""},
        ),
    )

    registry.register_command(
        CommandMetadata(
            name="detect code smells",
            description=(
                "Scans the repository to identify code smells, long methods, "
                "or architectural anti-patterns."
            ),
            category=CommandCategory.DEVELOPER,
            required_agent="developer_agent",
            required_tools=["filesystem"],
            example_usage="detect code smells",
        ),
        lambda args: execute_agent_intent(kernel, IntentType.DEVELOPER, "DetectCodeSmells", {}),
    )

    registry.register_command(
        CommandMetadata(
            name="detect duplicate code",
            description="Finds redundant or duplicated blocks of code across workspace files.",
            category=CommandCategory.DEVELOPER,
            required_agent="developer_agent",
            required_tools=["filesystem"],
            example_usage="detect duplicate code",
        ),
        lambda args: execute_agent_intent(
            kernel, IntentType.DEVELOPER, "DetectDuplicateCode", {}
        ),
    )

    registry.register_command(
        CommandMetadata(
            name="suggest refactoring",
            description="Suggests structural refactoring blueprints to improve code design.",
            category=CommandCategory.DEVELOPER,
            required_agent="developer_agent",
            required_tools=["filesystem"],
            example_usage="suggest refactoring",
        ),
        lambda args: execute_agent_intent(kernel, IntentType.DEVELOPER, "SuggestRefactoring", {}),
    )
