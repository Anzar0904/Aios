from aios.services.command.discovery import match_command
from aios.services.command.doc_gen import DocumentationGenerator
from aios.services.command.metadata import CommandCategory, CommandMetadata
from aios.services.command.registry import CommandRegistry


def test_command_registration_and_matching():
    registry = CommandRegistry()

    # 1. Register test command
    meta = CommandMetadata(
        name="test command",
        description="A test command",
        category=CommandCategory.SYSTEM,
        required_agent="mock_agent",
        required_tools=[],
        example_usage="test command args",
    )

    called_args = []

    def handler(args):
        called_args.append(args)

    registry.register_command(meta, handler)

    # 2. Check get_command
    assert registry.get_command("test command") == meta
    assert registry.get_command("TEST COMMAND") == meta

    # 3. Test matching
    res = match_command("test command hello world", registry)
    assert res is not None
    cmd, args = res
    assert cmd == meta
    assert args == "hello world"

    # Run handler
    handler_fn = registry.get_handler(cmd.name)
    handler_fn(args)
    assert called_args == ["hello world"]


def test_command_search_and_list():
    registry = CommandRegistry()

    c1 = CommandMetadata("git review", "desc", CommandCategory.DEVELOPER, "agent", [], "usage")
    c2 = CommandMetadata("ats score", "desc", CommandCategory.CAREER, "agent", [], "usage")

    registry.register_command(c1, lambda x: None)
    registry.register_command(c2, lambda x: None)

    # List by category
    dev_cmds = registry.list_commands(CommandCategory.DEVELOPER)
    assert len(dev_cmds) == 1
    assert dev_cmds[0].name == "git review"

    # Search
    results = registry.search_commands("review")
    assert len(results) == 1
    assert results[0].name == "git review"


def test_documentation_generation(tmp_path):
    registry = CommandRegistry()
    c1 = CommandMetadata(
        "git review",
        "review changes",
        CommandCategory.DEVELOPER,
        "agent",
        ["git"],
        "git review",
    )
    registry.register_command(c1, lambda x: None)

    doc_gen = DocumentationGenerator(registry)
    output_file = tmp_path / "COMMANDS.md"
    doc_gen.generate_markdown(output_file)

    content = output_file.read_text(encoding="utf-8")
    assert "# Personal AI OS Command Reference" in content
    assert "git review" in content
    assert "review changes" in content
