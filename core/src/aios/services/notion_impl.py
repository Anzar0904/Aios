import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import httpx

from aios.services.memory import MemoryService, MemoryType
from aios.services.notion import NotionCredentialsStore, NotionService

logger = logging.getLogger(__name__)


class LocalNotionService(NotionService):
    """Stub/Mock implementation of NotionService to verify authentication and credentials store."""

    def __init__(
        self,
        model_service: Optional[Any] = None,
        credentials_path: Optional[Path] = None,
        cache_path: Optional[Path] = None,
        memory_service: Optional[MemoryService] = None,
    ) -> None:
        self._model_service = model_service
        self._credentials_store = NotionCredentialsStore(path=credentials_path)
        self._cache_path = cache_path or Path(".agent/notion/cache.json")
        self._workspaces: Dict[str, str] = {}
        self._memory_service = memory_service

    def initialize(self) -> None:
        """Initialize the service and load persisted credentials."""
        logger.info("Initializing LocalNotionService")
        self._workspaces = self._credentials_store.load_all()
        if not self._memory_service:
            from aios.registry import ServiceRegistry
            if ServiceRegistry._global_registry:
                try:
                    self._memory_service = ServiceRegistry._global_registry.get(MemoryService)
                except KeyError:
                    pass

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

    def _compile_page_text(self, page: dict) -> str:
        """Compile a unified text representation of a page."""
        # Extract title
        title = "Untitled"
        properties = page.get("properties", {})
        for _name, prop in properties.items():
            if isinstance(prop, dict) and prop.get("type") == "title":
                title_list = prop.get("title", [])
                if title_list:
                    title = "".join([
                        t.get("plain_text", t.get("text", {}).get("content", ""))
                        for t in title_list
                    ])
                    break

        # Database association
        db_association = ""
        parent = page.get("parent", {})
        if parent.get("type") == "database_id":
            db_association = f"Database: {parent.get('database_id')}"

        # Properties
        prop_lines = []
        for prop_name, prop in properties.items():
            if not isinstance(prop, dict):
                continue
            p_type = prop.get("type")
            if p_type == "title":
                continue
            
            val_str = None
            if p_type == "rich_text":
                val_str = "".join([
                    t.get("plain_text", t.get("text", {}).get("content", ""))
                    for t in prop.get("rich_text", [])
                ])
            elif p_type == "number":
                val_str = str(prop.get("number")) if prop.get("number") is not None else ""
            elif p_type == "select":
                sel = prop.get("select")
                val_str = sel.get("name") if sel else ""
            elif p_type == "multi_select":
                val_str = ", ".join([s.get("name", "") for s in prop.get("multi_select", [])])
            elif p_type == "date":
                date_val = prop.get("date")
                val_str = date_val.get("start") if date_val else ""
            elif p_type == "checkbox":
                val_str = str(prop.get("checkbox"))
            elif p_type == "url":
                val_str = prop.get("url") or ""
            elif p_type == "email":
                val_str = prop.get("email") or ""
            elif p_type == "phone_number":
                val_str = prop.get("phone_number") or ""
            
            if val_str is not None:
                prop_lines.append(f"{prop_name}: {val_str}")

        # Block content
        def extract_block_text(blocks: List[dict]) -> str:
            text_parts = []
            for block in blocks:
                b_type = block.get("type")
                if not b_type:
                    continue
                block_content = block.get(b_type)
                if isinstance(block_content, dict):
                    rich_text = block_content.get("rich_text", [])
                    if rich_text:
                        b_text = "".join([
                            t.get("plain_text", t.get("text", {}).get("content", ""))
                            for t in rich_text
                        ])
                        if b_text:
                            text_parts.append(b_text)
                
                children = block.get("children", [])
                if children:
                    c_text = extract_block_text(children)
                    if c_text:
                        text_parts.append(c_text)
            return "\n".join(text_parts)

        blocks_text = extract_block_text(page.get("blocks", []))

        # Assemble
        parts = [f"Title: {title}"]
        if db_association:
            parts.append(db_association)
        if prop_lines:
            parts.append("Properties:\n" + "\n".join(prop_lines))
        if blocks_text:
            parts.append("Content:\n" + blocks_text)

        return "\n\n".join(parts)

    def _crawl_workspace(self, workspace_name: str, token: str) -> dict:
        """Crawl the workspace for pages, databases, and users, and save to cache."""
        self._current_token = token
        
        # Load existing cache data for this workspace
        cache_data = {}
        if self._cache_path.is_file():
            try:
                with open(self._cache_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        cache_data = json.loads(content)
            except Exception as e:
                logger.error(f"Failed to load existing cache: {e}")
        
        ws_cache = cache_data.get(workspace_name, {})
        metadata = ws_cache.get("metadata", {})
        last_sync_time = metadata.get("last_sync_time") if isinstance(metadata, dict) else None
        
        cached_pages = ws_cache.get("pages", [])
        cached_pages_by_id = {p["id"]: p for p in cached_pages if isinstance(p, dict) and "id" in p}
        
        start_sync_time = datetime.now(timezone.utc).isoformat()
        
        try:
            pages, databases = self._fetch_search_objects(token)
            
            def is_modified_since(
                last_edited_str: Optional[str],
                last_sync_str: Optional[str]
            ) -> bool:
                if not last_sync_str:
                    return True
                if not last_edited_str:
                    return True
                try:
                    e_str = last_edited_str.replace("Z", "+00:00")
                    s_str = last_sync_str.replace("Z", "+00:00")
                    return datetime.fromisoformat(e_str) > datetime.fromisoformat(s_str)
                except Exception:
                    return last_edited_str > last_sync_str

            for page in pages:
                page_id = page["id"]
                cached_page = cached_pages_by_id.get(page_id)
                
                has_changed = True
                if cached_page:
                    cached_edited = cached_page.get("last_edited_time")
                    current_edited = page.get("last_edited_time")
                    if cached_edited and current_edited == cached_edited:
                        has_changed = False
                    elif last_sync_time and current_edited:
                        if not is_modified_since(current_edited, last_sync_time):
                            has_changed = False
                
                if not has_changed and cached_page:
                    page["blocks"] = cached_page.get("blocks", [])
                    if "memory_id" in cached_page:
                        page["memory_id"] = cached_page["memory_id"]
                else:
                    page["blocks"] = self._fetch_block_children(page_id, token)
                    if cached_page and "memory_id" in cached_page:
                        page["memory_id"] = cached_page["memory_id"]
                    
            users = self._fetch_users(token)
            
            # Update MemoryService
            memory_service = self._memory_service
            if not memory_service:
                from aios.registry import ServiceRegistry
                if ServiceRegistry._global_registry:
                    try:
                        memory_service = ServiceRegistry._global_registry.get(MemoryService)
                    except KeyError:
                        pass
            
            if memory_service:
                for page in pages:
                    page_id = page["id"]
                    cached_page = cached_pages_by_id.get(page_id)
                    
                    is_new = "memory_id" not in page
                    has_changed = True
                    if cached_page:
                        cached_edited = cached_page.get("last_edited_time")
                        current_edited = page.get("last_edited_time")
                        if cached_edited and current_edited == cached_edited:
                            has_changed = False
                        elif last_sync_time and current_edited:
                            if not is_modified_since(current_edited, last_sync_time):
                                has_changed = False
                                
                    if is_new or has_changed:
                        unified_text = self._compile_page_text(page)
                        if is_new:
                            mem = memory_service.add_memory(
                                content=unified_text,
                                memory_type=MemoryType.NOTE,
                                tags=["notion"],
                                metadata_additional={
                                    "page_id": page_id,
                                    "workspace_name": workspace_name
                                }
                            )
                            page["memory_id"] = mem.memory_id
                        else:
                            memory_service.update_memory(
                                memory_id=page["memory_id"],
                                content=unified_text,
                                tags=["notion"],
                                metadata_additional={
                                    "page_id": page_id,
                                    "workspace_name": workspace_name
                                }
                            )
                
                memory_service.commit()
                
            structured_data = {
                "metadata": {
                    "last_sync_time": start_sync_time
                },
                "pages": pages,
                "databases": databases,
                "users": users,
            }
            
            cache_data[workspace_name] = structured_data
            
            # Save to cache file
            self._cache_path.parent.mkdir(parents=True, exist_ok=True)
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
