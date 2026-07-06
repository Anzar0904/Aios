# Documentation Standards
**Engineering Bible — Milestone 5**
**Version 1.0** · *Classified: For One Person Only* · *July 2026*

> [!IMPORTANT]
> This directory defines the **Documentation Standards** of the Personal AI OS.
> It outlines the layout rules, writing voice, API structures, diagram guidelines, and auto-generation processes.
> If any rule here conflicts with the Engineering Bible Foundation layer, the Foundation wins.

---

## Purpose

`docs/engineering/documentation_standards/` establishes the rules, templates, and style guides to ensure that documentation remains clear, accurate, and synchronized with code changes. It answers:

> **How must I write, structure, format, and generate documentation in this system?**

Every developer and AI agent must adhere to these guidelines to prevent documentation decay.

---

## Document Map

```
docs/engineering/documentation_standards/
├── README.md                  ← This file — navigation hub
├── documentation_standards.md ← Core playbook, document taxonomy, and sync rules
├── markdown_guidelines.md     ← Markdown syntax, metadata blocks, and link rules
├── api_documentation.md       ← Google-style docstrings, type hints, and templates
├── architecture_documentation.md ← ADR templates, design logs, and cross-references
├── generated_documentation.md ← Auto-generators, link checkers, and verification
├── diagram_standards.md       ← Mermaid diagram rules, flowcharting, and sequence structures
└── writing_guidelines.md      ← Voice guidelines, direct writing, and clarity rules
```

---

## Reading Order

| Step | Document | When to Read |
|------|----------|--------------|
| 1 | [documentation_standards.md](documentation_standards.md) | First — to understand the taxonomy and sync requirements |
| 2 | [markdown_guidelines.md](markdown_guidelines.md) | Before writing or editing any markdown file |
| 3 | [writing_guidelines.md](writing_guidelines.md) | Before editing technical documentation text |
| 4 | [api_documentation.md](api_documentation.md) | Before writing Python docstrings or type annotations |
| 5 | [diagram_standards.md](diagram_standards.md) | Before designing flowcharts or sequence diagrams |
| 6 | [architecture_documentation.md](architecture_documentation.md) | Before drafting ADRs or system design manuals |
| 7 | [generated_documentation.md](generated_documentation.md) | To audit lint compliance or run build tools |

---

## Quick Reference — Documentation Constraints

These rules are checked during pre-release and doc-build sweeps:

| Metric / Rule | Requirement | Reference Document |
|---------------|-------------|--------------------|
| **Metadata Block** | Mandatory header at the beginning of all `.md` files | [markdown_guidelines.md](markdown_guidelines.md) |
| **Link Schema** | Explicit file paths using the `file:///` scheme | [markdown_guidelines.md](markdown_guidelines.md) |
| **Hyperlinks** | Do not wrap link text in backticks | [markdown_guidelines.md](markdown_guidelines.md) |
| **Docstrings** | Google-style docstrings on all public classes and methods | [api_documentation.md](api_documentation.md) |
| **Type Hints** | 100% type annotation coverage for public methods | [api_documentation.md](api_documentation.md) |
| **Mermaid Syntax** | Node labels with special characters must be quoted | [diagram_standards.md](diagram_standards.md) |
| **Voice Style** | Direct, Precise, and Honest | [writing_guidelines.md](writing_guidelines.md) |
| **Doc Synchronization** | Documentation edits must be checked in with code changes | [documentation_standards.md](documentation_standards.md) |

---

## Relationship to the Engineering Bible Foundation

```
docs/engineering/               ← Foundation (Milestone 1)
     │
     ├── testing_standards/     ← Testing Standards (Milestone 4)
     │
     └── documentation_standards/ ← YOU ARE HERE (Milestone 5)
              │
              ├── Implements ──▶  engineering_principles.md §2.3 (Transparency)
              ├── Enforces   ──▶  07_DOCUMENTATION_GUIDELINES.md (markdown rules)
              └── Validates  ──▶  01_ENGINEERING_GUIDELINES.md (DoD completeness)
```

---

*Engineering Bible Documentation Standards · Personal AI OS · Sprint 8 M5 · Governed by [07_DOCUMENTATION_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/07_DOCUMENTATION_GUIDELINES.md)*
