from pathlib import Path

from aios.services.command.registry import CommandRegistry


class DocumentationGenerator:
    def __init__(self, registry: CommandRegistry) -> None:
        self.registry = registry

    def generate_markdown(self, output_path: Path) -> None:
        lines = [
            "# Personal AI OS Command Reference",
            "",
            "This document is automatically generated from the Command Registry.",
            "",
        ]

        from aios.services.command.metadata import CommandCategory

        for category in CommandCategory:
            cmds = self.registry.list_commands(category)
            if not cmds:
                continue
            lines.append(f"## {category.value} Commands")
            lines.append("")
            for cmd in cmds:
                lines.append(f"### `{cmd.name}`")
                lines.append(f"- **Description**: {cmd.description}")
                lines.append(f"- **Category**: {cmd.category.value}")
                lines.append(f"- **Required Agent**: {cmd.required_agent}")
                tools_str = (
                    ", ".join(cmd.required_tools) if cmd.required_tools else "None"
                )
                lines.append(f"- **Required Tools**: {tools_str}")
                lines.append(f"- **Example**: `{cmd.example_usage}`")
                lines.append("")

        output_path.write_text("\n".join(lines), encoding="utf-8")
