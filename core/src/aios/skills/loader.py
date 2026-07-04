import tomllib
from pathlib import Path
from typing import Optional

from aios.skills.base import BaseSkill
from aios.skills.metadata import SkillMetadata


class SkillLoader:
    def __init__(self) -> None:
        pass

    def load_skill(self, skill_dir: Path) -> Optional[BaseSkill]:
        toml_path = skill_dir / "skill.toml"
        if not toml_path.is_file():
            return None

        try:
            with open(toml_path, "rb") as f:
                data = tomllib.load(f)
            skill_data = data.get("skill", {})
            metadata = SkillMetadata(
                id=skill_data["id"],
                name=skill_data["name"],
                version=skill_data["version"],
                author=skill_data["author"],
                description=skill_data["description"],
                category=skill_data["category"],
                commands=skill_data.get("commands", []),
                capabilities=skill_data.get("capabilities", []),
                required_tools=skill_data.get("required_tools", []),
                required_models=skill_data.get("required_models", []),
                required_memory=skill_data.get("required_memory", []),
                prompt_directory=skill_data.get("prompt_directory", "prompts"),
            )
            return BaseSkill(metadata, str(skill_dir))
        except Exception:
            # Fallback simple toml parser
            try:
                content = toml_path.read_text(encoding="utf-8")
                res = {}
                for line in content.splitlines():
                    line = line.strip()
                    if not line or line.startswith("#") or line.startswith("["):
                        continue
                    if "=" in line:
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip('"').strip("'")
                        if v.startswith("[") and v.endswith("]"):
                            v = [
                                item.strip().strip('"').strip("'")
                                for item in v[1:-1].split(",")
                                if item.strip()
                            ]
                        res[k] = v
                metadata = SkillMetadata(
                    id=res["id"],
                    name=res["name"],
                    version=res["version"],
                    author=res["author"],
                    description=res["description"],
                    category=res["category"],
                    commands=res.get("commands", []),
                    capabilities=res.get("capabilities", []),
                    required_tools=res.get("required_tools", []),
                    required_models=res.get("required_models", []),
                    required_memory=res.get("required_memory", []),
                    prompt_directory=res.get("prompt_directory", "prompts"),
                )
                return BaseSkill(metadata, str(skill_dir))
            except Exception:
                return None
