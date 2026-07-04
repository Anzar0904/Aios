import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class ConversationStore:
    def __init__(self, storage_dir: Path) -> None:
        self.storage_dir = Path(storage_dir)
        try:
            self.storage_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            import tempfile
            self.storage_dir = Path(tempfile.gettempdir()) / "aios_conversations_fallback"
            self.storage_dir.mkdir(parents=True, exist_ok=True)

    def _get_path(self, conversation_id: str) -> Path:
        return self.storage_dir / f"{conversation_id}.json"

    def save(self, conversation: Dict[str, Any]) -> None:
        path = self._get_path(conversation["id"])
        with open(path, "w", encoding="utf-8") as f:
            json.dump(conversation, f, indent=2, ensure_ascii=False)

    def load(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        path = self._get_path(conversation_id)
        if not path.is_file():
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    def list_all(self) -> List[Dict[str, Any]]:
        conversations = []
        for path in self.storage_dir.glob("*.json"):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict) and "id" in data:
                        conversations.append(data)
            except Exception:
                pass
        conversations.sort(key=lambda x: x.get("updated_time", 0.0), reverse=True)
        return conversations

    def delete(self, conversation_id: str) -> bool:
        path = self._get_path(conversation_id)
        if path.is_file():
            path.unlink()
            return True
        return False
