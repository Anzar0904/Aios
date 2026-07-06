# AI Research Orchestration Spec
**Sprint 11 · Milestone 6** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define technical interfaces and coordination loops for the AI Research Orchestration engine.
* **Scope**: Governs coordinator threads, Event Bus subscriptions, and multi-tool orchestration.
* **Audience**: Systems Architects, DBAs, and AI developers.
* **Related Documents**:
  * [research/research_intelligence.md](file:///Users/anzarakhtar/aios/docs/research/research_intelligence.md) - Conceptual vision.
  * [research/orchestration/README.md](file:///Users/anzarakhtar/aios/docs/research/orchestration/README.md) - Orchestration hub.

---

## 1. Central Director Paradigm

The **Research Orchestration** engine serves as the main coordinator of the research workspace. Instead of tools triggering web queries independently, the AI OS kernel controls all search providers, crawling queues, parsers, and validation runners.

```
                    +------------------------------------+
                    |        AI OS Kernel (Director)     |
                    +------------------------------------+
                      /         |            |         \
                     v          v            v          v
                 [Search]   [Crawler]    [Parser]   [Validator]
```

* **Coordination Loop**:
  1. **Observe**: Monitors crawler task status, document download completions, and validation errors.
  2. **Reason**: Analyzes query goals against cached technical data.
  3. **Plan**: Generates and updates research plans.
  4. **Act**: Invokes search engines, crawls pages, parses sections, and validates facts.

---

## 2. Event Bus Orchestration Signals

The coordinator publishes and subscribes to key system events:
* **`research.query_initiated`**: Published when a user sets a research goal, starting the search phase.
* **`research.document_downloaded`**: Signals that a document was successfully scraped and is ready for parsing.
* **`research.fact_verified`**: Signals that a claim has been verified and added to the core catalog.
* **`research.contradiction_detected`**: Signals a conflict in claims, triggering consensus checks.
