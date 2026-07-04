import importlib.machinery
import importlib.util
from pathlib import Path
from typing import Any

from aios.skills.metadata import SkillMetadata


class BaseSkill:
    def __init__(self, metadata: SkillMetadata, path: str) -> None:
        self.metadata = metadata
        self.path = Path(path)
        self.enabled = True

    def register_commands(self, registry: Any, kernel: Any, conv_manager: Any) -> None:
        if not self.enabled:
            return
        commands_file = self.path / "commands.py"
        if not commands_file.is_file():
            return

        try:
            loader = importlib.machinery.SourceFileLoader(
                self.metadata.id + "_commands", str(commands_file)
            )
            spec = importlib.util.spec_from_loader(self.metadata.id + "_commands", loader)
            if spec is not None:
                module = importlib.util.module_from_spec(spec)
                loader.exec_module(module)
                if hasattr(module, "register_commands"):
                    module.register_commands(registry, kernel, conv_manager)
        except Exception:
            pass

    def unregister_commands(self, registry: Any) -> None:
        for cmd_name in self.metadata.commands:
            registry.unregister_command(cmd_name)
