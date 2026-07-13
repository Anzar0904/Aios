import hashlib
import json
import logging
import time
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional

from aios.config import NotionConfig
from aios.services.knowledge_hub import (
    KnowledgeDocument,
    KnowledgeHubService,
    KnowledgeMetadata,
    KnowledgePage,
    KnowledgeProvider,
    KnowledgeReference,
    KnowledgeSyncResult,
)
from aios.services.personal import KnowledgeEntry, PersonalService

logger = logging.getLogger(__name__)


class NotionProvider(KnowledgeProvider):
    def __init__(self, config: NotionConfig) -> None:
        self._config = config
        self._headers = {
            "Authorization": f"Bearer {config.token or ''}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json",
        }
        self._base_url = "https://api.notion.com/v1"

    def get_name(self) -> str:
        return "notion"

    def authenticate(self) -> bool:
        if self._config.offline_mode:
            return True
        if not self._config.token:
            return False

        # Test authentication by fetching users list
        try:
            req = urllib.request.Request(
                f"{self._base_url}/users/me",
                headers=self._headers,
                method="GET"
            )
            with urllib.request.urlopen(req, timeout=self._config.timeout) as resp:
                return resp.status == 200
        except Exception as e:
            logger.error(f"Notion authentication failed: {e}")
            return False

    def discover_databases(self) -> List[Dict[str, Any]]:
        if self._config.offline_mode:
            return [{"id": "mock_db_1", "title": "Missions DB"}]

        # Discover databases via search
        payload = {
            "filter": {
                "value": "database",
                "property": "object"
            }
        }
        try:
            data = self._post("/search", payload)
            results = data.get("results", [])
            return [{"id": db.get("id"), "title": self._get_title(db)} for db in results]
        except Exception as e:
            logger.error(f"Failed to discover Notion databases: {e}")
            return []

    def discover_pages(self) -> List[KnowledgePage]:
        if self._config.offline_mode:
            return [KnowledgePage(page_id="mock_page_1", title="Default Parent Page")]

        payload = {
            "filter": {
                "value": "page",
                "property": "object"
            }
        }
        try:
            data = self._post("/search", payload)
            results = data.get("results", [])
            pages = []
            for page in results:
                pages.append(
                    KnowledgePage(
                        page_id=page.get("id"),
                        title=self._get_title(page),
                        url=page.get("url"),
                    )
                )
            return pages
        except Exception as e:
            logger.error(f"Failed to discover Notion pages: {e}")
            return []

    def search(self, query: str) -> List[KnowledgePage]:
        if self._config.offline_mode:
            return [KnowledgePage(page_id="mock_page_1", title="Mock matching page")]

        payload = {"query": query}
        try:
            data = self._post("/search", payload)
            results = data.get("results", [])
            pages = []
            for item in results:
                if item.get("object") == "page":
                    pages.append(
                        KnowledgePage(
                            page_id=item.get("id"),
                            title=self._get_title(item),
                            url=item.get("url"),
                        )
                    )
            return pages
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def read_page(self, page_id: str) -> Optional[KnowledgePage]:
        if self._config.offline_mode:
            return KnowledgePage(page_id=page_id, title="Mocked Page Content", content="Mocked Markdown Content")

        try:
            # 1. Get page details
            page_data = self._get(f"/pages/{page_id}")
            title = self._get_title(page_data)

            # 2. Get children blocks to assemble content
            blocks_data = self._get(f"/blocks/{page_id}/children")
            blocks = blocks_data.get("results", [])
            content_lines = []
            for b in blocks:
                type_ = b.get("type")
                if type_ in ["paragraph", "heading_1", "heading_2", "heading_3", "bulleted_list_item"]:
                    text = self._extract_rich_text(b.get(type_, {}).get("rich_text", []))
                    if type_ == "heading_1":
                        content_lines.append(f"# {text}")
                    elif type_ == "heading_2":
                        content_lines.append(f"## {text}")
                    elif type_ == "heading_3":
                        content_lines.append(f"### {text}")
                    elif type_ == "bulleted_list_item":
                        content_lines.append(f"- {text}")
                    else:
                        content_lines.append(text)

            return KnowledgePage(
                page_id=page_id,
                title=title,
                content="\n".join(content_lines),
                url=page_data.get("url"),
            )
        except Exception as e:
            logger.error(f"Read page failed: {e}")
            return None

    def create_page(
        self,
        parent_id: str,
        title: str,
        content: str,
        properties: Optional[Dict[str, Any]] = None,
    ) -> Optional[KnowledgePage]:
        if self._config.offline_mode:
            return KnowledgePage(page_id=f"notion_{int(time.time())}", title=title, content=content, url="http://mock-notion.com")

        # Convert markdown text content to block list
        blocks = self._markdown_to_blocks(content)

        payload = {
            "parent": {"page_id": parent_id},
            "properties": {
                "title": {
                    "title": [
                        {"text": {"content": title}}
                    ]
                }
            },
            "children": blocks,
        }

        # Override parent if parent is a database
        if properties and "database_id" in properties:
            payload["parent"] = {"database_id": properties["database_id"]}

        try:
            res = self._post("/pages", payload)
            return KnowledgePage(
                page_id=res.get("id"),
                title=title,
                url=res.get("url"),
            )
        except Exception as e:
            logger.error(f"Create page failed: {e}")
            return None

    def update_page(
        self,
        page_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        properties: Optional[Dict[str, Any]] = None,
    ) -> Optional[KnowledgePage]:
        if self._config.offline_mode:
            return KnowledgePage(page_id=page_id, title=title or "Updated Title", content=content or "Updated Content")

        try:
            # 1. Update properties (including Title)
            if title or properties:
                payload = {}
                if title:
                    payload["properties"] = {
                        "title": {
                            "title": [
                                {"text": {"content": title}}
                            ]
                        }
                    }
                self._patch(f"/pages/{page_id}", payload)

            # 2. Update content blocks if provided
            if content is not None:
                # Delete existing blocks
                existing_blocks = self._get(f"/blocks/{page_id}/children")
                for b in existing_blocks.get("results", []):
                    self._delete(f"/blocks/{b['id']}")

                # Append new blocks
                new_blocks = self._markdown_to_blocks(content)
                self._patch(f"/blocks/{page_id}/children", {"children": new_blocks})

            return self.read_page(page_id)
        except Exception as e:
            logger.error(f"Update page failed: {e}")
            return None

    # HTTP client helper methods
    def _post(self, path: str, payload: dict) -> dict:
        return self._request(path, payload, "POST")

    def _get(self, path: str) -> dict:
        return self._request(path, None, "GET")

    def _patch(self, path: str, payload: dict) -> dict:
        return self._request(path, payload, "PATCH")

    def _delete(self, path: str) -> dict:
        return self._request(path, None, "DELETE")

    def _request(self, path: str, payload: Optional[dict], method: str) -> dict:
        url = f"{self._base_url}{path}"
        data = json.dumps(payload).encode("utf-8") if payload else None

        last_err = None
        for attempt in range(self._config.retry_count):
            try:
                req = urllib.request.Request(url, headers=self._headers, data=data, method=method)
                with urllib.request.urlopen(req, timeout=self._config.timeout) as resp:
                    return json.loads(resp.read().decode("utf-8"))
            except urllib.error.HTTPError as e:
                last_err = e
                # Check for rate limiting (429) or transient server errors (5xx)
                if e.code in [429, 500, 502, 503, 504]:
                    time.sleep(1.0 * (attempt + 1))
                    continue
                raise e
            except Exception as e:
                last_err = e
                time.sleep(1.0 * (attempt + 1))
                continue
        raise last_err

    # Markdown Parser & Formatter Helpers
    def _markdown_to_blocks(self, content: str) -> List[dict]:
        blocks = []
        for line in content.split("\n"):
            line = line.strip()
            if not line:
                continue

            if line.startswith("# "):
                blocks.append(self._create_block("heading_1", line[2:]))
            elif line.startswith("## "):
                blocks.append(self._create_block("heading_2", line[3:]))
            elif line.startswith("### "):
                blocks.append(self._create_block("heading_3", line[4:]))
            elif line.startswith("- ") or line.startswith("* "):
                blocks.append(self._create_block("bulleted_list_item", line[2:]))
            else:
                blocks.append(self._create_block("paragraph", line))
        return blocks

    def _create_block(self, type_: str, text: str) -> dict:
        return {
            "object": "block",
            "type": type_,
            type_: {
                "rich_text": [
                    {"type": "text", "text": {"content": text}}
                ]
            }
        }

    def _get_title(self, page_or_db: dict) -> str:
        props = page_or_db.get("properties", {})
        title_prop = props.get("title") or props.get("Name")
        if title_prop and title_prop.get("title"):
            return self._extract_rich_text(title_prop.get("title", []))
        return page_or_db.get("title", [{"text": {"content": "Untitled"}}])[0].get("text", {}).get("content", "Untitled")

    def _extract_rich_text(self, rich_texts: List[dict]) -> str:
        return "".join(t.get("text", {}).get("content", "") for t in rich_texts)


