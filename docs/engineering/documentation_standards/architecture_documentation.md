# Architecture Documentation & ADR Standards
**Engineering Bible — Milestone 5**
**Version 1.0** · *Classified: For One Person Only* · *July 2026*

---

## 1. Architectural Decision Records (ADRs)

Major architectural changes, library integrations, or pattern deviations must be recorded as **Architectural Decision Records (ADRs)** inside the [docs/adr/](file:///Users/anzarakhtar/aios/docs/adr/) directory (or logged directly under `10_DECISION_LOG.md`).

### ADR Document Schema
Every ADR must include the following sections:
1. **Title**: Structured as `ADR-[Number]: [Descriptive Title]` (e.g. `ADR-0004: Redis Session Storage`).
2. **Status**: Must be one of `Proposed`, `Accepted`, `Rejected`, or `Superseded` (referencing the replacing ADR).
3. **Context**: Explains the technical challenge, constraints, and requirements.
4. **Decision**: Clearly describes the selected solution and implementation approach.
5. **Consequences**: Outlines tradeoffs, performance impacts, and changes to system dependencies.

---

## 2. Design Documentation Guidelines

System design documents explain structural relationships and flow sequences:
* **Subsystem Boundaries**: Map interfaces, concrete classes, and config parameters to their respective architectural layers (UI, Kernel, Services, Engines, Plugins).
* **Data Flow Diagrams**: Detail execution flows (like user queries, tool invocations, or DB writes) using Mermaid sequence charts.
* **Class Schemas**: Document relational database tables, vector metadata keys, and event dataclass schemas.

---

## 3. Cross-Referencing Design Files

To maintain consistency and prevent duplicate content:
* **System Design**: Refer to [15_SYSTEM_DESIGN.md](file:///Users/anzarakhtar/aios/docs/15_SYSTEM_DESIGN.md) for sequence diagrams and system wiring maps.
* **Architecture Rules**: Cross-reference [02_ARCHITECTURE_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/02_ARCHITECTURE_GUIDELINES.md) when describing dependency injection boundaries, service contracts, and kernel state details.

---

*Engineering Bible Documentation Standards · Personal AI OS · Sprint 8 M5 · Governed by [07_DOCUMENTATION_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/07_DOCUMENTATION_GUIDELINES.md)*
