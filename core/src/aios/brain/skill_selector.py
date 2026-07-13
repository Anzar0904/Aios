from typing import List, Optional

from aios.brain.models import SkillSelection
from aios.skills.registry import SkillRegistry


class SkillSelector:
    def __init__(self, skill_registry: SkillRegistry) -> None:
        self.skill_registry = skill_registry

    def select_skills(
        self, objective: str, capability: Optional[str] = None
    ) -> List[SkillSelection]:
        query = objective.lower().strip()
        selections = []

        skills = self.skill_registry.list_skills()

        # Automatic GitHub Intelligence trigger based on query intent keywords
        github_keywords = [
            "github",
            "repository",
            "repo",
            "pull request",
            "pr",
            "issue",
            "commit",
            "branch",
            "release",
            "workflow",
            "actions",
        ]
        import re

        if any(re.search(r"\b" + re.escape(kw) + r"\b", query) for kw in github_keywords):
            for skill in skills:
                if skill.metadata.id == "github" and skill.enabled:
                    return [
                        SkillSelection(
                            skill_id="github",
                            confidence=0.99,
                            reason="Automatic GitHub Intelligence trigger based on query intent keywords.",
                            matched_commands=list(skill.metadata.commands),
                        )
                    ]

        # 1. Deterministic/Exact command match:
        for skill in skills:
            if not skill.enabled:
                continue

                continue
            # Filter by capability if specified
            if capability and capability not in getattr(skill.metadata, "capabilities", []):
                continue

            matched_commands = []
            for cmd in skill.metadata.commands:
                if query == cmd.lower() or query.startswith(cmd.lower() + " "):
                    matched_commands.append(cmd)

            if matched_commands:
                selections.append(
                    SkillSelection(
                        skill_id=skill.metadata.id,
                        confidence=1.0,
                        reason=f"Deterministic match on command(s): {', '.join(matched_commands)}",
                        matched_commands=matched_commands,
                    )
                )

        if selections:
            # Longest command match first
            selections.sort(key=lambda x: len(x.matched_commands[0]), reverse=True)
            return [selections[0]]

        # 2. Heuristic/Keyword match:
        for skill in skills:
            if not skill.enabled:
                continue
            # Filter by capability if specified
            if capability and capability not in getattr(skill.metadata, "capabilities", []):
                continue

            score = 0.0
            matched_cmds = []

            # Dynamic capability matching: if no specific capability constraint is provided,
            # boost skills whose capability tags match keyword words in the query
            skill_caps = getattr(skill.metadata, "capabilities", [])
            for cap in skill_caps:
                if cap.lower() in query:
                    score += 0.5

            category = (
                skill.metadata.category.lower()
                if hasattr(skill.metadata, "category") and skill.metadata.category
                else ""
            )
            if category and category in query:
                score += 0.4

            desc = skill.metadata.description.lower()
            desc_words = desc.split()
            query_words = query.split()
            common_words = set(desc_words).intersection(set(query_words))
            if common_words:
                score += min(0.3, len(common_words) * 0.05)

            for cmd in skill.metadata.commands:
                cmd_lower = cmd.lower()
                if any(word in query for word in cmd_lower.split() if len(word) > 2):
                    score += 0.15
                    matched_cmds.append(cmd)

            if score > 0.0:
                selections.append(
                    SkillSelection(
                        skill_id=skill.metadata.id,
                        confidence=min(0.95, score),
                        reason="Heuristic match on description/category, capabilities, and commands.",
                        matched_commands=matched_cmds,
                    )
                )

        selections.sort(key=lambda x: x.confidence, reverse=True)
        return selections
