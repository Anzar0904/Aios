import logging
from pathlib import Path
from typing import Any, Dict, Optional

from aios.services.notion import NotionCredentialsStore, NotionService

logger = logging.getLogger(__name__)


class LocalNotionService(NotionService):
    """Stub/Mock implementation of NotionService to verify authentication and credentials store."""

    def __init__(
        self,
        model_service: Optional[Any] = None,
        credentials_path: Optional[Path] = None,
    ) -> None:
        self._model_service = model_service
        self._credentials_store = NotionCredentialsStore(path=credentials_path)
        self._workspaces: Dict[str, str] = {}

    def initialize(self) -> None:
        """Initialize the service and load persisted credentials."""
        logger.info("Initializing LocalNotionService")
        self._workspaces = self._credentials_store.load_all()

    def start(self) -> None:
        """Start the service."""
        pass

    def shutdown(self) -> None:
        """Shutdown the service."""
        pass

    def login(self, token: str, workspace_name: str) -> bool:
        """Connect a workspace using an Integration Token."""
        if not token or not workspace_name:
            return False
        self._credentials_store.save_token(workspace_name, token)
        self._workspaces = self._credentials_store.load_all()
        return True

    def logout(self, workspace_name: Optional[str] = None) -> bool:
        """Disconnect workspace(s)."""
        if workspace_name is None:
            self._credentials_store.delete_all()
        else:
            self._credentials_store.delete_workspace(workspace_name)
        self._workspaces = self._credentials_store.load_all()
        return True

    def get_status(self) -> dict:
        """Get the current service status."""
        return {
            "status": "connected" if self._workspaces else "disconnected",
            "workspaces": list(self._workspaces.keys()),
        }

    def sync(self) -> dict:
        """Sync pages and databases from connected workspaces (mock implementation)."""
        return {
            "status": "success",
            "synced_pages": 0,
            "workspaces": list(self._workspaces.keys()),
        }

    def search(self, query: str) -> list:
        """Search connected Notion workspaces for pages/databases (mock implementation)."""
        return []

    def summarize(self, page_id: str) -> str:
        """Summarize a page's content (mock implementation)."""
        return f"Summary of page {page_id}"

    def create_page(self, parent_id: str, title: str, content: str) -> dict:
        """Create a new page (mock implementation)."""
        return {
            "id": f"mock_page_{parent_id}",
            "title": title,
            "parent_id": parent_id,
            "status": "created",
        }

    def update_page(self, page_id: str, content: str) -> dict:
        """Update existing page content (mock implementation)."""
        return {
            "id": page_id,
            "content": content,
            "status": "updated",
        }

    def list_databases(self) -> list:
        """List all accessible databases (mock implementation)."""
        return []
