from typing import List

from aios.services.intent import Intent


class ToolSelector:
    def __init__(self) -> None:
        pass

    def select_tools(self, intent: Intent) -> List[str]:
        action = intent.action.lower()
        
        if "repository" in action or "dependencies" in action or "todo" in action:
            return ["filesystem", "git", "memory"]
        elif "git" in action or "commit" in action or "release" in action:
            return ["git", "memory"]
        elif "file" in action or "ats" in action or "resume" in action or "job" in action:
            return ["filesystem", "memory"]
        elif "status" in action:
            return ["memory"]
        
        return ["filesystem", "memory"]
