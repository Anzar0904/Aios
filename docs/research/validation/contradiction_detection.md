# Contradiction Detection Spec
**Sprint 11 · Milestone 4** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define collision checking algorithms, text contradiction parsing, and alert triggers.
* **Scope**: Governs semantic comparison loops, conflict checkers, and warning engines.
* **Audience**: DBAs, Backend Developers, and System Architects.
* **Related Documents**:
  * [research/processing/relationship_extraction.md](file:///Users/anzarakhtar/aios/docs/research/relationship_extraction.md) - Relationships mappings.
  * [research/validation/confidence_scoring.md](file:///Users/anzarakhtar/aios/docs/research/validation/confidence_scoring.md) - Confidence scores.

---

## 1. Cross-Reference Contradiction Scanner

When new concepts and evidence statements are indexed, the **Contradiction Detection** engine scans local databases to locate conflicting claims:

```
[New Evidence Indexed]
          |
          v
[Search Local Database] ===> Find existing facts matching concept name
          |
          v
[Semantic Contrast Check] ===> Compare statements using contrast models
          |
          +--- Conflicting statement found (e.g. Parameter Y is deprecated vs required)
          |
          v
[Register CONTRADICTS Edge] ===> Link conflicting FactNodes
          |
          v
[Trigger Contradiction Alert] ===> Print warning in REPL console
```

---

## 2. Collision Warning Logs

When a contradiction is detected:
1. Link the conflicting `FactNodes` using a `CONTRADICTS` edge in the Evidence Graph.
2. Reduce the confidence scores of both facts until the conflict is resolved.
3. Print a warning in the REPL console:
   ```
   [Research Contradiction Warning]
   Conflicting claims detected for concept 'Notion API Page Creation':
   - Source A (rfc-editor.org): "Parent ID is a required string parameter."
   - Source B (developer.notion.com): "Parent ID can be omitted if workspace root is set."
   Resolving conflict using consensus analysis...
   ```
