# Documentation Playbook & Taxonomy Standards
**Engineering Bible — Milestone 5**
**Version 1.0** · *Classified: For One Person Only* · *July 2026*

---

## 1. Documentation Philosophy: Documentation as Code

In the Personal AI OS, documentation is treated as code. Because the codebase is modified across disconnected chat sessions by various AI agents, out-of-date or incorrect documentation acts as a source of system bugs and architectural drift.

### Core Documentation Principles
1. **Single Source of Truth**: Each document has exactly one responsibility. Redundant explanations of service behaviors are prohibited.
2. **Precision for Both Humans and AI**: Document details must be organized using structured terminology, explicit file links, and tabular summaries to make them easy for both human owners and AI contexts to parse.
3. **Simultaneous Lifecycle Updates**: A code modification is not complete until its corresponding documentation files, change lists, and inline docstrings are updated in the same commit.

---

## 2. Document Taxonomy

Documentation is divided into five distinct tiers based on stability and responsibility:

| Tier | Category | Stability | Purpose | Reference Files |
|------|----------|-----------|---------|-----------------|
| 1 | **Constitutional Core** | Permanent | Defines core vision, values, and constraints. | `00_PROJECT_VISION.md` |
| 2 | **System Guidelines** | High | Defines standards for coding, security, and testing. | `docs/engineering/` |
| 3 | **PM Specifications** | Medium | Defines roadmaps, requirements, and designs. | `09_ROADMAP.md`, `12_PRD.md` |
| 4 | **Technical Manuals** | Variable | Documents low-level code architecture and execution flows. | `16_ENGINEERING_BIBLE.md` |
| 5 | **Dynamic Logs** | Append-Only | Documents design logs and user decisions. | `10_DECISION_LOG.md` |

---

## 3. Synchronization Policy

To prevent documentation drift during active development:
* **The Atomic Commit Rule**: If a code change modifies an interface, creates a database repository, or deprecates a command, the corresponding documentation files (such as `16_ENGINEERING_BIBLE.md` or a skill `README.md`) must be updated in the same commit.
* **Deprecation Notice**: No public interface, service method, or command can be removed without first being flagged as deprecated in the codebase and documented as such in the release logs.
* **Pre-commit Audits**: Verification checks must verify that all links are valid and that metadata headers are present on all modified files.

---

*Engineering Bible Documentation Standards · Personal AI OS · Sprint 8 M5 · Governed by [07_DOCUMENTATION_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/07_DOCUMENTATION_GUIDELINES.md)*
