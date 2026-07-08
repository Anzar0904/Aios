import abc
import json
import logging
from pathlib import Path
from typing import Dict, Optional

from aios.services.base import ServiceLifecycle

logger = logging.getLogger(__name__)


class NotionCredentialsStore:
    """Manages reading and writing Notion integration tokens to local storage."""

    def __init__(self, path: Optional[Path] = None) -> None:
        self.path = path or Path(".agent/notion/credentials.json")

    def _ensure_dir(self) -> None:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.error(f"Failed to create directory for credentials: {e}")

    def load_all(self) -> Dict[str, str]:
        """Loads all workspace credentials from credentials.json."""
        if not self.path.is_file():
            return {}
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    return {}
                data = json.loads(content)
                if isinstance(data, dict):
                    return data
        except Exception as e:
            logger.error(f"Failed to load Notion credentials: {e}")
        return {}

    def save_token(self, workspace_name: str, token: str) -> None:
        """Saves a token mapped to a workspace name."""
        self._ensure_dir()
        current = self.load_all()
        updated = {**current, workspace_name: token}
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(updated, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save Notion token: {e}")

    def delete_workspace(self, workspace_name: str) -> None:
        """Removes a workspace from credentials."""
        if not self.path.is_file():
            return
        current = self.load_all()
        updated = {k: v for k, v in current.items() if k != workspace_name}
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(updated, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to delete Notion workspace: {e}")

    def delete_all(self) -> None:
        """Removes all credentials and deletes the credentials file if it exists."""
        if self.path.is_file():
            try:
                self.path.unlink()
            except Exception as e:
                logger.error(f"Failed to delete credentials file: {e}")


class NotionService(ServiceLifecycle, abc.ABC):
    """Unified service interface for Notion Intelligence."""

    @abc.abstractmethod
    def login(self, token: str, workspace_name: str) -> bool:
        """Connect a workspace using an Integration Token."""
        pass

    @abc.abstractmethod
    def logout(self, workspace_name: Optional[str] = None) -> bool:
        """Disconnect workspace(s)."""
        pass

    @abc.abstractmethod
    def get_status(self) -> dict:
        """Get the current service status."""
        pass

    @abc.abstractmethod
    def sync(self) -> dict:
        """Sync pages and databases from connected workspaces."""
        pass

    @abc.abstractmethod
    def search(self, query: str) -> list:
        """Search connected Notion workspaces for pages/databases."""
        pass

    @abc.abstractmethod
    def summarize(self, page_id: str) -> str:
        """Summarize a page's content."""
        pass

    @abc.abstractmethod
    def create_page(self, parent_id: str, title: str, content: str) -> dict:
        """Create a new page."""
        pass

    @abc.abstractmethod
    def update_page(self, page_id: str, content: str) -> dict:
        """Update existing page content."""
        pass

    @abc.abstractmethod
    def list_databases(self) -> list:
        """List all accessible databases."""
        pass
