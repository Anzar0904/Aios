# Research Memory Guide

The Research Memory system integrates learning summaries and verified concepts with Semantic Memory (Qdrant) and the Universal Knowledge Graph.

---

## 1. Semantic Memory Indexing

When concepts are indexed:
- **Repository**: `research_memory`
- **Text format**: `"Concept: <name> - <evidence>"`
- **Tags**: `["research", "concept", "evidence"]`

---

## 2. Graph Node Synced Properties

- **RESEARCH**: `{"category": <category>, "status": <status>}`
- **PAPER**: `{"summary": <summary>}`
- **Relationships**: `CITES` and `SUPPORTS` links mapped on nodes creation.
