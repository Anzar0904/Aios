import shutil
from pathlib import Path
from typing import Any

from aios.skills.loader import SkillLoader
from aios.skills.registry import SkillRegistry


class SkillManager:
    def __init__(self, skills_dir: Path, registry: SkillRegistry) -> None:
        self.skills_dir = Path(skills_dir)
        self.registry = registry
        self.loader = SkillLoader()

    def load_all_skills(self) -> None:
        if not self.skills_dir.is_dir():
            self.skills_dir.mkdir(parents=True, exist_ok=True)

        for path in self.skills_dir.iterdir():
            if path.is_dir() and not path.name.startswith("."):
                skill = self.loader.load_skill(path)
                if skill:
                    self.registry.register(skill)

    def register_all_commands(self, command_registry: Any, kernel: Any, conv_manager: Any) -> None:
        for skill in self.registry.list_skills():
            if skill.enabled:
                skill.register_commands(command_registry, kernel, conv_manager)

    def install_skill(self, source_dir: Path) -> bool:
        if not source_dir.is_dir():
            return False
        dest = self.skills_dir / source_dir.name
        if dest.exists():
            return False
        shutil.copytree(source_dir, dest)
        skill = self.loader.load_skill(dest)
        if skill:
            self.registry.register(skill)
            return True
        return False

    def uninstall_skill(self, skill_id: str, command_registry: Any) -> bool:
        skill = self.registry.get_skill(skill_id)
        if not skill:
            return False
        skill.unregister_commands(command_registry)
        self.registry.unregister(skill_id)
        if skill.path.exists():
            shutil.rmtree(skill.path)
        return True

    def enable_skill(
        self, skill_id: str, command_registry: Any, kernel: Any, conv_manager: Any
    ) -> bool:
        skill = self.registry.get_skill(skill_id)
        if not skill:
            return False
        skill.enabled = True
        skill.register_commands(command_registry, kernel, conv_manager)
        return True

    def disable_skill(self, skill_id: str, command_registry: Any) -> bool:
        skill = self.registry.get_skill(skill_id)
        if not skill:
            return False
        skill.enabled = False
        skill.unregister_commands(command_registry)
        return True

    def reload_skill(
        self, skill_id: str, command_registry: Any, kernel: Any, conv_manager: Any
    ) -> bool:
        skill = self.registry.get_skill(skill_id)
        if not skill:
            return False
        skill.unregister_commands(command_registry)

        reloaded = self.loader.load_skill(skill.path)
        if reloaded:
            reloaded.enabled = skill.enabled
            self.registry.register(reloaded)
            if reloaded.enabled:
                reloaded.register_commands(command_registry, kernel, conv_manager)
            return True
        return False
