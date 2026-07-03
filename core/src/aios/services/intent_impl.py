import logging

from aios.services.intent import Intent, IntentResolverService, IntentType

logger = logging.getLogger(__name__)


class LocalIntentResolver(IntentResolverService):
    """Rule-based implementation of IntentResolverService for the MVP.

    Maps natural language phrases to structured Intents.
    """

    def initialize(self) -> None:
        logger.info("Initializing LocalIntentResolver")

    def classify(self, text: str) -> IntentType:
        """Classifies natural language text into an IntentType based on rules."""
        cleaned = text.strip().lower()

        # Memory rules
        if cleaned.startswith("remember") or cleaned.startswith("add memory"):
            return IntentType.MEMORY

        # Context rules
        if cleaned in (
            "show my current project",
            "show current project",
            "show project",
            "show context",
            "context",
            "project",
        ):
            return IntentType.CONTEXT

        # Session rules
        if cleaned in ("end session", "exit session", "quit session", "end", "exit", "quit"):
            return IntentType.SESSION

        # Developer rules
        if cleaned in ("analyze repository", "analyze repo", "repository analysis"):
            return IntentType.DEVELOPER

        if (
            cleaned == "explain this file"
            or cleaned.startswith("explain file ")
            or cleaned.startswith("explain ")
        ):
            return IntentType.DEVELOPER

        if cleaned in (
            "summarize architecture",
            "architecture summary",
            "summarize arch",
            "summarize",
        ):
            return IntentType.DEVELOPER

        if cleaned in ("git review", "git status review", "review git"):
            return IntentType.DEVELOPER

        # System rules
        if cleaned in ("status", "system status", "uptime", "kernel status"):
            return IntentType.SYSTEM

        # Tool rules mapped to System
        if cleaned in ("tool list", "tools"):
            return IntentType.SYSTEM

        if cleaned.startswith("git ") or cleaned == "git":
            return IntentType.SYSTEM

        if cleaned == "ls" or cleaned.startswith("ls "):
            return IntentType.SYSTEM

        if cleaned.startswith("read ") or cleaned.startswith("write "):
            return IntentType.SYSTEM

        if cleaned in ("pwd", "whoami") or cleaned.startswith("echo "):
            return IntentType.SYSTEM

        return IntentType.UNKNOWN

    def resolve(self, text: str) -> Intent:
        """Translates natural language text into a structured Intent."""
        cleaned = text.strip()
        intent_type = self.classify(cleaned)

        if intent_type == IntentType.MEMORY:
            lower_text = cleaned.lower()
            content = ""
            if lower_text.startswith("remember this:"):
                content = cleaned[len("remember this:") :].strip()
            elif lower_text.startswith("remember this"):
                content = cleaned[len("remember this") :].strip()
            elif lower_text.startswith("remember"):
                content = cleaned[len("remember") :].strip()
            elif lower_text.startswith("add memory"):
                content = cleaned[len("add memory") :].strip()

            if not content:
                content = "Remembered interaction"

            return Intent(
                intent_type=IntentType.MEMORY,
                target_service="MemoryService",
                action="Add",
                parameters={"content": content},
                confidence=1.0,
            )

        elif intent_type == IntentType.CONTEXT:
            return Intent(
                intent_type=IntentType.CONTEXT,
                target_service="ContextService",
                action="Show",
                parameters={},
                confidence=1.0,
            )

        elif intent_type == IntentType.SESSION:
            return Intent(
                intent_type=IntentType.SESSION,
                target_service="SessionService",
                action="End",
                parameters={},
                confidence=1.0,
            )

        elif intent_type == IntentType.DEVELOPER:
            lower_text = cleaned.lower()
            if lower_text in ("analyze repository", "analyze repo", "repository analysis"):
                return Intent(
                    intent_type=IntentType.DEVELOPER,
                    target_service="AgentRuntimeService",
                    action="AnalyzeRepository",
                    parameters={},
                    confidence=1.0,
                )
            elif (
                lower_text == "explain this file"
                or lower_text.startswith("explain file ")
                or lower_text.startswith("explain ")
            ):
                path = "core/src/aios/kernel.py"
                if lower_text.startswith("explain file "):
                    path = cleaned[len("explain file ") :].strip()
                elif lower_text.startswith("explain "):
                    extracted = cleaned[len("explain ") :].strip()
                    if extracted != "this file" and extracted != "file":
                        path = extracted
                return Intent(
                    intent_type=IntentType.DEVELOPER,
                    target_service="AgentRuntimeService",
                    action="ExplainFile",
                    parameters={"path": path},
                    confidence=1.0,
                )
            elif lower_text in (
                "summarize architecture",
                "architecture summary",
                "summarize arch",
                "summarize",
            ):
                return Intent(
                    intent_type=IntentType.DEVELOPER,
                    target_service="AgentRuntimeService",
                    action="SummarizeArchitecture",
                    parameters={},
                    confidence=1.0,
                )
            elif lower_text in ("git review", "git status review", "review git"):
                return Intent(
                    intent_type=IntentType.DEVELOPER,
                    target_service="AgentRuntimeService",
                    action="GitReview",
                    parameters={},
                    confidence=1.0,
                )

        elif intent_type == IntentType.SYSTEM:
            lower_text = cleaned.lower()
            if lower_text in ("tool list", "tools"):
                return Intent(
                    intent_type=IntentType.SYSTEM,
                    target_service="ToolService",
                    action="ToolList",
                    parameters={},
                    confidence=1.0,
                )

            elif lower_text.startswith("git ") or lower_text == "git":
                action = lower_text[4:].strip() if lower_text.startswith("git ") else "status"
                if action in ("status", "branch", "log"):
                    return Intent(
                        intent_type=IntentType.SYSTEM,
                        target_service="ToolService",
                        action="ExecuteTool",
                        parameters={"tool_name": "git", "arguments": {"action": action}},
                        confidence=1.0,
                    )
                else:
                    return Intent(
                        intent_type=IntentType.SYSTEM,
                        target_service="ToolService",
                        action="ExecuteTool",
                        parameters={"tool_name": "terminal", "arguments": {"command": cleaned}},
                        confidence=0.8,
                    )

            elif lower_text == "ls" or lower_text.startswith("ls "):
                path = cleaned[3:].strip() if lower_text.startswith("ls ") else "."
                return Intent(
                    intent_type=IntentType.SYSTEM,
                    target_service="ToolService",
                    action="ExecuteTool",
                    parameters={
                        "tool_name": "filesystem",
                        "arguments": {"action": "list", "path": path},
                    },
                    confidence=1.0,
                )

            elif lower_text.startswith("read "):
                path = cleaned[5:].strip()
                return Intent(
                    intent_type=IntentType.SYSTEM,
                    target_service="ToolService",
                    action="ExecuteTool",
                    parameters={
                        "tool_name": "filesystem",
                        "arguments": {"action": "read", "path": path},
                    },
                    confidence=1.0,
                )

            elif lower_text.startswith("write "):
                rest = cleaned[6:].strip()
                path = rest
                content = ""
                if " " in rest:
                    path, content = rest.split(" ", 1)
                return Intent(
                    intent_type=IntentType.SYSTEM,
                    target_service="ToolService",
                    action="ExecuteTool",
                    parameters={
                        "tool_name": "filesystem",
                        "arguments": {"action": "write", "path": path, "content": content},
                    },
                    confidence=1.0,
                )

            elif lower_text in ("pwd", "whoami") or lower_text.startswith("echo "):
                return Intent(
                    intent_type=IntentType.SYSTEM,
                    target_service="ToolService",
                    action="ExecuteTool",
                    parameters={"tool_name": "terminal", "arguments": {"command": cleaned}},
                    confidence=1.0,
                )

            elif lower_text in ("status", "system status", "uptime", "kernel status"):
                return Intent(
                    intent_type=IntentType.SYSTEM,
                    target_service="Kernel",
                    action="Status",
                    parameters={},
                    confidence=1.0,
                )

        return Intent(
            intent_type=IntentType.UNKNOWN,
            target_service="None",
            action="Unknown",
            parameters={},
            confidence=0.0,
        )

    def validate(self, intent: Intent) -> bool:
        """Validates that a resolved Intent is well-formed and executable."""
        if intent.intent_type == IntentType.UNKNOWN:
            return False
        if not intent.target_service or not intent.action:
            return False
        if intent.intent_type == IntentType.MEMORY and "content" not in intent.parameters:
            return False
        return True
