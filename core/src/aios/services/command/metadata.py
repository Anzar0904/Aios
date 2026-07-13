from enum import Enum
from typing import List


class CommandCategory(Enum):
    DEVELOPER = "Developer"
    CAREER = "Career"
    RESEARCH = "Research"
    AUTOMATION = "Automation"
    LEARNING = "Learning"
    SYSTEM = "System"
    MEMORY = "Memory"
    CONVERSATION = "Conversation"
    CLI = "CLI"


class CommandMetadata:
    def __init__(
        self,
        name: str,
        description: str,
        category: CommandCategory,
        required_agent: str,
        required_tools: List[str],
        example_usage: str,
    ) -> None:
        self.name = name
        self.description = description
        self.category = category
        self.required_agent = required_agent
        self.required_tools = required_tools
        self.example_usage = example_usage
