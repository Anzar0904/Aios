# Collection Selector Architecture

This document describes target collection matching and selection weighting.

---

## 1. Domain-to-Collection Mappings

Domains map directly to Qdrant collections:
* `engineering` -> `engineering_memory`
* `workspace` -> `workspace_memory`
* `projects` -> `project_memory`
* `documentation` -> `documentation_memory`
* `conversation` -> `conversation_memory`
* `automation` -> `automation_memory`
* `provider` -> `provider_memory`
* `research` -> `research_memory`
* `knowledge` -> `knowledge_memory`

---

## 2. Selection Weighting & Extensibility

* **Weighted Recall**: Allows selecting multiple collections with different priority weights (e.g. allocating `0.8` weight to engineering and `0.2` to documentation for developer queries).
* **Future Plugins**: The select interface is modular, permitting future integration with LLM-driven classifiers or vector category index searchers.