class LocalKnowledgeHub(KnowledgeHubService):
    def __init__(self, config: NotionConfig, personal_service: PersonalService) -> None:
        self._config = config
        self._personal = personal_service
        self._providers: Dict[str, KnowledgeProvider] = {}
        self._sync_registry: Dict[str, dict] = {}

    def initialize(self) -> None:
        logger.info("Initializing LocalKnowledgeHub")

        # Instantiate and register NotionProvider
        notion_prov = NotionProvider(self._config)
        self.register_provider(notion_prov)

        # Load sync registry from personal database
        self._load_sync_registry()

    def register_provider(self, provider: KnowledgeProvider) -> None:
        self._providers[provider.get_name()] = provider
        logger.info(f"Registered Knowledge Hub provider: {provider.get_name()}")

    def get_provider(self, name: str) -> Optional[KnowledgeProvider]:
        return self._providers.get(name)

    def sync_document(self, doc: KnowledgeDocument, provider_name: str) -> KnowledgeSyncResult:
        provider = self.get_provider(provider_name)
        if not provider:
            return KnowledgeSyncResult(
                document_id=doc.document_id,
                provider=provider_name,
                status="failed",
                error_message=f"Provider {provider_name} not found"
            )

        # Calculate hash of document contents to check for updates
        content_hash = hashlib.sha256(doc.content.encode("utf-8")).hexdigest()

        # Check if already synced
        reg_entry = self._sync_registry.get(doc.document_id)
        if reg_entry:
            # If hash matches, skip sync to avoid duplicate uploads
            if reg_entry.get("content_hash") == content_hash:
                return KnowledgeSyncResult(
                    document_id=doc.document_id,
                    provider=provider_name,
                    status="skipped",
                    provider_page_id=reg_entry.get("provider_page_id")
                )

            # Update existing page
            page_id = reg_entry.get("provider_page_id")
            updated = provider.update_page(page_id, title=doc.title, content=doc.content)
            if updated:
                reg_entry["content_hash"] = content_hash
                reg_entry["version"] += 1
                reg_entry["last_modified"] = time.time()
                reg_entry["sync_status"] = "synced"
                self._save_sync_registry()

                try:
                    from aios.registry import ServiceRegistry
                    from aios.services.persistence import SemanticMemoryManager
                    registry = self._registry or ServiceRegistry._global_registry
                    if registry:
                        sem_mgr = registry.get(SemanticMemoryManager)
                        if sem_mgr:
                            text_summary = (
                                f"Notion Sync Update: [{doc.metadata.category}] Title: {doc.title}\n"
                                f"Document ID: {doc.document_id}\n"
                                f"Content:\n{doc.content}"
                            )
                            metadata = {
                                "document_id": doc.document_id,
                                "category": doc.metadata.category,
                                "timestamp": time.time(),
                                "type": "notion_sync"
                            }
                            sem_mgr.index_memory(
                                repository_name="knowledge_memory",
                                entity_id=doc.document_id,
                                text=text_summary,
                                metadata=metadata,
                                tags=["knowledge_hub", "notion_sync", doc.metadata.category]
                            )
                except Exception:
                    pass

                return KnowledgeSyncResult(
                    document_id=doc.document_id,
                    provider=provider_name,
                    status="success",
                    provider_page_id=page_id,
                    timestamp=time.time()
                )
            else:
                return KnowledgeSyncResult(
                    document_id=doc.document_id,
                    provider=provider_name,
                    status="failed",
                    error_message="Failed to update page"
                )

        # Create new page
        parent_page = self._config.default_parent_page or "mock_page_1"
        properties = {}

        # Use default database if matching category is configured
        if self._config.default_databases and doc.metadata.category in self._config.default_databases:
            db_id = self._config.default_databases[doc.metadata.category]
            properties["database_id"] = db_id

        created = provider.create_page(parent_page, doc.title, doc.content, properties)
        if created:
            self._sync_registry[doc.document_id] = {
                "provider_page_id": created.page_id,
                "content_hash": content_hash,
                "version": doc.metadata.version,
                "last_modified": time.time(),
                "sync_status": "synced",
                "category": doc.metadata.category,
            }
            self._save_sync_registry()

            # Map reference
            doc.references.append(
                KnowledgeReference(
                    reference_id=created.page_id,
                    reference_type="notion_page",
                    provider=provider_name,
                    url=created.url,
                )
            )

            try:
                from aios.registry import ServiceRegistry
                from aios.services.persistence import SemanticMemoryManager
                registry = self._registry or ServiceRegistry._global_registry
                if registry:
                    sem_mgr = registry.get(SemanticMemoryManager)
                    if sem_mgr:
                        text_summary = (
                            f"Notion Sync: [{doc.metadata.category}] Title: {doc.title}\n"
                            f"Document ID: {doc.document_id}\n"
                            f"Content:\n{doc.content}"
                        )
                        metadata = {
                            "document_id": doc.document_id,
                            "category": doc.metadata.category,
                            "timestamp": time.time(),
                            "type": "notion_sync"
                        }
                        sem_mgr.index_memory(
                            repository_name="knowledge_memory",
                            entity_id=doc.document_id,
                            text=text_summary,
                            metadata=metadata,
                            tags=["knowledge_hub", "notion_sync", doc.metadata.category]
                        )
            except Exception:
                pass

            return KnowledgeSyncResult(
                document_id=doc.document_id,
                provider=provider_name,
                status="success",
                provider_page_id=created.page_id,
                timestamp=time.time()
            )
        else:
            return KnowledgeSyncResult(
                document_id=doc.document_id,
                provider=provider_name,
                status="failed",
                error_message="Failed to create page"
            )

    def get_sync_status(self, document_id: str) -> Optional[KnowledgeMetadata]:
        entry = self._sync_registry.get(document_id)
        if not entry:
            return None
        return KnowledgeMetadata(
            unique_id=document_id,
            timestamp=entry.get("last_modified", 0.0),
            source_subsystem="knowledge_hub",
            category=entry.get("category", ""),
            version=entry.get("version", 1),
            content_hash=entry.get("content_hash", ""),
            last_modified=entry.get("last_modified", 0.0),
            provider_page_id=entry.get("provider_page_id"),
            sync_status=entry.get("sync_status", "pending"),
        )

    def _load_sync_registry(self) -> None:
        try:
            profile = self._personal.get_active_profile()
            if profile:
                for entry in profile.knowledge:
                    if entry.id == "knowledge_hub_sync_registry":
                        self._sync_registry = json.loads(entry.content)
                        break
        except Exception as e:
            logger.error(f"Failed to load sync registry: {e}")

    def _save_sync_registry(self) -> None:
        try:
            profile = self._personal.get_active_profile()
            if profile:
                new_entry = KnowledgeEntry(
                    id="knowledge_hub_sync_registry",
                    title="Knowledge Hub Sync Registry",
                    content=json.dumps(self._sync_registry),
                    tags=["system", "sync"],
                    updated_at=time.time(),
                )
                replaced = False
                for idx, entry in enumerate(profile.knowledge):
                    if entry.id == "knowledge_hub_sync_registry":
                        profile.knowledge[idx] = new_entry
                        replaced = True
                        break
                if not replaced:
                    profile.knowledge.append(new_entry)
                profile.version += 1
                self._personal.update_profile(profile.id, profile)
        except Exception as e:
            logger.error(f"Failed to save sync registry: {e}")
