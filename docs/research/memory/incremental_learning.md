# Incremental Learning & Evidence Updates Spec
**Sprint 11 · Milestone 5** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define evidence accumulation patterns, dynamic confidence boosts, and version graph updates.
* **Scope**: Governs SQL updates, confidence scaling, and database transactions.
* **Audience**: AI Prompt Engineers, Integration Engineers, and Quality Auditors.
* **Related Documents**:
  * [research/validation/confidence_scoring.md](file:///Users/anzarakhtar/aios/docs/research/validation/confidence_scoring.md) - Confidence scoring.
  * [research/memory/memory_consolidation.md](file:///Users/anzarakhtar/aios/docs/research/memory/memory_consolidation.md) - Memory consolidation.

---

## 1. Evidence Accumulation

When new research runs extract additional citations matching an existing concept, the system does not create a new `FactNode`. Instead, it uses **Incremental Learning**:
1. Locates the existing `FactNode` matching the concept name.
2. Creates a new `EvidenceNode` containing the new citation.
3. Inserts a `SUPPORTED_BY` edge in the Evidence Graph connecting the existing `FactNode` to the new `EvidenceNode`.
4. Boosts the confidence score of the fact.

---

## 2. Dynamic Confidence Boosting

The confidence score (CS) of a fact scales dynamically as additional supporting evidence is found:

$$\text{CS}_{\text{new}} = \text{CS}_{\text{old}} + (1 - \text{CS}_{\text{old}}) \times \beta \times \text{SCS}_{\text{source}}$$

* **$\beta$ (Confidence Boost Factor)**: Set to **0.15** per distinct domain source.
* **Score Ceiling**: Ensures the confidence score asymptotically approaches `1.0`, but never exceeds it.
* **Relevance Recalculation**: If the score crosses the **0.80** threshold, the fact's status changes to `VERIFIED`, and it is indexed in Qdrant for active agent use.
