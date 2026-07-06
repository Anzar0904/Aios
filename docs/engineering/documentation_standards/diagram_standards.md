# Mermaid Diagram Conventions
**Engineering Bible — Milestone 5**
**Version 1.0** · *Classified: For One Person Only* · *July 2026*

---

## 1. Allowed Diagram Categories

To visualize system behaviors, the Personal AI OS uses three types of Mermaid diagrams:

* **Flowcharts (`graph TD` or `graph LR`)**: Map logical pathways, lifecycle state loops, and directory dependencies.
* **Sequence Diagrams (`sequenceDiagram`)**: Map chronological request execution flows, event messaging, and cross-service calls.
* **State Diagrams (`stateDiagram-v2`)**: Map state machine transitions (e.g. Kernel states, session statuses, or task execution states).

---

## 2. Mermaid Syntax Conventions & Guards

Mermaid diagrams must be written carefully to prevent rendering errors in markdown viewers:

* **Quote Special Characters**: Node labels containing brackets, parentheses, colons, or punctuation must be wrapped in double quotes.
  
  * *Correct*: `A["Init Service (LocalEventBus)"]`
  * *Incorrect*: `A[Init Service (LocalEventBus)]` (causes parsing errors)

* **No Inline HTML**: Do not use raw HTML tags (like `<br>` or `<b>`) inside node labels. Use standard string formats instead.
* **Diagram Keywords Capitalization**: Mermaid structural keywords must use camelCase or exact casing as specified by the standard:
  * `sequenceDiagram`
  * `stateDiagram-v2`
  * `graph TD` or `graph LR`
  * `loop`, `end`, `alt`, `opt` (lowercase for control structures)

---

## 3. Styling & Structural Consistency

* **Actor Labeling**: In sequence diagrams, keep participant labels concise (e.g., using short labels like `actor User as CLI User` and `participant Bus as LocalEventBus`).
* **Autonumbering**: Always enable autonumbering at the beginning of sequence diagrams using the `autonumber` keyword.
* **Direction Consistency**: Flowcharts should default to Top-to-Bottom (`TD`) or Left-to-Right (`LR`) layouts to keep them readable.

---

*Engineering Bible Documentation Standards · Personal AI OS · Sprint 8 M5 · Governed by [07_DOCUMENTATION_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/07_DOCUMENTATION_GUIDELINES.md)*
