# Multi-Source Reasoning & Facts Synthesis Spec
**Sprint 11 · Milestone 6** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define technical interfaces and logic for synthesizing claims and resolving conflicts across multiple sources.
* **Scope**: Governs semantic merges, cross-source validations, and fact resolutions.
* **Audience**: Systems Integrators, DBAs, and Lead Developers.
* **Related Documents**:
  * [research/validation/evidence_graph.md](file:///Users/anzarakhtar/aios/docs/research/validation/evidence_graph.md) - Evidence graph.
  * [research/validation/contradiction_detection.md](file:///Users/anzarakhtar/aios/docs/research/validation/contradiction_detection.md) - Contradictions.

---

## 1. Multi-Source Facts Synthesis

When compiling information on a topic, the **Multi-Source Reasoning** engine synthesizes claims from different sources to create unified Fact nodes:

```
[Source A: Blog post] ===(Claim: next is fast)===\
                                                  v
[Source B: Next Docs] ===(Claim: next uses RSC)====> [Reasoning Engine] ===> [FactNode: next uses RSC]
                                                  ^
[Source C: GitHub]    ===(Claim: next v14 released)/
```

1. **Verify Source Categories**: Prioritizes source types (Specifications > Documentation > blogs).
2. **Concept Merging**: Identifies matching concept references across sources and combines their arguments.
3. **Consolidation**: Merges redundant evidence statements into a single, cohesive fact record.

---

## 2. Resolving Contradictions

If sources provide conflicting information (e.g., parameter types differ):
1. **Analyze Conflicts**: Compiles the conflicting statements.
2. **Evaluate Trustworthiness**: Compares the credibility scores of the sources.
3. **Trigger Resolution**:
   * If one source has a significantly higher credibility score (e.g. standard spec vs blog post), it is accepted.
   * If both sources are official (e.g., v13 vs v14 documentation), the newer document is accepted, and the old fact is marked as deprecated.
   * If scores are equal, the system pauses and alerts the developer.
