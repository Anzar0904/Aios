from dataclasses import dataclass, field
from typing import List


@dataclass
class SkillMetadata:
    id: str
    name: str
    version: str
    author: str
    description: str
    category: str
    commands: List[str] = field(default_factory=list)
    capabilities: List[str] = field(default_factory=list)
    required_tools: List[str] = field(default_factory=list)
    required_models: List[str] = field(default_factory=list)
    required_memory: List[str] = field(default_factory=list)
    prompt_directory: str = "prompts"
    enabled: bool = True

