# Consensus Analysis Spec
**Sprint 11 · Milestone 4** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define voting schema evaluations, community metric parsers, and consensus resolution loops.
* **Scope**: Governs peer evaluations, score calculations, and resolution strategies.
* **Audience**: Systems Architects, DBAs, and Lead Developers.
* **Related Documents**:
  * [research/processing/relationship_extraction.md](file:///Users/anzarakhtar/aios/docs/research/relationship_extraction.md) - Relationships.
  * [research/validation/contradiction_detection.md](file:///Users/anzarakhtar/aios/docs/research/validation/contradiction_detection.md) - Contradictions.

---

## 1. Community Consensus Scoring

When conflicts arise in developer blogs or forum discussions, the **Consensus Analysis** module evaluates community feedback to rank claims:
* **StackOverflow**: Checks if an answer is the "Accepted Answer" (boosting consensus) and parses upvote counts.
* **Reddit / forums**: Evaluates upvote ratios and developer comment feedback.
* **GitHub issues**: Counts reactions (e.g. thumbs-up, heart) on comments proposing fixes.

---

## 2. Consensus Resolution Loops

If two claims contradict:
1. **Source Category Check**: The engine prefers official specifications (`SCS = 100`) over forum answers (`SCS = 50`).
2. **Date Comparison**: If both claims are from official sources, the system prefers the newer document, assuming it reflects recent API changes.
3. **Resolve Conflict**: Update the Evidence Graph:
   * The resolved fact's status is set to `VERIFIED` (restoring its CS).
   * The rejected fact's status is set to `CONTRADICTED`, and it is excluded from agent contexts.
