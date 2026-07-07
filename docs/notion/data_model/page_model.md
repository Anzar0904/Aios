# Notion Intelligence — Page Model Specification
**Sprint 9 · Milestone 3** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define the Page data models, properties, parent mappings, and serialization rules for translating pages to internal OS models.
* **Scope**: Governs Python page classes, data builders, and `KnowledgeDocument` translation services.
* **Audience**: Backend Engineers, Systems Architects, and AI coding agents.
* **Related Documents**:
  * [17_KNOWLEDGE_BASE.md](file:///Users/anzarakhtar/aios/docs/17_KNOWLEDGE_BASE.md) - Context memory models.
  * [notion/capabilities.md](file:///Users/anzarakhtar/aios/docs/notion/capabilities.md) - Domain capabilities overview.

---

## 1. Page Model Design

In the Personal AI OS, a Notion Page is represented by the `NotionPage` class. It acts as a node within the workspace hierarchy, referencing parent pages, containing metadata properties, and linking to child blocks.

Every `NotionPage` maps directly to a local **`KnowledgeDocument`** (the system-wide schema for text and vector index inputs, defined in [17_KNOWLEDGE_BASE.md](file:///Users/anzarakhtar/aios/docs/17_KNOWLEDGE_BASE.md)).

---

## 2. Python Class Interfaces

The page definitions live under `aios.providers.notion.models.page`:

```python
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field
from aios.services.knowledge_hub import KnowledgeDocument, KnowledgeMetadata

@dataclass
class NotionPage:
    page_id: str
    workspace_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    created_by_user_id: str
    updated_by_user_id: str
    url: str
    parent_type: str  # 'workspace', 'page', or 'database'
    parent_id: Optional[str] = None
    properties: Dict[str, Any] = field(default_factory=dict)
    block_ids: List[str] = field(default_factory=list)
    local_markdown_path: Optional[str] = None

    def to_knowledge_document(self) -> KnowledgeDocument:
        """Convert this Notion page into a standard OS KnowledgeDocument."""
        metadata = KnowledgeMetadata(
            source="notion",
            external_id=self.page_id,
            workspace_id=self.workspace_id,
            parent_id=self.parent_id,
            last_modified=self.updated_at,
            custom_fields={
                "url": self.url,
                "created_by": self.created_by_user_id,
                "updated_by": self.updated_by_user_id,
                "parent_type": self.parent_type,
                **self.properties
            }
        )
        return KnowledgeDocument(
            document_id=f"notion_{self.page_id}",
            content="",  # Populated subsequently by the Block compilation service
            metadata=metadata
        )

    @classmethod
    def from_notion_json(cls, data: Dict[str, Any], workspace_id: str) -> "NotionPage":
        """Build an instance of NotionPage from the raw Notion JSON API payload."""
        properties = data.get("properties", {})
        
        # Helper to extract standard page title from page property block
        title = "Untitled"
        for prop_name, prop_val in properties.items():
            if prop_val.get("type") == "title":
                title_list = prop_val.get("title", [])
                if title_list:
                    title = "".join([t.get("plain_text", "") for t in title_list])
                break

        parent = data.get("parent", {})
        parent_type = parent.get("type", "workspace")
        parent_id = parent.get(parent_type) if parent_type != "workspace" else None

        return cls(
            page_id=data["id"],
            workspace_id=workspace_id,
            title=title,
            created_at=datetime.fromisoformat(data["created_time"].replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(data["last_edited_time"].replace("Z", "+00:00")),
            created_by_user_id=data["created_by"]["id"],
            updated_by_user_id=data["last_edited_by"]["id"],
            url=data["url"],
            parent_type=parent_type,
            parent_id=parent_id,
            properties=properties
        )
```

---

## 3. Bidirectional Serialization Rules

### Pull (Notion JSON -> Local Model)
* The `NotionProvider` calls the API client to fetch the page payload.
* The payload is passed to `NotionPage.from_notion_json(...)`.
* The local page cache is updated in SQLite, and metadata properties are flattened into dictionary fields.

### Push (Local Model -> Notion JSON)
* When updating a page title or custom fields:
  * Compile changes into Notion's property format.
  * Send a `PATCH` request to `https://api.notion.com/v1/pages/{page_id}`.
  * Update the local SQLite hashes to match the API's response.
