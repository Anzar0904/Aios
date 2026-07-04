from pathlib import Path

from aios.skills.manager import SkillManager


class SkillInstaller:
    def __init__(self, manager: SkillManager) -> None:
        self.manager = manager

    def install(self, source_dir: str) -> bool:
        return self.manager.install_skill(Path(source_dir))
