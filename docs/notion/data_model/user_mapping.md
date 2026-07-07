# Notion Intelligence — User Mapping Specification
**Sprint 9 · Milestone 3** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define user model conversions, user identity resolution, and metadata indexing between Notion accounts and local OS profiles.
* **Scope**: Governs user parsing rules, email lookup registries, and identity synchronization processes.
* **Audience**: Integration Developers, Systems Engineers, and AI coding agents.
* **Related Documents**:
  * [notion/capabilities.md](file:///Users/anzarakhtar/aios/docs/notion/capabilities.md) - User and permissions capabilities.
  * [notion/authentication/oauth_flow.md](file:///Users/anzarakhtar/aios/docs/notion/authentication/oauth_flow.md) - OAuth payloads and user details.

---

## 1. User Identity Mapping

When sync operations pull changes containing author fields (e.g. `created_by`, `last_edited_by` properties) or when assigning database cards (`people` properties), the AI OS resolves these identifiers using local profile mapping policies.

The system maps Notion User entities to internal **`UserProfile`** definitions (stored in `personal_profiles.json`).

```
 [Notion User JSON]
        |
        +---> Resolve via: "people.email" 
        |
        v
 [Local Profiles Lookup] ===> matches e.g. "anzarakhtar@example.com"
        |
        v
 [Internal UserProfile] (ID: anzar_akhtar_09)
```

---

## 2. Python Class Interfaces

The user mapping models live under `aios.providers.notion.models.user`:

```python
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class NotionUser:
    user_id: str
    name: str
    avatar_url: Optional[str] = None
    email: Optional[str] = None
    user_type: str = "person" # 'person' or 'bot'

    @classmethod
    def from_notion_json(cls, data: Dict[str, Any]) -> "NotionUser":
        """Convert a raw Notion user JSON block into a typed user model."""
        user_type = data.get("type", "person")
        email = None
        if user_type == "person":
            email = data.get("person", {}).get("email")

        return cls(
            user_id=data["id"],
            name=data.get("name", "Unknown User"),
            avatar_url=data.get("avatar_url"),
            email=email,
            user_type=user_type
        )
```

---

## 3. Reconciliation Workflows

When the OS processes a synced page or database row containing user parameters:
1. Extract the `user_id` from the JSON payload.
2. Check the local SQLite lookup cache: `SELECT local_profile_id FROM notion_users_reconciliation WHERE notion_user_id = ?`.
3. If not cached:
   * Query the Notion API user details endpoint: `GET https://api.notion.com/v1/users/{user_id}`.
   * Parse the user using `NotionUser.from_notion_json(...)`.
   * If the user is a `person` and has an email, look up that email inside the local `personal_profiles.json` directory.
   * Link the matching profile, and save the mapping in the SQLite reconciliation table:
     ```sql
     CREATE TABLE IF NOT EXISTS notion_users_reconciliation (
         notion_user_id TEXT PRIMARY KEY,
         local_profile_id TEXT NOT NULL,
         notion_user_email TEXT,
         resolved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
     );
     ```
4. If no email is returned or no profile matches, assign the record to the default owner account.
