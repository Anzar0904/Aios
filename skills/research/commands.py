import sys
from aios.services.command.metadata import CommandCategory, CommandMetadata
from aios.services.research import ResearchService


def execute_research_topic(args: str, kernel, conv_manager) -> None:
    topic = args.strip()
    if not topic:
        print("Usage: research topic <topic>")
        return

    try:
        research_svc = kernel.registry.get(ResearchService)
        result = research_svc.research(topic)
        print(result.report)
    except Exception as e:
        print(f"Research failed: {str(e)}")


def execute_search_web(args: str, kernel, conv_manager) -> None:
    query = args.strip()
    if not query:
        print("Usage: search web <query>")
        return

    try:
        research_svc = kernel.registry.get(ResearchService)
        result = research_svc.research(query)
        print("\n=== Search Results ===")
        for idx, s in enumerate(result.sources, 1):
            print(f"[{idx}] {s.title} ({s.url})")
            print(f"    Snippet: {s.snippet}\n")
    except Exception as e:
        print(f"Search failed: {str(e)}")


def execute_generate_research_report(args: str, kernel, conv_manager) -> None:
    topic = args.strip()
    if not topic:
        print("Usage: generate research report <topic>")
        return

    try:
        research_svc = kernel.registry.get(ResearchService)
        result = research_svc.research(topic)
        print(f"Generating research report for topic: '{topic}'...")
        print(result.report)
    except Exception as e:
        print(f"Report generation failed: {str(e)}")


def register_commands(registry, kernel, conv_manager) -> None:
    # 1. research topic
    registry.register_command(
        CommandMetadata(
            name="research topic",
            description="Performs technical research on a topic and returns a cited markdown report.",
            category=CommandCategory.CLI,
            required_agent="None",
            required_tools=[],
            example_usage="research topic LocalEventBus versus NATS",
        ),
        lambda args: execute_research_topic(args, kernel, conv_manager),
    )

    # 2. search web
    registry.register_command(
        CommandMetadata(
            name="search web",
            description="Searches the web/local repositories for snippets related to the query.",
            category=CommandCategory.CLI,
            required_agent="None",
            required_tools=[],
            example_usage="search web python git libraries",
        ),
        lambda args: execute_search_web(args, kernel, conv_manager),
    )

    # 3. generate research report
    registry.register_command(
        CommandMetadata(
            name="generate research report",
            description="Generates a technical research report based on gathered source snippets.",
            category=CommandCategory.CLI,
            required_agent="None",
            required_tools=[],
            example_usage="generate research report sandboxing in macOS",
        ),
        lambda args: execute_generate_research_report(args, kernel, conv_manager),
    )
