import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import httpx

from aios.services.notion import NotionCredentialsStore, NotionService

logger = logging.getLogger(__name__)


class LocalNotionService(NotionService):
    """Stub/Mock implementation of NotionService to verify authentication and credentials store."""

    def __init__(
        self,
        model_service: Optional[Any] = None,
        credentials_path: Optional[Path] = None,
        cache_path: Optional[Path] = None,
    ) -> None:
        self._model_service = model_service
        self._credentials_store = NotionCredentialsStore(path=credentials_path)
        self._cache_path = cache_path or Path(".agent/notion/cache.json")
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

    def _request(
        self,
        method: str,
        path: str,
        json_data: Optional[dict] = None,
        params: Optional[dict] = None,
        token: Optional[str] = None,
    ) -> dict:
        """Make an HTTP request to the Notion API using httpx.Client."""
        active_token = token or getattr(self, "_current_token", None)
        if not active_token and self._workspaces:
            active_token = list(self._workspaces.values())[0]
        if not active_token:
            raise ValueError("No Notion API token available")

        url = f"https://api.notion.com{path}"
        headers = {
            "Authorization": f"Bearer {active_token}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json",
        }
        with httpx.Client() as client:
            response = client.request(
                method, url, headers=headers, json=json_data, params=params
            )
            response.raise_for_status()
            return response.json()

    def _fetch_search_objects(self, token: str) -> Tuple[List[dict], List[dict]]:
        pages = []
        databases = []
        has_more = True
        next_cursor = None

        while has_more:
            json_data = {}
            if next_cursor:
                json_data["start_cursor"] = next_cursor

            res = self._request(
                method="POST",
                path="/v1/search",
                json_data=json_data,
                token=token,
            )

            results = res.get("results", [])
            for obj in results:
                obj_type = obj.get("object")
                if obj_type == "page":
                    pages.append(obj)
                elif obj_type == "database":
                    databases.append(obj)

            has_more = res.get("has_more", False)
            next_cursor = res.get("next_cursor")

        return pages, databases

    def _fetch_block_children(self, block_id: str, token: str) -> List[dict]:
        blocks = []
        has_more = True
        next_cursor = None

        while has_more:
            params = {}
            if next_cursor:
                params["start_cursor"] = next_cursor

            res = self._request(
                method="GET",
                path=f"/v1/blocks/{block_id}/children",
                params=params,
                token=token,
            )

            results = res.get("results", [])
            for block in results:
                if block.get("has_children", False):
                    block["children"] = self._fetch_block_children(block["id"], token)
                blocks.append(block)

            has_more = res.get("has_more", False)
            next_cursor = res.get("next_cursor")

        return blocks

    def _fetch_users(self, token: str) -> List[dict]:
        users = []
        has_more = True
        next_cursor = None

        while has_more:
            params = {}
            if next_cursor:
                params["start_cursor"] = next_cursor

            res = self._request(
                method="GET",
                path="/v1/users",
                params=params,
                token=token,
            )

            users.extend(res.get("results", []))
            has_more = res.get("has_more", False)
            next_cursor = res.get("next_cursor")

        return users

    def _crawl_workspace(self, workspace_name: str, token: str) -> dict:
        """Crawl the workspace for pages, databases, and users, and save to cache."""
        self._current_token = token
        try:
            pages, databases = self._fetch_search_objects(token)

            for page in pages:
                page_id = page["id"]
                page["blocks"] = self._fetch_block_children(page_id, token)

            users = self._fetch_users(token)

            structured_data = {
                "pages": pages,
                "databases": databases,
                "users": users,
            }

            # Save to cache file
            self._cache_path.parent.mkdir(parents=True, exist_ok=True)

            cache_data = {}
            if self._cache_path.is_file():
                try:
                    with open(self._cache_path, "r", encoding="utf-8") as f:
                        content = f.read().strip()
                        if content:
                            cache_data = json.loads(content)
                except Exception as e:
                    logger.error(f"Failed to load existing cache: {e}")

            cache_data[workspace_name] = structured_data

            try:
                with open(self._cache_path, "w", encoding="utf-8") as f:
                    json.dump(cache_data, f, indent=2, ensure_ascii=False)
            except Exception as e:
                logger.error(f"Failed to save cache data: {e}")

            return structured_data
        finally:
            if hasattr(self, "_current_token"):
                delattr(self, "_current_token")

    def sync(self) -> dict:
        """Sync pages and databases from connected workspaces."""
        synced_pages = 0
        for workspace_name, token in self._workspaces.items():
            res = self._crawl_workspace(workspace_name, token)
            synced_pages += len(res.get("pages", []))
        return {
            "status": "success",
            "synced_pages": synced_pages,
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
