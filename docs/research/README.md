# Research Intelligence — Documentation Hub
**Sprint 11 · Milestone 1 (Foundation)** · Version 1.0 · July 2026

---

> [!IMPORTANT]
> This directory defines the **Research Intelligence Foundation** for the Personal AI OS.
> All documents in this section are subordinate to and derived from
> [00_PROJECT_VISION.md](file:///Users/anzarakhtar/aios/docs/00_PROJECT_VISION.md) (the OS Constitution) and 
> [16_ENGINEERING_BIBLE.md](file:///Users/anzarakhtar/aios/docs/16_ENGINEERING_BIBLE.md) (the Engineering Bible).
>
> In accordance with system guidelines, this module operates under a local-first, offline-first paradigm, keeping the AI OS kernel as the central execution and reasoning core while safely acquiring, validating, indexing, and reasoning over external technical knowledge.

---

## Purpose

`docs/research/` is the canonical home for the architectural specifications, functional capabilities, integration strategies, security models, and development roadmap of the Research Intelligence subsystem.

This subsystem provides the AI OS with a comprehensive, provider-agnostic framework to search, download, parse, validate, and reason over technical literature—including documentation, APIs, specs, RFCs, academic papers, git repositories, issue trackers, blogs, and technical forums. It enables agents to act as knowledgeable research assistants while protecting the local environment.

---

## Document Map

```
docs/research/
├── README.md                    ← This file — navigation hub
├── research_intelligence.md      ← Conceptual vision and product framework
├── architecture.md              ← Structural components, classes, and databases
├── capabilities.md              ← Source categories, validation, and reasoning maps
├── integration_strategy.md      ← Web crawlers, semantic schemas, and local caches
├── security_model.md            ← Path containment, sandbox runs, and key vaults
└── roadmap.md                   ← Sprint 11 milestones, timeline, and risk matrix
```

---

## Reading Order

| Step | Document | When to Read |
|------|----------|--------------|
| 1 | [`research_intelligence.md`](file:///Users/anzarakhtar/aios/docs/research/research_intelligence.md) | First — Establish the conceptual vision, design tenets, and system paradigms. |
| 2 | [`architecture.md`](file:///Users/anzarakhtar/aios/docs/research/architecture.md) | Before reviewing or implementing class models, crawler threads, or database tables. |
| 3 | [`capabilities.md`](file:///Users/anzarakhtar/aios/docs/research/capabilities.md) | Before writing source parsers, validation rules, or cross-referencing concepts. |
| 4 | [`integration_strategy.md`](file:///Users/anzarakhtar/aios/docs/research/integration_strategy.md) | Before coding scraping pipelines, Qdrant indexing collectors, or local memory caches. |
| 5 | [`security_model.md`](file:///Users/anzarakhtar/aios/docs/research/security_model.md) | Mandatory reading before handling tokens, writing command wrappers, or modifying networking layers. |
| 6 | [`roadmap.md`](file:///Users/anzarakhtar/aios/docs/research/roadmap.md) | To review sprint tasks, milestones, and mitigation plans. |

---

## Core System Integration

The Research Intelligence subsystem directly integrates with several existing services defined in the [Engineering Bible](file:///Users/anzarakhtar/aios/docs/16_ENGINEERING_BIBLE.md):

* **Knowledge Hub Service**: Expands the `KnowledgeHubService` to index and search external technical specifications, API structures, and RFC documents locally.
* **Tiered Memory System**: Maps parsed technical resources into local vector storage (Qdrant) inside the `research_memory` collection to enable semantic queries.
* **Action Engine & Task Executor**: Equips research agents with tools for web searching, document retrieval, and markdown formatting.
* **Notion Intelligence**: Publishes compiled research reports and structured specifications directly to Notion databases.
* **Development Workspace Intelligence**: Feeds code-level libraries dependencies research requirements into the research agent's query pipelines.
