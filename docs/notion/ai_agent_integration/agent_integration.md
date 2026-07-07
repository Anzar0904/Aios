# Notion Intelligence — Agent Integration Framework
**Sprint 9 · Milestone 6** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define the high-level coordination patterns, prompt injection schemas, and interfaces connecting AI OS agents to Notion data.
* **Scope**: Governs agent prompt templates, workspace tools, and routing contexts.
* **Audience**: AI Prompt Engineers, Systems Architects, and Agent Developers.
* **Related Documents**:
  * [00_PROJECT_VISION.md](file:///Users/anzarakhtar/aios/docs/00_PROJECT_VISION.md) - Project Constitution.
  * [notion/ai_agent_integration/README.md](file:///Users/anzarakhtar/aios/docs/notion/ai_agent_integration/README.md) - Integration navigation hub.

---

## 1. Agent-Workspace Interaction Paradigm

In the Personal AI OS, **agents are not autonomous actors inside the external workspace**. The local OS kernel remains the decision-making core, while agents are temporary execution threads spawned to solve specific objectives.

```
       [Notion Page Contexts]
                 | (Read)
                 v
   +---------------------------+
   |   AI OS Agent Runtime     | ===> Resolves plans via OmniRoute
   +---------------------------+
                 | (Write)
                 v
       [Remote Workspace Pages]
```

* **Notion as an Input (Context)**: Agents query the database, pull page Markdown, retrieve historical comments, and extract design specs to construct prompt contexts.
* **Notion as an Output (Target)**: Agents publish final execution logs, write reports, create database rows, and update check items.

---

## 2. Dynamic Tool Registry

Agents interact with Notion using standard provider tools registered under the **`ToolService`** (see [16_ENGINEERING_BIBLE.md](file:///Users/anzarakhtar/aios/docs/16_ENGINEERING_BIBLE.md)):

```python
class NotionAgentTools:
    @staticmethod
    def query_notion_search(query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Tool enabling agents to search active Notion workspace pages and databases."""
        return search_service.hybrid_query(query, limit=limit)

    @staticmethod
    def get_notion_document(document_id: str) -> str:
        """Tool enabling agents to fetch the parsed Markdown content of a specific page."""
        doc = knowledge_hub.pull_document(document_id)
        return doc.content

    @staticmethod
    def update_notion_row(row_id: str, properties: Dict[str, Any]) -> bool:
        """Tool enabling agents to update database row cells (e.g. status status)."""
        return database_service.update_row(row_id, properties)
```

---

## 3. Context Routing & OmniRoute Integration

To manage API latency and keep token costs low, the agent execution framework utilizes the **OmniRoute** selector (defined in [docs/04_AI_MODEL_STRATEGY.md](file:///Users/anzarakhtar/aios/docs/04_AI_MODEL_STRATEGY.md)):
1. **Analyze Scopes**: When an agent initiates a task, OmniRoute estimates the query size.
2. **Context Compression**: If retrieved Notion pages exceed the target context window, the system uses semantic search to isolate the top 3 relevant sections, filtering out boilerplate text.
3. **Route Query**: If the network is offline or `offline_mode` is set to true, OmniRoute blocks Notion API calls and routes searches to local SQLite and Qdrant replicas.
