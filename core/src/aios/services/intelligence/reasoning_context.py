from typing import Any, Dict, List

from aios.services.intent import Intent


class ReasoningContext:
    def __init__(
        self,
        intent: Intent,
        repository_analysis: Dict[str, Any],
        conversation_summary: str,
        conversation_history: str,
        memories: List[Any],
        workspace: Dict[str, Any],
        selected_tools: List[str],
        expanded_query: str
    ) -> None:
        self.intent = intent
        self.repository_analysis = repository_analysis
        self.conversation_summary = conversation_summary
        self.conversation_history = conversation_history
        self.memories = memories
        self.workspace = workspace
        self.selected_tools = selected_tools
        self.expanded_query = expanded_query
