# Documentation Style & Voice Guidelines
**Engineering Bible — Milestone 5**
**Version 1.0** · *Classified: For One Person Only* · *July 2026*

---

## 1. The Personal AI OS Voice

All documentation in the Personal AI OS must conform to the project's voice style (defined in [00_PROJECT_VISION.md](file:///Users/anzarakhtar/aios/docs/00_PROJECT_VISION.md)).

```
                       +-------------------------------+
                       |  THE PERSONAL AI OS VOICE    |
                       +───────────────────────────────+
                       |  DIRECT   : No filler words   |
                       |  PRECISE  : Exact terminology |
                       |  HONEST   : Clear tradeoffs   |
                       +-------------------------------+
```

---

## 2. Style Rules

### Rule 1: Direct Writing
* **No Preambles**: Eliminate conversational introductions (e.g., "In this chapter, we will discuss how service lifecycle operations are performed...").
* **Immediate Headings**: Start sections immediately with active subheadings and concise, bulleted explanations.
* **Imperative Mood**: Use direct, action-oriented descriptions for instructions (e.g., "Mock adjacent dependencies" rather than "You should try to mock adjacent dependencies").

### Rule 2: Precision
* **Exact Terminology**: Use exact names for code symbols, types, and files (e.g., using `LocalEventBus` instead of "our event handler").
* **Explicit Status Labels**: Clearly mark sections as either implemented, planned, or experimental.
* **Define Limits**: Always specify context limits, timeout durations, and memory retention sizes when documenting services.

### Rule 3: Honesty
* **Acknowledge Tradeoffs**: Document why a specific design pattern or database was selected, along with its limitations (e.g. SQLite database locks or Redis out-of-memory limits).
* **Latency Costs**: List performance costs (such as prompt formatting time overheads) and connection limits clearly.
* **Privacy & Security Boundaries**: Document where data is cached and define path limits clearly.

---

*Engineering Bible Documentation Standards · Personal AI OS · Sprint 8 M5 · Governed by [07_DOCUMENTATION_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/07_DOCUMENTATION_GUIDELINES.md)*
