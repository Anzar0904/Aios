import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from aios.services.conversation.models import (
    Conversation,
    ConversationMessage,
    ConversationSummary,
)
from aios.services.conversation.store import ConversationStore
from aios.services.model import LLMRequest, ModelService

logger = logging.getLogger(__name__)

def parse_summary_response(text: str) -> Dict[str, Any]:
    lines = text.strip().split("\n")
    summary = ""
    decisions = []
    action_items = []
    unresolved_questions = []
    
    current_section = None
    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            continue
        
        # Check for section headers
        if line_stripped.lower().startswith("summary:"):
            summary = line_stripped[8:].strip()
            current_section = "summary"
            continue
        elif line_stripped.lower().startswith("decisions:"):
            current_section = "decisions"
            continue
        elif line_stripped.lower().startswith("action items:"):
            current_section = "action_items"
            continue
        elif line_stripped.lower().startswith("unresolved questions:"):
            current_section = "unresolved_questions"
            continue
            
        # Parse bullet points or continue text
        if current_section == "summary":
            summary += " " + line_stripped
        elif current_section in ("decisions", "action_items", "unresolved_questions"):
            # strip bullet points
            if line_stripped.startswith(("-", "*", "•")):
                item = line_stripped[1:].strip()
            else:
                item = line_stripped
            
            if item:
                if current_section == "decisions":
                    decisions.append(item)
                elif current_section == "action_items":
                    action_items.append(item)
                elif current_section == "unresolved_questions":
                    unresolved_questions.append(item)
                    
    return {
        "summary": summary.strip(),
        "decisions": decisions,
        "action_items": action_items,
        "unresolved_questions": unresolved_questions
    }

class ConversationManager:
    def __init__(self, store: ConversationStore) -> None:
        self.store = store
        self.active_conversation_id: Optional[str] = None
        self._load_active_id()

    def _load_active_id(self) -> None:
        active_file = self.store.storage_dir / "active_conversation.txt"
        if active_file.is_file():
            try:
                self.active_conversation_id = active_file.read_text(encoding="utf-8").strip()
            except Exception:
                self.active_conversation_id = None

    def _save_active_id(self) -> None:
        active_file = self.store.storage_dir / "active_conversation.txt"
        try:
            if self.active_conversation_id:
                active_file.write_text(self.active_conversation_id, encoding="utf-8")
            else:
                if active_file.is_file():
                    active_file.unlink()
        except Exception:
            pass

    def create_conversation(
        self, title: Optional[str] = None, agent_name: Optional[str] = None
    ) -> Conversation:
        conv = Conversation(title=title, active_agent=agent_name)
        self.store.save(conv.to_dict())
        self.active_conversation_id = conv.id
        self._save_active_id()
        return conv

    def resume_conversation(self, conversation_id: str) -> Optional[Conversation]:
        data = self.store.load(conversation_id)
        if data:
            conv = Conversation.from_dict(data)
            self.active_conversation_id = conv.id
            self._save_active_id()
            return conv
        return None

    def get_current_conversation(self) -> Optional[Conversation]:
        if not self.active_conversation_id:
            return None
        data = self.store.load(self.active_conversation_id)
        if data:
            return Conversation.from_dict(data)
        return None

    def list_conversations(self) -> List[Dict[str, Any]]:
        return self.store.list_all()

    def rename_conversation(self, conversation_id: str, new_title: str) -> bool:
        data = self.store.load(conversation_id)
        if data:
            conv = Conversation.from_dict(data)
            conv.title = new_title
            conv.updated_time = time.time()
            self.store.save(conv.to_dict())
            return True
        return False

    def archive_conversation(self, conversation_id: str) -> bool:
        data = self.store.load(conversation_id)
        if data:
            conv = Conversation.from_dict(data)
            conv.archived = True
            conv.updated_time = time.time()
            self.store.save(conv.to_dict())
            return True
        return False

    def delete_conversation(self, conversation_id: str) -> bool:
        success = self.store.delete(conversation_id)
        if success and self.active_conversation_id == conversation_id:
            self.active_conversation_id = None
            self._save_active_id()
        return success

    def add_message(self, conversation_id: str, role: str, content: str) -> None:
        data = self.store.load(conversation_id)
        if data:
            conv = Conversation.from_dict(data)
            conv.messages.append(ConversationMessage(role, content))
            conv.updated_time = time.time()
            self.store.save(conv.to_dict())

    def summarize_if_needed(
        self,
        conversation: Conversation,
        model_service: ModelService,
        max_messages: int = 10,
    ) -> None:
        if len(conversation.messages) <= max_messages:
            return

        logger.info(
            f"Summarizing conversation {conversation.id} as message count "
            f"({len(conversation.messages)}) exceeds limit ({max_messages})"
        )

        keep_count = 4
        summarize_messages = conversation.messages[:-keep_count]
        keep_messages = conversation.messages[-keep_count:]

        msg_lines = []
        for m in summarize_messages:
            msg_lines.append(f"{m.role.upper()}: {m.content}")
        messages_to_summarize = "\n".join(msg_lines)

        prev_summary = "None"
        if conversation.summary:
            s = conversation.summary
            prev_summary = (
                f"Summary: {s.summary}\n"
                f"Decisions:\n" + "\n".join([f"- {d}" for d in s.decisions]) + "\n"
                "Action Items:\n" + "\n".join([f"- {a}" for a in s.action_items]) + "\n"
                "Unresolved Questions:\n"
                + "\n".join([f"- {q}" for q in s.unresolved_questions])
            )

        project_root = Path.cwd().resolve()
        template_path = project_root / "skills" / "conversation" / "prompts" / "summarize_history.md"

        if template_path.is_file():
            template_content = template_path.read_text(encoding="utf-8")
        else:
            template_content = (
                "You are an AI OS assistant.\n"
                "Summarize the following conversation history.\n\n"
                "## Previous Summary\n{previous_summary}\n\n"
                "## Messages to Summarize\n{messages_to_summarize}\n"
            )

        prompt = (
            template_content.replace("{previous_summary}", prev_summary)
            .replace("{messages_to_summarize}", messages_to_summarize)
        )

        try:
            llm_res = model_service.execute_request(
                LLMRequest(
                    prompt=prompt,
                    system_instruction=(
                        "You are an expert at summarizing technical conversations. "
                        "Return strictly formatted outputs."
                    ),
                    model_name="claude-3-5-sonnet",
                )
            )
            
            parsed = parse_summary_response(llm_res.content)
            
            conversation.summary = ConversationSummary(
                summary=parsed["summary"],
                decisions=parsed["decisions"],
                action_items=parsed["action_items"],
                unresolved_questions=parsed["unresolved_questions"]
            )
            
            conversation.messages = keep_messages
            conversation.updated_time = time.time()
            self.store.save(conversation.to_dict())
            
        except Exception as e:
            logger.error(f"Failed to summarize conversation {conversation.id}: {e}", exc_info=True)
