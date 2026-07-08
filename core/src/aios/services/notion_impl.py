import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import httpx

from aios.services.memory import MemoryService, MemoryType
from aios.services.model import LLMRequest, ModelService
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
        if not self._memory_service or not self._model_service:
            from aios.registry import ServiceRegistry

            if ServiceRegistry._global_registry:
                if not self._memory_service:
                    try:
                        self._memory_service = ServiceRegistry._global_registry.get(MemoryService)
                    except KeyError:
                        pass
                if not self._model_service:
                    try:
                        self._model_service = ServiceRegistry._global_registry.get(ModelService)
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
            response = client.request(method, url, headers=headers, json=json_data, params=params)
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
                    title = "".join(
                        [
                            t.get("plain_text", t.get("text", {}).get("content", ""))
                            for t in title_list
                        ]
                    )
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
                val_str = "".join(
                    [
                        t.get("plain_text", t.get("text", {}).get("content", ""))
                        for t in prop.get("rich_text", [])
                    ]
                )
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
                        b_text = "".join(
                            [
                                t.get("plain_text", t.get("text", {}).get("content", ""))
                                for t in rich_text
                            ]
                        )
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
                last_edited_str: Optional[str], last_sync_str: Optional[str]
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
                                    "workspace_name": workspace_name,
                                },
                            )
                            page["memory_id"] = mem.memory_id
                        else:
                            memory_service.update_memory(
                                memory_id=page["memory_id"],
                                content=unified_text,
                                tags=["notion"],
                                metadata_additional={
                                    "page_id": page_id,
                                    "workspace_name": workspace_name,
                                },
                            )

                memory_service.commit()

            structured_data = {
                "metadata": {"last_sync_time": start_sync_time},
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

    def _load_cache(self) -> dict:
        if not self._cache_path or not self._cache_path.is_file():
            return {}
        try:
            with open(self._cache_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                return json.loads(content) if content else {}
        except Exception as e:
            logger.error(f"Failed to load cache: {e}")
            return {}

    def _find_page(self, page_id: str) -> Optional[Tuple[str, dict]]:
        cache = self._load_cache()
        for ws_name, ws_data in cache.items():
            pages = ws_data.get("pages", [])
            for page in pages:
                if page.get("id") == page_id:
                    return ws_name, page
        return None

    def _collect_block_types(self, blocks: List[dict]) -> List[str]:
        types = set()
        for block in blocks:
            b_type = block.get("type")
            if b_type:
                types.add(b_type)
            children = block.get("children", [])
            if children:
                types.update(self._collect_block_types(children))
        return sorted(list(types))

    def _extract_references(self, page: dict) -> Set[str]:
        referenced_ids = set()

        # 1. Extract from properties (relations)
        properties = page.get("properties", {})
        for _prop_name, prop in properties.items():
            if not isinstance(prop, dict):
                continue
            p_type = prop.get("type")
            if p_type == "relation":
                for rel in prop.get("relation", []):
                    if isinstance(rel, dict) and "id" in rel:
                        referenced_ids.add(rel["id"])
            elif p_type in ("rich_text", "title"):
                for text_item in prop.get(p_type, []):
                    if isinstance(text_item, dict) and text_item.get("type") == "mention":
                        mention = text_item.get("mention", {})
                        m_type = mention.get("type")
                        if m_type in ("page", "database") and m_type in mention:
                            referenced_ids.add(mention[m_type]["id"])

        # 2. Extract recursively from blocks
        def extract_from_blocks(blocks: List[dict]):
            for block in blocks:
                b_type = block.get("type")
                if not b_type:
                    continue
                block_content = block.get(b_type)
                if isinstance(block_content, dict):
                    rich_text = block_content.get("rich_text", [])
                    for text_item in rich_text:
                        if isinstance(text_item, dict) and text_item.get("type") == "mention":
                            mention = text_item.get("mention", {})
                            m_type = mention.get("type")
                            if m_type in ("page", "database") and m_type in mention:
                                referenced_ids.add(mention[m_type]["id"])
                children = block.get("children", [])
                if children:
                    extract_from_blocks(children)

        extract_from_blocks(page.get("blocks", []))
        return referenced_ids

    def search(self, query: str) -> list:
        """Search connected Notion workspaces for pages/databases (local cache search)."""
        cache = self._load_cache()
        results = []
        query_lower = query.lower()
        for ws_name, ws_data in cache.items():
            # Search pages
            for page in ws_data.get("pages", []):
                # Check title
                title = ""
                properties = page.get("properties", {})
                for _name, prop in properties.items():
                    if isinstance(prop, dict) and prop.get("type") == "title":
                        title_list = prop.get("title", [])
                        title = "".join([t.get("plain_text", "") for t in title_list])
                        break
                # Check unified text
                unified_text = self._compile_page_text(page)
                if query_lower in title.lower() or query_lower in unified_text.lower():
                    results.append(
                        {
                            "type": "page",
                            "id": page.get("id"),
                            "title": title,
                            "workspace": ws_name,
                            "object": page,
                        }
                    )

            # Search databases
            for db in ws_data.get("databases", []):
                # Check title
                title = ""
                title_list = db.get("title", [])
                if title_list:
                    title = "".join([t.get("plain_text", "") for t in title_list])
                if query_lower in title.lower():
                    results.append(
                        {
                            "type": "database",
                            "id": db.get("id"),
                            "title": title,
                            "workspace": ws_name,
                            "object": db,
                        }
                    )
        return results

    def explain(self, page_id: str) -> dict:
        """Describe page properties, hierarchy, and child block types."""
        res = self._find_page(page_id)
        if not res:
            raise ValueError(f"Page {page_id} not found in cache")
        ws_name, page = res

        # Get title
        title = "Untitled"
        properties = page.get("properties", {})
        for _name, prop in properties.items():
            if isinstance(prop, dict) and prop.get("type") == "title":
                title_list = prop.get("title", [])
                if title_list:
                    title = "".join(
                        [
                            t.get("plain_text", t.get("text", {}).get("content", ""))
                            for t in title_list
                        ]
                    )
                    break

        # Get hierarchy
        parent = page.get("parent", {})
        parent_type = parent.get("type", "unknown")
        parent_id = parent.get(parent_type) if parent_type != "unknown" else None

        # Get child block types
        blocks = page.get("blocks", [])
        child_types = self._collect_block_types(blocks)

        # Format properties
        formatted_props = {}
        for prop_name, prop in properties.items():
            if not isinstance(prop, dict):
                continue
            p_type = prop.get("type")
            formatted_props[prop_name] = {"type": p_type}

        return {
            "id": page_id,
            "title": title,
            "workspace": ws_name,
            "properties": formatted_props,
            "hierarchy": {"parent_type": parent_type, "parent_id": parent_id},
            "child_block_types": child_types,
        }

    def summarize(self, page_id: str) -> str:
        """Retrieve the page's block content, format it, package it inside an LLMRequest,

        and execute it using ModelService to get the summary.
        """
        res = self._find_page(page_id)
        if not res:
            raise ValueError(f"Page {page_id} not found in cache")
        ws_name, page = res

        # Get formatted page text (unified text representation)
        page_text = self._compile_page_text(page)

        # Package inside LLMRequest
        prompt = f"Please summarize the following Notion page content:\n\n{page_text}"
        request = LLMRequest(prompt=prompt)

        if self._model_service:
            response = self._model_service.execute_request(request)
            return response.content
        else:
            raise ValueError("ModelService is not available")

    def create_page(self, parent_id: str, title: str, content: str) -> dict:
        """Create a new page by making a POST request to Notion API

        and updating local cache/memory.
        """
        cache = self._load_cache()

        # 1. Determine parent type and workspace token
        parent_type = "page_id"
        workspace_name = None
        for ws_name, ws_data in cache.items():
            if any(p.get("id") == parent_id for p in ws_data.get("pages", [])):
                parent_type = "page_id"
                workspace_name = ws_name
                break
            if any(d.get("id") == parent_id for d in ws_data.get("databases", [])):
                parent_type = "database_id"
                workspace_name = ws_name
                break

        token = self._workspaces.get(workspace_name) if workspace_name else None

        # Find if parent database is in cache and check its properties
        title_prop_name = "title"
        if parent_type == "database_id" and workspace_name:
            for db in cache[workspace_name].get("databases", []):
                if db.get("id") == parent_id:
                    props = db.get("properties", {})
                    for k, v in props.items():
                        if isinstance(v, dict) and v.get("type") == "title":
                            title_prop_name = k
                            break

        properties = {title_prop_name: {"title": [{"text": {"content": title}}]}}

        children_blocks = []
        if content:
            lines = content.split("\n")
            for line in lines:
                if line.strip():
                    children_blocks.append(
                        {
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [{"type": "text", "text": {"content": line}}]
                            },
                        }
                    )

        payload = {
            "parent": {parent_type: parent_id},
            "properties": properties,
        }
        if children_blocks:
            payload["children"] = children_blocks

        # Make API Request
        res = self._request("POST", "/v1/pages", json_data=payload, token=token)

        # Add blocks to response since API creation returns metadata but not children blocks
        res_with_blocks = {**res, "blocks": children_blocks}

        # 2. Write the new page to cache and index it in MemoryService
        if not workspace_name and self._workspaces:
            workspace_name = list(self._workspaces.keys())[0]

        if workspace_name:
            cache = self._load_cache()
            ws_cache = cache.get(
                workspace_name,
                {
                    "metadata": {"last_sync_time": datetime.now(timezone.utc).isoformat()},
                    "pages": [],
                    "databases": [],
                    "users": [],
                },
            )

            memory_id = None
            if self._memory_service:
                unified_text = self._compile_page_text(res_with_blocks)
                mem = self._memory_service.add_memory(
                    content=unified_text,
                    memory_type=MemoryType.NOTE,
                    tags=["notion"],
                    metadata_additional={
                        "page_id": res_with_blocks["id"],
                        "workspace_name": workspace_name,
                    },
                )
                self._memory_service.commit()
                memory_id = mem.memory_id

            new_page = {**res_with_blocks}
            if memory_id:
                new_page["memory_id"] = memory_id

            new_ws_cache = {**ws_cache, "pages": ws_cache.get("pages", []) + [new_page]}
            new_cache = {**cache, workspace_name: new_ws_cache}

            self._cache_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self._cache_path, "w", encoding="utf-8") as f:
                json.dump(new_cache, f, indent=2, ensure_ascii=False)

            return new_page

        return res_with_blocks

    def update_page(self, page_id: str, content: str) -> dict:
        """Update existing page content by appending block children

        via Notion API and updating cache/memory.
        """
        res_find = self._find_page(page_id)
        workspace_name = None
        cached_page = None
        if res_find:
            workspace_name, cached_page = res_find

        token = self._workspaces.get(workspace_name) if workspace_name else None

        children_blocks = []
        if content:
            lines = content.split("\n")
            for line in lines:
                if line.strip():
                    children_blocks.append(
                        {
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {
                                "rich_text": [{"type": "text", "text": {"content": line}}]
                            },
                        }
                    )

        new_blocks = []
        if children_blocks:
            api_res = self._request(
                "POST",
                f"/v1/blocks/{page_id}/children",
                json_data={"children": children_blocks},
                token=token,
            )
            new_blocks = api_res.get("results", [])

        if workspace_name:
            cache = self._load_cache()
            updated_pages = []
            page_to_update = None

            for p in cache[workspace_name].get("pages", []):
                if p.get("id") == page_id:
                    page_to_update = p
                else:
                    updated_pages.append(p)

            if page_to_update is not None:
                updated_page = {
                    **page_to_update,
                    "blocks": page_to_update.get("blocks", []) + new_blocks,
                }

                if self._memory_service and "memory_id" in updated_page:
                    unified_text = self._compile_page_text(updated_page)
                    self._memory_service.update_memory(
                        memory_id=updated_page["memory_id"],
                        content=unified_text,
                        tags=["notion"],
                        metadata_additional={"page_id": page_id, "workspace_name": workspace_name},
                    )
                    self._memory_service.commit()

                updated_pages.append(updated_page)

                new_ws_cache = {**cache[workspace_name], "pages": updated_pages}
                new_cache = {**cache, workspace_name: new_ws_cache}

                with open(self._cache_path, "w", encoding="utf-8") as f:
                    json.dump(new_cache, f, indent=2, ensure_ascii=False)

        return {"id": page_id, "status": "updated", "blocks_added": len(new_blocks)}

    def list_databases(self) -> list:
        """List all accessible databases from cache."""
        cache = self._load_cache()
        databases = []
        for ws_data in cache.values():
            databases.extend(ws_data.get("databases", []))
        return databases

    def generate_graphs(self, graphs_dir: Optional[Path] = None) -> dict:
        """Traverse the cache and construct Graphviz DOT files and a Markdown summary."""
        cache = self._load_cache()

        # Ensure graphs output directory exists
        if graphs_dir is None:
            graphs_dir = Path(".agent/notion/graphs")
        graphs_dir.mkdir(parents=True, exist_ok=True)

        # 1. Gather all nodes and metadata
        workspaces = list(cache.keys())
        pages = []
        databases = []

        page_by_id = {}
        db_by_id = {}
        node_workspace = {}  # maps id -> workspace_name

        for ws_name, ws_data in cache.items():
            for p in ws_data.get("pages", []):
                p_id = p.get("id")
                if p_id:
                    pages.append(p)
                    page_by_id[p_id] = p
                    node_workspace[p_id] = ws_name

            for db in ws_data.get("databases", []):
                db_id = db.get("id")
                if db_id:
                    databases.append(db)
                    db_by_id[db_id] = db
                    node_workspace[db_id] = ws_name

        def get_page_title(p: dict) -> str:
            properties = p.get("properties", {})
            for _name, prop in properties.items():
                if isinstance(prop, dict) and prop.get("type") == "title":
                    title_list = prop.get("title", [])
                    if title_list:
                        return "".join([t.get("plain_text", "") for t in title_list])
            return "Untitled Page"

        def get_db_title(db: dict) -> str:
            title_list = db.get("title", [])
            if title_list:
                return "".join([t.get("plain_text", "") for t in title_list])
            return "Untitled Database"

        # Safe helper to escape labels
        def escape_label(label: str) -> str:
            return label.replace('"', '\\"')

        # --- Graph 1: workspace_graph.dot ---
        ws_lines = ["digraph WorkspaceGraph {", '    node [style=filled, fillcolor="#F3F4F6"];']
        for ws in workspaces:
            ws_id = f"workspace_{ws.replace(' ', '_')}"
            ws_lines.append(
                f'    {ws_id} [shape=box, fillcolor="#C7D2FE", label="Workspace: {escape_label(ws)}"];'
            )

        for p in pages:
            p_id = p["id"]
            title = get_page_title(p)
            ws_name = node_workspace.get(p_id)
            ws_node_id = f"workspace_{ws_name.replace(' ', '_')}" if ws_name else None

            ws_lines.append(
                f'    "{p_id}" [shape=ellipse, fillcolor="#E0F2FE", label="Page: {escape_label(title)}"];'
            )

            # Parent relationship
            parent = p.get("parent", {})
            p_type = parent.get("type")
            if p_type == "workspace" and ws_node_id:
                ws_lines.append(f'    {ws_node_id} -> "{p_id}";')
            elif p_type == "page_id":
                parent_id = parent.get("page_id")
                if parent_id:
                    ws_lines.append(f'    "{parent_id}" -> "{p_id}";')
            elif p_type == "database_id":
                parent_id = parent.get("database_id")
                if parent_id:
                    ws_lines.append(f'    "{parent_id}" -> "{p_id}";')

        for db in databases:
            db_id = db["id"]
            title = get_db_title(db)
            ws_name = node_workspace.get(db_id)
            ws_node_id = f"workspace_{ws_name.replace(' ', '_')}" if ws_name else None

            ws_lines.append(
                f'    "{db_id}" [shape=cylinder, fillcolor="#FEF3C7", label="DB: {escape_label(title)}"];'
            )

            # Parent relationship
            parent = db.get("parent", {})
            p_type = parent.get("type")
            if p_type == "workspace" and ws_node_id:
                ws_lines.append(f'    {ws_node_id} -> "{db_id}";')
            elif p_type == "page_id":
                parent_id = parent.get("page_id")
                if parent_id:
                    ws_lines.append(f'    "{parent_id}" -> "{db_id}";')
            elif p_type == "database_id":
                parent_id = parent.get("database_id")
                if parent_id:
                    ws_lines.append(f'    "{parent_id}" -> "{db_id}";')

        ws_lines.append("}")

        # --- Graph 2: page_relationship.dot ---
        page_lines = [
            "digraph PageRelationship {",
            '    node [shape=ellipse, style=filled, fillcolor="#E0F2FE"];',
        ]
        for p in pages:
            p_id = p["id"]
            title = get_page_title(p)
            page_lines.append(f'    "{p_id}" [label="{escape_label(title)}"];')

            # Parent relation if parent is page
            parent = p.get("parent", {})
            if parent.get("type") == "page_id":
                parent_id = parent.get("page_id")
                page_lines.append(f'    "{parent_id}" -> "{p_id}" [label="parent-child"];')

            # References/Mentions
            refs = self._extract_references(p)
            for ref_id in refs:
                if ref_id in page_by_id:
                    page_lines.append(f'    "{p_id}" -> "{ref_id}" [label="mentions"];')
        page_lines.append("}")

        # --- Graph 3: database_relationship.dot ---
        db_lines = ["digraph DatabaseRelationship {", "    node [style=filled];"]
        for db in databases:
            db_id = db["id"]
            title = get_db_title(db)
            db_lines.append(
                f'    "{db_id}" [shape=cylinder, fillcolor="#FEF3C7", label="{escape_label(title)}"];'
            )

        for p in pages:
            p_id = p["id"]
            title = get_page_title(p)
            db_lines.append(
                f'    "{p_id}" [shape=ellipse, fillcolor="#E0F2FE", label="{escape_label(title)}"];'
            )

            # Database parent
            parent = p.get("parent", {})
            if parent.get("type") == "database_id":
                parent_id = parent.get("database_id")
                db_lines.append(f'    "{parent_id}" -> "{p_id}" [label="contains"];')

            refs = self._extract_references(p)
            for ref_id in refs:
                if ref_id in db_by_id:
                    db_lines.append(f'    "{p_id}" -> "{ref_id}" [label="refers"];')
                elif ref_id in page_by_id:
                    db_lines.append(f'    "{p_id}" -> "{ref_id}" [label="mentions"];')
        db_lines.append("}")

        # --- Graph 4: sync_dependency.dot ---
        sync_lines = ["digraph SyncDependency {", '    node [style=filled, fillcolor="#F3F4F6"];']

        for ws in workspaces:
            ws_id = f"workspace_{ws.replace(' ', '_')}"
            sync_lines.append(
                f'    {ws_id} [shape=box, fillcolor="#C7D2FE", label="Workspace: {escape_label(ws)}"];'
            )

        for p in pages:
            p_id = p["id"]
            title = get_page_title(p)
            sync_lines.append(
                f'    "{p_id}" [shape=ellipse, fillcolor="#E0F2FE", label="{escape_label(title)}"];'
            )

            parent = p.get("parent", {})
            p_type = parent.get("type")
            if p_type == "workspace":
                ws_id = f"workspace_{node_workspace.get(p_id, '').replace(' ', '_')}"
                sync_lines.append(f'    {ws_id} -> "{p_id}" [label="syncs"];')
            elif p_type == "page_id":
                parent_id = parent.get("page_id")
                sync_lines.append(f'    "{parent_id}" -> "{p_id}" [label="parent"];')
            elif p_type == "database_id":
                parent_id = parent.get("database_id")
                sync_lines.append(f'    "{parent_id}" -> "{p_id}" [label="member"];')

            refs = self._extract_references(p)
            for ref_id in refs:
                if ref_id in page_by_id or ref_id in db_by_id:
                    sync_lines.append(f'    "{p_id}" -> "{ref_id}" [label="depends"];')

        for db in databases:
            db_id = db["id"]
            title = get_db_title(db)
            sync_lines.append(
                f'    "{db_id}" [shape=cylinder, fillcolor="#FEF3C7", label="{escape_label(title)}"];'
            )

            parent = db.get("parent", {})
            p_type = parent.get("type")
            if p_type == "workspace":
                ws_id = f"workspace_{node_workspace.get(db_id, '').replace(' ', '_')}"
                sync_lines.append(f'    {ws_id} -> "{db_id}" [label="syncs"];')
            elif p_type == "page_id":
                parent_id = parent.get("page_id")
                sync_lines.append(f'    "{parent_id}" -> "{db_id}" [label="parent"];')

        sync_lines.append("}")

        # Save dot files
        files_written = {}
        for filename, lines in [
            ("workspace_graph.dot", ws_lines),
            ("page_relationship.dot", page_lines),
            ("database_relationship.dot", db_lines),
            ("sync_dependency.dot", sync_lines),
        ]:
            filepath = graphs_dir / filename
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("\n".join(lines) + "\n")
            files_written[filename] = str(filepath)

        # Write notion_graphs.md summarizing relationships with inline Mermaid graphs
        md_lines = [
            "# Notion Workspace Relationships Summary",
            "",
            "This file summarizes the relationships between workspaces, databases, and pages discovered in your Notion account.",
            "",
            "## Workspaces and Hierarchy",
            "The following Mermaid diagram shows the hierarchy of workspaces, databases, and pages:",
            "```mermaid",
            "graph TD",
        ]

        for ws in workspaces:
            ws_clean = ws.replace(" ", "_")
            md_lines.append(f'    workspace_{ws_clean}["Workspace: {ws}"]')

        for p in pages:
            p_id = p["id"]
            title = get_page_title(p)
            md_lines.append(f'    p_{p_id.replace("-", "_")}["Page: {title}"]')

            parent = p.get("parent", {})
            p_type = parent.get("type")
            if p_type == "workspace":
                ws_clean = node_workspace.get(p_id, "").replace(" ", "_")
                md_lines.append(f"    workspace_{ws_clean} --> p_{p_id.replace('-', '_')}")
            elif p_type == "page_id":
                parent_id = parent.get("page_id")
                md_lines.append(
                    f"    p_{parent_id.replace('-', '_')} --> p_{p_id.replace('-', '_')}"
                )
            elif p_type == "database_id":
                parent_id = parent.get("database_id")
                md_lines.append(
                    f"    db_{parent_id.replace('-', '_')} --> p_{p_id.replace('-', '_')}"
                )

        for db in databases:
            db_id = db["id"]
            title = get_db_title(db)
            md_lines.append(f'    db_{db_id.replace("-", "_")}["Database: {title}"]')

            parent = db.get("parent", {})
            p_type = parent.get("type")
            if p_type == "workspace":
                ws_clean = node_workspace.get(db_id, "").replace(" ", "_")
                md_lines.append(f"    workspace_{ws_clean} --> db_{db_id.replace('-', '_')}")
            elif p_type == "page_id":
                parent_id = parent.get("page_id")
                md_lines.append(
                    f"    p_{parent_id.replace('-', '_')} --> db_{db_id.replace('-', '_')}"
                )

        md_lines.extend(
            [
                "```",
                "",
                "## Page Mentions & Relations",
                "This shows the cross-references and relations between pages and databases:",
                "```mermaid",
                "graph LR",
            ]
        )

        has_ref = False
        for p in pages:
            p_id = p["id"]
            p_clean = p_id.replace("-", "_")
            refs = self._extract_references(p)
            for ref_id in refs:
                ref_clean = ref_id.replace("-", "_")
                if ref_id in page_by_id:
                    md_lines.append(f"    p_{p_clean} -->|mentions| p_{ref_clean}")
                    has_ref = True
                elif ref_id in db_by_id:
                    md_lines.append(f"    p_{p_clean} -->|references| db_{ref_clean}")
                    has_ref = True
        if not has_ref:
            md_lines.append("    %% No cross-references found")

        md_lines.extend(
            [
                "```",
                "",
                "## Exported Files",
                "The following Graphviz DOT files have been generated:",
            ]
        )
        for filename, filepath in files_written.items():
            md_lines.append(f"- [{filename}](file://{filepath})")

        md_filepath = graphs_dir / "notion_graphs.md"
        with open(md_filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(md_lines) + "\n")

        files_written["notion_graphs.md"] = str(md_filepath)

        return {"status": "success", "graphs_dir": str(graphs_dir), "files": files_written}
