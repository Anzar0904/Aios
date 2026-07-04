import json
from pathlib import Path
from typing import List, Optional

from aios.services.task.models import Task


class TaskHistory:
    def __init__(self, storage_dir: Path) -> None:
        self.storage_dir = Path(storage_dir)
        try:
            self.storage_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            import tempfile
            self.storage_dir = Path(tempfile.gettempdir()) / "aios_tasks_fallback"
            self.storage_dir.mkdir(parents=True, exist_ok=True)

    def _get_path(self, task_id: str) -> Path:
        return self.storage_dir / f"{task_id}.json"

    def save_task(self, task: Task) -> None:
        path = self._get_path(task.id)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(task.to_dict(), f, indent=2, ensure_ascii=False)

    def load_task(self, task_id: str) -> Optional[Task]:
        path = self._get_path(task_id)
        if not path.is_file():
            tasks = self.list_tasks()
            for t in tasks:
                if t.id.startswith(task_id) or t.title.lower() == task_id.lower():
                    return t
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                return Task.from_dict(json.load(f))
        except Exception:
            return None

    def list_tasks(self) -> List[Task]:
        tasks = []
        for path in self.storage_dir.glob("*.json"):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    tasks.append(Task.from_dict(json.load(f)))
            except Exception:
                pass
        tasks.sort(key=lambda x: x.updated_at, reverse=True)
        return tasks

    def delete_task(self, task_id: str) -> bool:
        path = self._get_path(task_id)
        if path.is_file():
            path.unlink()
            return True
        tasks = self.list_tasks()
        for t in tasks:
            if t.id.startswith(task_id):
                self._get_path(t.id).unlink()
                return True
        return False
