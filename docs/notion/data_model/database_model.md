# Notion Intelligence — Database Model Specification
**Sprint 9 · Milestone 3** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define the Database schemas, column properties, database rows, and dataclass structures.
* **Scope**: Governs Python database mapping engines, tables synchronizers, and query builder interfaces.
* **Audience**: DBAs, Backend Developers, and AI coding agents.
* **Related Documents**:
  * [notion/capabilities.md](file:///Users/anzarakhtar/aios/docs/notion/capabilities.md) - Database capabilities.
  * [notion/data_model/property_mapping.md](file:///Users/anzarakhtar/aios/docs/notion/data_model/property_mapping.md) - Property translators.

---

## 1. Database Model Design

A Notion Database is represented by the `NotionDatabase` metadata definition class, while individual database pages/records are represented by the `NotionDatabaseRow` class.

Since the AI OS maps specific tables (e.g. status boards, release pipelines) to local services, the system maintains schema mappings mapping database IDs to local configurations.

---

## 2. Python Class Interfaces

The database structures live under `aios.providers.notion.models.database`:

```python
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field

@dataclass
class NotionDatabase:
    database_id: str
    workspace_id: str
    title: str
    created_at: datetime
    updated_at: datetime
    properties_schema: Dict[str, str] = field(default_factory=dict) # Property Name -> Type string (e.g. 'select', 'date')
    url: str = ""

    @classmethod
    def from_notion_json(cls, data: Dict[str, Any], workspace_id: str) -> "NotionDatabase":
        """Build database schema definition from Notion JSON metadata API payload."""
        title = "Untitled Database"
        title_list = data.get("title", [])
        if title_list:
            title = "".join([t.get("plain_text", "") for t in title_list])

        properties_schema = {}
        for prop_name, prop_desc in data.get("properties", {}).items():
            properties_schema[prop_name] = prop_desc.get("type", "rich_text")

        return cls(
            database_id=data["id"],
            workspace_id=workspace_id,
            title=title,
            created_at=datetime.fromisoformat(data["created_time"].replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(data["last_edited_time"].replace("Z", "+00:00")),
            properties_schema=properties_schema,
            url=data.get("url", "")
        )


@dataclass
class NotionDatabaseRow:
    row_id: str
    database_id: str
    created_at: datetime
    updated_at: datetime
    values: Dict[str, Any] = field(default_factory=dict) # Property Name -> Typed Value
    
    @classmethod
    def from_notion_json(cls, data: Dict[str, Any]) -> "NotionDatabaseRow":
        """Convert a database record (which is technically a page) to a row model."""
        row_id = data["id"]
        database_id = data["parent"]["database_id"]
        
        # Extracted and parsed values will be mapped using the Property Mapping Service
        values = {}
        for prop_name, prop_data in data.get("properties", {}).items():
            values[prop_name] = prop_data # Standard parser mappings apply

        return cls(
            row_id=row_id,
            database_id=database_id,
            created_at=datetime.fromisoformat(data["created_time"].replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(data["last_edited_time"].replace("Z", "+00:00")),
            values=values
        )
```

---

## 3. Bidirectional Serialization Rules

### Querying Rows (Notion -> Local)
* Use the query endpoint: `POST https://api.notion.com/v1/databases/{database_id}/query`.
* Parse each page element in the response list using `NotionDatabaseRow.from_notion_json(...)`.
* Save rows in the local SQLite table for cache storage.

### Mutating Rows (Local -> Notion)
* When creating a row or updating cell values:
  * Compile row property values into Notion’s API JSON payload.
  * Send `POST /v1/pages` (for insertions) or `PATCH /v1/pages/{row_id}` (for updates).
  * Record update confirmation hashes in local state registers.
