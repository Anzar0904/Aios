# Roadmaps & Product Definition

> This section contains the product vision, requirements, design specifications, technology stack, and release roadmap for the Personal AI OS.

---

## Product Definition

| Document | Purpose |
|---|---|
| [PROJECT_VISION.md](PROJECT_VISION.md) | Constitutional core: what the AI OS is, why it exists, guiding philosophy |
| [PRD.md](PRD.md) | Product Requirements Document: target use cases, MVP scope, success metrics |
| [DRD.md](DRD.md) | Design Requirements Document: database structures, JSON schemas, contracts |
| [TECH_STACK.md](TECH_STACK.md) | Approved languages, external packages, and platform requirements |

## Release Planning

| Document | Purpose |
|---|---|
| [ROADMAP.md](ROADMAP.md) | Release timelines, sprint milestones, and product maturity horizons |

---

## Sprints at a Glance

| Sprint | Theme | Status |
|---|---|---|
| S0 (Architecture) | Persistence split, bootstrap modularization, repo deduplication | ✅ Complete |
| S1 (Stability) | Full test coverage, linting, type annotations | 🔄 Planned |
| S2 (Runtime) | Daemon mode, async event loop, renderer | 🔄 Planned |
| S3 (Intelligence) | Context assembly v2, retrieval pipeline optimization | 🔄 Planned |
| S4 (UX) | CLI improvements, skill discovery, onboarding | 🔄 Planned |

Detailed milestone reports are in [`docs/milestones/`](../milestones/README.md).

---

## Related Sections
- [ADRs →](../adr/README.md)
- [Architecture →](../architecture/README.md)
- [Guides →](../guides/README.md)
