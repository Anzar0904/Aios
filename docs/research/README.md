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
├── roadmap.md                   ← Sprint 11 milestones, timeline, and risk matrix
├── source_discovery/            ← Milestone 2: Search discovery, sitemaps, and rate limits
├── processing/                  ← Milestone 3: Markdown conversion, NER, and relationships
├── validation/                  ... Milestone 4: SSL checks, confidence formulas, and contradictions
├── memory/                      ← Milestone 5: Lifecycles, consolidation, and Qdrant collections
├── orchestration/               ← Milestone 6: Planning DAGs, context compilation, and approvals
└── certification/               ← Milestone 7: Compliance audits and Research Health scorecard
```

---

## Reading Order

| Step | Document / Directory | When to Read |
|------|----------------------|--------------|
| 1 | [`research_intelligence.md`](file:///Users/anzarakhtar/aios/docs/research/research_intelligence.md) | First — Establish the conceptual vision, design tenets, and system paradigms. |
| 2 | [`architecture.md`](file:///Users/anzarakhtar/aios/docs/research/architecture.md) | Before reviewing or implementing class models, crawler threads, or database tables. |
| 3 | [`capabilities.md`](file:///Users/anzarakhtar/aios/docs/research/capabilities.md) | Before writing source parsers, validation rules, or cross-referencing concepts. |
| 4 | [`integration_strategy.md`](file:///Users/anzarakhtar/aios/docs/research/integration_strategy.md) | Before coding scraping pipelines, Qdrant indexing collectors, or local memory caches. |
| 5 | [`security_model.md`](file:///Users/anzarakhtar/aios/docs/research/security_model.md) | Mandatory reading before handling tokens, writing command wrappers, or modifying networking layers. |
| 6 | [`roadmap.md`](file:///Users/anzarakhtar/aios/docs/research/roadmap.md) | To review sprint tasks, milestones, and mitigation plans. |
| 7 | [Source Discovery Hub →](file:///Users/anzarakhtar/aios/docs/research/source_discovery/README.md) | To study target crawling, robots.txt compliance, and token rates. |
| 8 | [Processing Hub →](file:///Users/anzarakhtar/aios/docs/research/processing/README.md) | To study element pruners, NER tagging, and dependency mappings. |
| 9 | [Validation Hub →](file:///Users/anzarakhtar/aios/docs/research/validation/README.md) | To study SSL verifications, SSRF guards, and confidence scores. |
| 10 | [Memory Hub →](file:///Users/anzarakhtar/aios/docs/research/memory/README.md) | To study SQLite, Qdrant vectors, and Redis invalidations. |
| 11 | [Orchestration Hub →](file:///Users/anzarakhtar/aios/docs/research/orchestration/README.md) | To study planning DAGs, context loaders, and Approval constraints. |
| 12 | [Certification Hub →](file:///Users/anzarakhtar/aios/docs/research/certification/README.md) | To review compliance verification sheets and health scorecards. |

---

## Core System Integration

The Research Intelligence subsystem directly integrates with several existing services defined in the [Engineering Bible](file:///Users/anzarakhtar/aios/docs/16_ENGINEERING_BIBLE.md):

* **Knowledge Hub Service**: Expands the `KnowledgeHubService` to index and search external technical specifications, API structures, and RFC documents locally.
* **Tiered Memory System**: Maps parsed technical resources into local vector storage (Qdrant) inside the `research_memory` collection to enable semantic queries.
* **Action Engine & Task Executor**: Equips research agents with tools for web searching, document retrieval, and markdown formatting.
* **Notion Intelligence**: Publishes compiled research reports and structured specifications directly to Notion databases.
* **Development Workspace Intelligence**: Feeds code-level libraries dependencies research requirements into the research agent's query pipelines.
