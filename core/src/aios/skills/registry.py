from typing import Dict, List, Optional

from aios.skills.base import BaseSkill


class SkillRegistry:
    def __init__(self) -> None:
        self._skills: Dict[str, BaseSkill] = {}

    def register(self, skill: BaseSkill) -> None:
        self._skills[skill.metadata.id] = skill

    def unregister(self, skill_id: str) -> None:
        if skill_id in self._skills:
            del self._skills[skill_id]

    def get_skill(self, skill_id: str) -> Optional[BaseSkill]:
        return self._skills.get(skill_id)

    def list_skills(self) -> List[BaseSkill]:
        return list(self._skills.values())
