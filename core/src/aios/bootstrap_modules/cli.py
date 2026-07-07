"""
bootstrap_modules/cli.py

Constructs, initializes and registers the CLI Command Registry.
"""

from __future__ import annotations

from aios.services.command import CommandRegistry


def bootstrap_cli(registry) -> CommandRegistry:  # noqa: ANN001
    """Constructs, initializes, and registers CLI components."""
    command_registry = CommandRegistry()
    command_registry.initialize()
    registry.register(CommandRegistry, command_registry)
    return command_registry
