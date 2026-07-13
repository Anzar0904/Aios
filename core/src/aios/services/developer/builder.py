from pathlib import Path
from typing import Any, Dict, List, Optional


def format_to_markdown(data: Any, indent: int = 0) -> str:
    if isinstance(data, dict):
        lines = []
        for k, v in data.items():
            if v is None or v == [] or v == "":
                continue
            key_str = "  " * indent + f"* **{k}**:"
            if isinstance(v, (dict, list)):
                lines.append(key_str)
                lines.append(format_to_markdown(v, indent + 1))
            else:
                lines.append(f"{key_str} {v}")
        return "\n".join(lines)
    elif isinstance(data, list):
        lines = []
        for item in data:
            if isinstance(item, (dict, list)):
                lines.append(format_to_markdown(item, indent + 1))
            else:
                lines.append("  " * indent + f"- {item}")
        return "\n".join(lines)
    else:
        return str(data)


class PromptBuilder:
    def __init__(self, templates_dir: str) -> None:
        self.templates_dir = Path(templates_dir).resolve()

    def build_prompt(
        self,
        template_name: str,
        workspace_summary: Dict[str, Any],
        intent_action: str,
        intent_parameters: Dict[str, Any],
        memories: List[Any],
        extra_replacements: Optional[Dict[str, Any]] = None,
    ) -> str:
        template_path = self.templates_dir / f"{template_name}.md"
        if not template_path.is_file():
            # Fallback inline template
            template_content = (
                "You are a Senior Software Developer Agent.\n\n"
                "## Workspace Summary\n{workspace_summary}\n\n"
                "## Intent Action\n* Action: {intent_action}\n* Parameters: {intent_parameters}\n\n"
                "## Memories\n{memories}\n"
            )
        else:
            try:
                template_content = template_path.read_text(encoding="utf-8")
            except Exception as e:
                raise RuntimeError(f"Failed to read prompt template '{template_name}': {e}") from e

        # Format memories
        formatted_memories = ""
        if memories:
            formatted_memories = "\n".join(
                [f"- [{m.memory_type.value}] {m.content}" for m in memories]
            )
        else:
            formatted_memories = "No relevant memories retrieved."

        # Format workspace summary sections
        summary_formatted = {}
        for section, content in workspace_summary.items():
            summary_formatted[section.lower().replace(" ", "_")] = format_to_markdown(content)

        replacements = {
            "workspace_summary": format_to_markdown(workspace_summary),
            "project": summary_formatted.get("project", ""),
            "languages": summary_formatted.get("languages", ""),
            "frameworks": summary_formatted.get("frameworks", ""),
            "architecture": summary_formatted.get("architecture", ""),
            "modules": summary_formatted.get("modules", ""),
            "dependencies": summary_formatted.get("dependencies", ""),
            "tests": summary_formatted.get("tests", ""),
            "git_status": summary_formatted.get("git_status", ""),
            "git_diff": summary_formatted.get("git_diff", ""),
            "git_diff_cached": summary_formatted.get("git_diff_cached", ""),
            "recent_activity": summary_formatted.get("recent_activity", ""),
            "open_todos": summary_formatted.get("open_todos", ""),
            "intent_action": intent_action,
            "intent_parameters": format_to_markdown(intent_parameters),
            "memories": formatted_memories,
        }

        # Merge extra replacements if provided
        if extra_replacements:
            for k, v in extra_replacements.items():
                replacements[k] = str(v)

        # Build prompt by replacing placeholders
        prompt = template_content
        for key, val in replacements.items():
            placeholder = f"{{{key}}}"
            prompt = prompt.replace(placeholder, str(val))

        return prompt

    def build_prompt_from_reasoning_context(
        self,
        template_name: str,
        reasoning_context: Any,
    ) -> str:
        template_path = self.templates_dir / f"{template_name}.md"
        if not template_path.is_file():
            # Fallback inline template
            template_content = (
                "You are a Senior Software Developer Agent.\n\n"
                "## Workspace Summary\n{project}\n\n"
                "## Intent Action\n* Action: {intent_action}\n* Parameters: {intent_parameters}\n\n"
                "## Memories\n{memories}\n"
            )
        else:
            try:
                template_content = template_path.read_text(encoding="utf-8")
            except Exception as e:
                raise RuntimeError(f"Failed to read prompt template '{template_name}': {e}") from e

        # Format memories
        formatted_memories = ""
        if reasoning_context.memories:
            formatted_memories = "\n".join(
                [f"- [{m.memory_type.value}] {m.content}" for m in reasoning_context.memories]
            )
        else:
            formatted_memories = "No relevant memories retrieved."

        # Map workspace/repository analysis sections
        repo = reasoning_context.repository_analysis

        replacements = {
            "intent_action": reasoning_context.intent.action,
            "intent_parameters": format_to_markdown(reasoning_context.intent.parameters),
            "memories": formatted_memories,
            "conversation_summary": reasoning_context.conversation_summary,
            "conversation_history": reasoning_context.conversation_history,
            "expanded_query": reasoning_context.expanded_query,
            "selected_tools": ", ".join(reasoning_context.selected_tools),
            "project": format_to_markdown(reasoning_context.workspace.get("project_name", "")),
            "languages": format_to_markdown(repo.get("languages", "")),
            "frameworks": format_to_markdown(repo.get("frameworks", "")),
            "architecture": format_to_markdown(repo.get("architecture", "")),
            "modules": format_to_markdown(repo.get("modules", "")),
            "dependencies": format_to_markdown(repo.get("dependencies", "")),
            "tests": format_to_markdown(repo.get("tests", "")),
            "git_status": format_to_markdown(repo.get("git_status", "")),
            "git_diff": format_to_markdown(repo.get("git_diff", "")),
            "git_diff_cached": format_to_markdown(repo.get("git_diff_cached", "")),
            "recent_activity": format_to_markdown(repo.get("recent_activity", "")),
            "open_todos": format_to_markdown(repo.get("open_todos", "")),
        }

        # Build prompt by replacing placeholders
        prompt = template_content
        for key, val in replacements.items():
            placeholder = f"{{{key}}}"
            prompt = prompt.replace(placeholder, str(val))
        return prompt
