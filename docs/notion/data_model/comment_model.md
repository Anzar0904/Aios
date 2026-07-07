# Notion Intelligence — Comment Model Specification
**Sprint 9 · Milestone 3** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define the Comment data models, thread representations, and conversion routines mapping to the internal collaboration review structures.
* **Scope**: Governs comment models and synchronization adapters for discussions.
* **Audience**: Backend Engineers, Systems Architects, and Integration Developers.
* **Related Documents**:
  * [17_KNOWLEDGE_BASE.md](file:///Users/anzarakhtar/aios/docs/17_KNOWLEDGE_BASE.md) - Review collaboration services definitions.
  * [notion/capabilities.md](file:///Users/anzarakhtar/aios/docs/notion/capabilities.md) - Comments capabilities mapping.

---

## 1. Comment Thread Architecture

Collaborative engineering requires comment synchronization to facilitate consensus reviews (managed by the **`ReviewCollaborationService`** as documented in [17_KNOWLEDGE_BASE.md](file:///Users/anzarakhtar/aios/docs/17_KNOWLEDGE_BASE.md)). 

```
               [Notion Page Discussion]
                   |             |
           [Comment Node A]   [Comment Node B]
                   |
           [Reply Node A1] (Nested)
```

The system maps Notion comments to internal `CommentThread` models, supporting replies and inline annotations.

---

## 2. Python Class Interfaces

The comment models live under `aios.providers.notion.models.comment`:

```python
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field

@dataclass
class NotionComment:
    comment_id: str
    parent_type: str  # 'page_id' or 'discussion_id'
    parent_id: str
    author_user_id: str
    created_at: datetime
    updated_at: datetime
    rich_text_content: str
    discussion_id: Optional[str] = None

    @classmethod
    def from_notion_json(cls, data: Dict[str, Any]) -> "NotionComment":
        """Convert a raw Notion comment JSON block into a typed comment model."""
        rich_text_list = data.get("rich_text", [])
        content = "".join([t.get("plain_text", "") for t in rich_text_list])

        parent = data.get("parent", {})
        parent_type = "page_id" if "page_id" in parent else "discussion_id"
        parent_id = parent.get(parent_type, "")

        return cls(
            comment_id=data["id"],
            parent_type=parent_type,
            parent_id=parent_id,
            author_user_id=data["created_by"]["id"],
            created_at=datetime.fromisoformat(data["created_time"].replace("Z", "+00:00")),
            updated_at=datetime.fromisoformat(data["last_edited_time"].replace("Z", "+00:00")),
            rich_text_content=content,
            discussion_id=data.get("discussion_id")
        )
```

---

## 3. Bidirectional Serialization Rules

### Pull (Notion -> Local)
* Fetch comments for a page using: `GET https://api.notion.com/v1/comments?block_id={page_id}`.
* Iterate through the results and parse them using `NotionComment.from_notion_json(...)`.
* Log these comments in the SQLite sync cache and dispatch events to the `ReviewCollaborationService`.

### Push (Local -> Notion)
* To add a comment or reply to a thread:
  * Compile the text content into a Notion comment payload.
  * Issue a `POST` request to `https://api.notion.com/v1/comments`:
    ```json
    {
      "parent": {
        "page_id": "8f8bca12-efd8-4ba3-bfd0-cd1712a4501a"
      },
      "rich_text": [
        {
          "text": {
            "content": "Approval consensus completed: Version matches criteria."
          }
        }
      ]
    }
    ```
  * Update the local database cache with the returned comment ID.
