import tempfile
from pathlib import Path
from unittest.mock import MagicMock

from aios.services.command import CommandRegistry
from aios.skills.manager import SkillManager
from aios.skills.metadata import SkillMetadata
from aios.skills.registry import SkillRegistry


def test_skill_metadata():
    meta = SkillMetadata(
        id="test_skill",
        name="Test Skill",
        version="1.0.0",
        author="Tester",
        description="A test skill",
        category="Test",
        commands=["test_command"],
    )
    assert meta.id == "test_skill"
    assert meta.commands == ["test_command"]
    assert meta.enabled is True


def test_skill_registry_and_manager():
    with tempfile.TemporaryDirectory() as tmpdir:
        skills_dir = Path(tmpdir)

        skill_path = skills_dir / "test_skill"
        skill_path.mkdir()

        toml_content = """
[skill]
id = "test_skill"
name = "Test Skill"
version = "1.0.0"
author = "Tester"
description = "A test skill"
category = "Test"
commands = ["test_command"]
"""
        (skill_path / "skill.toml").write_text(toml_content, encoding="utf-8")

        commands_py = """
from aios.services.command.metadata import CommandMetadata, CommandCategory

def register_commands(registry, kernel, conv_manager):
    registry.register_command(
        CommandMetadata(
            name="test_command",
            description="A test command",
            category=CommandCategory.CLI,
            required_agent="None",
            required_tools=[],
            example_usage="test_command"
        ),
        lambda args: print("Hello from test command")
    )
"""
        (skill_path / "commands.py").write_text(commands_py, encoding="utf-8")

        registry = SkillRegistry()
        manager = SkillManager(skills_dir, registry)

        manager.load_all_skills()

        loaded = registry.get_skill("test_skill")
        assert loaded is not None
        assert loaded.metadata.id == "test_skill"
        assert loaded.metadata.version == "1.0.0"

        cmd_registry = CommandRegistry()
        kernel = MagicMock()
        conv_manager = MagicMock()

        manager.register_all_commands(cmd_registry, kernel, conv_manager)
        assert cmd_registry.get_command("test_command") is not None

        manager.disable_skill("test_skill", cmd_registry)
        assert loaded.enabled is False
        assert cmd_registry.get_command("test_command") is None

        manager.enable_skill("test_skill", cmd_registry, kernel, conv_manager)
        assert loaded.enabled is True
        assert cmd_registry.get_command("test_command") is not None

        manager.reload_skill("test_skill", cmd_registry, kernel, conv_manager)
        assert cmd_registry.get_command("test_command") is not None

        manager.uninstall_skill("test_skill", cmd_registry)
        assert registry.get_skill("test_skill") is None
        assert cmd_registry.get_command("test_command") is None
