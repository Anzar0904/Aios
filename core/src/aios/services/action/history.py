import json
from pathlib import Path
from typing import List, Optional

from aios.services.action.models import ActionPlan


class ActionHistory:
    def __init__(self, storage_dir: Path) -> None:
        self.storage_dir = Path(storage_dir)
        try:
            self.storage_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            import tempfile

            self.storage_dir = Path(tempfile.gettempdir()) / "aios_actions_fallback"
            self.storage_dir.mkdir(parents=True, exist_ok=True)

        self._active_plan_path = self.storage_dir / "active_plan.json"

    def _get_path(self, plan_id: str) -> Path:
        return self.storage_dir / f"{plan_id}.json"

    def save_plan(self, plan: ActionPlan) -> None:
        path = self._get_path(plan.id)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(plan.to_dict(), f, indent=2, ensure_ascii=False)

    def set_active_plan(self, plan: ActionPlan) -> None:
        with open(self._active_plan_path, "w", encoding="utf-8") as f:
            json.dump(plan.to_dict(), f, indent=2, ensure_ascii=False)

    def get_active_plan(self) -> Optional[ActionPlan]:
        if not self._active_plan_path.is_file():
            return None
        try:
            with open(self._active_plan_path, "r", encoding="utf-8") as f:
                return ActionPlan.from_dict(json.load(f))
        except Exception:
            return None

    def clear_active_plan(self) -> None:
        if self._active_plan_path.is_file():
            self._active_plan_path.unlink()

    def load_plan(self, plan_id: str) -> Optional[ActionPlan]:
        path = self._get_path(plan_id)
        if not path.is_file():
            plans = self.list_plans()
            for p in plans:
                if p.id.startswith(plan_id):
                    return p
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                return ActionPlan.from_dict(json.load(f))
        except Exception:
            return None

    def list_plans(self) -> List[ActionPlan]:
        plans = []
        for path in self.storage_dir.glob("*.json"):
            if path.name == "active_plan.json":
                continue
            try:
                with open(path, "r", encoding="utf-8") as f:
                    plans.append(ActionPlan.from_dict(json.load(f)))
            except Exception:
                pass
        plans.sort(key=lambda x: x.updated_at, reverse=True)
        return plans
