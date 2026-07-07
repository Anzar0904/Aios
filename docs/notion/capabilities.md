# Notion Intelligence — Capabilities Specification
**Sprint 9 · Milestone 1 (Foundation)** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Detail the data mapping models, serialization rules, and capabilities for pages, databases, blocks, comments, users, and permissions.
* **Scope**: Dictates the parser design, AST translators, and JSON serialization schemas.
* **Audience**: Backend Developers, Integration Engineers, and AI coding agents.
* **Related Documents**:
  * [17_KNOWLEDGE_BASE.md](file:///Users/anzarakhtar/aios/docs/17_KNOWLEDGE_BASE.md) - System dictionary and data schemas.
  * [notion/architecture.md](file:///Users/anzarakhtar/aios/docs/notion/architecture.md) - Subsystem architecture.

---

## 1. Workspace Isolation & Boundaries

The AI OS interacts with Notion under strict workspace boundaries. A single Notion integration token is tied to a specific Workspace. 
* **Scoping**: The OS cannot traverse the entire workspace directory. It can only view and mutate pages and databases that the user has explicitly shared with the integration using the "Add connections" menu in Notion.
* **Metadata Tracking**:
  ```json
  {
    "workspace_id": "8f8bca12-efd8-4ba3-bfd0-cd1712a4501a",
    "workspace_name": "Personal Mind Extension",
    "bot_id": "76fa35bc-1f5e-4b62-a279-d5910faaea7b"
  }
  ```

---

## 2. Page Capabilities

Notion Pages are treated as documents. The system supports reading, creating, updating, and indexing pages.

* **Page Metadata Mapping**: Maps properties (title, icon, cover image, parents) to a local `KnowledgeDocument`.
* **Markdown Translation AST**: The AI OS converts Notion pages to Markdown files for local file indexing, and compiles Markdown files back into block payloads for updates.

```
       [Notion Page JSON]
               | (Parser)
               v
      [Block AST Hierarchy]
               | (Compiler)
               v
     [Local Markdown File]
```

---

## 3. Database Capabilities

Databases represent structured datasets. The AI OS uses Notion Databases to maintain status boards (e.g., job application tracking tables, code release checklists, review queues, automation runs).

* **Typed Schema Mapping**: The module parses Notion database schemas and maps them to Python dataclasses:

| Notion Property Type | Python Mapping | Description |
|----------------------|----------------|-------------|
| `title` | `str` | Name of the database record. |
| `rich_text` | `str` | Unstructured text properties. |
| `select` | `Enum` | Single value selection. |
| `multi_select` | `List[Enum]` | Tag arrays. |
| `date` | `datetime` / `Tuple[datetime, datetime]` | Single timestamps or start/end ranges. |
| `checkbox` | `bool` | Boolean flags (e.g. `Approved`). |
| `number` | `float` / `int` | Integer metrics or cost values. |
| `relation` | `List[str]` | References to Page IDs in other databases. |
| `people` | `List[str]` | User emails or account identifier strings. |

* **Querying & Filtering**: The OS compiles semantic search queries into Notion filters:
  ```json
  {
    "filter": {
      "and": [
        {
          "property": "Status",
          "select": { "equals": "In Progress" }
        },
        {
          "property": "Priority",
          "select": { "equals": "P0" }
        }
      ]
    }
  }
  ```

---

## 4. Block Capabilities

Notion represents page content as a tree of blocks. The `NotionProvider` compiles these blocks into a unified abstract syntax tree (AST):

* **Paragraph**: Text strings mapped to standard paragraphs.
* **Headings**: `heading_1`, `heading_2`, `heading_3` mapped to `#`, `##`, `###` Markdown tags.
* **Code Blocks**: Formatted with syntax highlighting. Synthesized from Markdown fenced code blocks:
  ```json
  {
    "type": "code",
    "code": {
      "caption": [],
      "rich_text": [{ "type": "text", "text": { "content": "print('hello')" } }],
      "language": "python"
    }
  }
  ```
* **Lists**: Bulleted lists, numbered lists, and `to_do` blocks (which map to checkboxes).
* **Callouts & Quotes**: Mapped directly to Markdown alerts (e.g., `> [!NOTE]`).

---

## 5. User Capabilities

* **Identity Reconciliation**: Maps Notion User objects to local personal profiles (`personal_profiles.json`) using email matches.
* **Task Allocation**: When assigning tasks or assigning approvals (`ApprovalEngineService`), the OS queries database `people` fields and resolves Notion user IDs.

---

## 6. Comments & Discussion Capabilities

Collaborative engineering requires comments tracking for reviews (as designed in `ReviewCollaborationService` in [17_KNOWLEDGE_BASE.md](file:///Users/anzarakhtar/aios/docs/17_KNOWLEDGE_BASE.md)).

* **Thread Retrieval**: Fetches comment threads from specific Notion pages.
* **Inline Annotations**: Inserts comments at specific block elements during code reviews.
* **Reply Synchronization**: Matches local REPL console replies to Notion threads, maintaining contextual continuity.

---

## 7. Security Permissions & Gates

To conform to the [Security Guidelines](file:///Users/anzarakhtar/aios/docs/05_SECURITY_GUIDELINES.md), the module operates under a granular permission policy:

```
                  +-----------------------------------+
                  |         Notion Query Run          |
                  +-----------------------------------+
                                    |
                                    v
                  +-----------------------------------+
                  |      Is Page ID Shared?           |
                  +-----------------------------------+
                                   / \
                                 No   Yes
                                 /     \
                                v       v
              [Access Denied Error]   [Evaluate Command Risk]
                                                 |
                                                 v
                                      [Is Mutation Operation?]
                                               / \
                                             No   Yes
                                             /     \
                                            v       v
                                    [Read Allowed] [Is Dangerous / Deletion?]
                                                         / \
                                                       No   Yes
                                                       /     \
                                                      v       v
                                              [Run Sync]   [Block for human
                                                            REPL approval]
```
* **Read Limits**: Access restricted to shared page hierarchies.
* **Write Gates**: Any mutation targeting metadata fields or parent page titles prompts a LOW risk classification (logged automatically). Destructive deletions trigger a HIGH risk classification (blocks for user approval).
