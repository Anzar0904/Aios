# Knowledge Validation & Evidence Graph — Navigation Hub
**Sprint 11 · Milestone 4** · Version 1.0 · July 2026

---

> [!IMPORTANT]
> This directory houses the **Knowledge Validation & Evidence Graph** specifications for the Personal AI OS.
> It builds upon the [Research Foundation](file:///Users/anzarakhtar/aios/docs/research/README.md), [Source Discovery](file:///Users/anzarakhtar/aios/docs/research/source_discovery/README.md), and [Research Processing](file:///Users/anzarakhtar/aios/docs/research/processing/README.md) specifications.
>
> In accordance with local-first system design guidelines, all evidence mapping, credibility scoring, contradiction detections, consensus evaluations, citation tracking, and versionings are processed locally, utilizing PostgreSQL database backends, Qdrant semantic indices, and Redis caches.

---

## Documents

| Document | Purpose |
|---|---|
| [evidence_graph.md](file:///Users/anzarakhtar/aios/docs/research/validation/evidence_graph.md) | The directed graph schema representing the hierarchy: KnowledgeNode → Fact → Evidence → Confidence → Version |
| [source_validation.md](file:///Users/anzarakhtar/aios/docs/research/validation/source_validation.md) | Domain security checks, SSL certificates verification, and author reputation lints |
| [confidence_scoring.md](file:///Users/anzarakhtar/aios/docs/research/validation/confidence_scoring.md) | Formulating the Confidence Score (CS) based on credibility, age decay, and compiler validation |
| [contradiction_detection.md](file:///Users/anzarakhtar/aios/docs/research/validation/contradiction_detection.md) | Cross-reference scanners detecting conflicting technical claims and triggering REPL alerts |
| [consensus_analysis.md](file:///Users/anzarakhtar/aios/docs/research/validation/consensus_analysis.md) | Evaluating voting schemas, accepted forum answers, and community consensus indexes |
| [citation_management.md](file:///Users/anzarakhtar/aios/docs/research/validation/citation_management.md) | Mapping facts to evidence targets, document snippets, and section line coordinates |
| [knowledge_versioning.md](file:///Users/anzarakhtar/aios/docs/research/validation/knowledge_versioning.md) | Storing version logs, tracking updates, and marking deprecated statements as stale |

---

## Reading Order

1. **[`evidence_graph.md`](file:///Users/anzarakhtar/aios/docs/research/validation/evidence_graph.md)**: Start here to understand the core evidence model.
2. **[`source_validation.md`](file:///Users/anzarakhtar/aios/docs/research/validation/source_validation.md)**: Learn how source files are vetted before parsing.
3. **[`confidence_scoring.md`](file:///Users/anzarakhtar/aios/docs/research/validation/confidence_scoring.md)**: Explore calculations determining fact reliability.
4. **[`contradiction_detection.md`](file:///Users/anzarakhtar/aios/docs/research/validation/contradiction_detection.md)** & **[`consensus_analysis.md`](file:///Users/anzarakhtar/aios/docs/research/validation/consensus_analysis.md)**: Review how conflicts are detected and consensus is reached.
5. **[`citation_management.md`](file:///Users/anzarakhtar/aios/docs/research/validation/citation_management.md)** & **[`knowledge_versioning.md`](file:///Users/anzarakhtar/aios/docs/research/validation/knowledge_versioning.md)**: Read about source citations and knowledge version histories.
