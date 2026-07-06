# Fact Confidence Scoring Spec
**Sprint 11 · Milestone 4** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define confidence scoring metrics, formulas, age decay parameters, and compiler verification gates.
* **Scope**: Governs quality indices, reliability scores, and verification queues.
* **Audience**: AI Prompt Engineers, Integration Engineers, and Quality Auditors.
* **Related Documents**:
  * [research/source_discovery/source_prioritization.md](file:///Users/anzarakhtar/aios/docs/research/source_discovery/source_prioritization.md) - Prioritization.
  * [research/validation/evidence_graph.md](file:///Users/anzarakhtar/aios/docs/research/validation/evidence_graph.md) - Graph structure.

---

## 1. Fact Confidence Score (CS) Formula

The **Confidence Score (CS)** evaluates the reliability of a technical claim out of 1.0 points:

$$\text{CS} = (\text{SCS} \times 0.3) + (\text{Consensus Score} \times 0.3) + (\text{Age Decay Factor} \times 0.1) + (\text{Direct Validation} \times 0.3)$$

* **SCS (Source Credibility Score)**: The baseline credibility of the source domain (0.0 to 1.0).
* **Consensus Score**: The agreement ratio across different sources (e.g. 1.0 if multiple sources agree, 0.0 if sources contradict).
* **Age Decay Factor**: Reduces the score of older documents:
  $$\text{Decay} = e^{-\lambda \times \text{Age in Years}} \quad (\text{where } \lambda = 0.1)$$
* **Direct Validation**: Set to 1.0 if the AI OS compiles the code example or runs local tests successfully; set to 0.0 otherwise.

---

## 2. Dynamic Score Scaling

* **Verified Fact Gate**: A fact is marked as `VERIFIED` and cached in Qdrant only if its CS exceeds **0.80**.
* **Direct Testing Integration**: If an agent is uncertain about a code example in a document:
  1. Write the snippet to a temporary file.
  2. Invoke compiler tools (e.g. `poetry run python [file.py]`) within a sandboxed terminal.
  3. If execution succeeds with an exit code of `0`, set Direct Validation to `1.0`, boosting the claim's CS.
