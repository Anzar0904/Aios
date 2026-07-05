# Development Guides

> This section contains all engineering guidelines, standards, and how-to guides for contributors (human or AI) working on the Personal AI OS.

---

## Start Here

| Document | Audience | Purpose |
|---|---|---|
| [CONTRIBUTING.md](CONTRIBUTING.md) | All contributors | Setup, branching, commit conventions, AI-authored commit tagging |
| [ENGINEERING_CONSTITUTION.md](ENGINEERING_CONSTITUTION.md) | All contributors | Non-negotiable engineering principles and philosophy |
| [ENGINEERING_GUIDELINES.md](ENGINEERING_GUIDELINES.md) | Engineers | Core principles: boring by default, optimize for deletion, SRP |

## Engineering Standards

| Document | Purpose |
|---|---|
| [CODING_STANDARDS.md](CODING_STANDARDS.md) | Style rules, file line limits (max 400 lines), complexity budgets |
| [DOCUMENTATION_GUIDELINES.md](DOCUMENTATION_GUIDELINES.md) | Markdown formatting, metadata blocks, and docstring standards |
| [TESTING_GUIDELINES.md](TESTING_GUIDELINES.md) | Unit, integration, contract, and regression testing standards |
| [SECURITY_GUIDELINES.md](SECURITY_GUIDELINES.md) | Secrets handling, encryption at rest/in transit, risk gates |

## Implementation Guides

| Document | Purpose |
|---|---|
| [IMPLEMENTATION_GUIDELINES.md](IMPLEMENTATION_GUIDELINES.md) | How to implement new skills, write tools, register commands |
| [AI_MODEL_STRATEGY.md](AI_MODEL_STRATEGY.md) | Model selection matrices, offline runtimes, fallback chains |
| [ENGINEERING_BIBLE.md](ENGINEERING_BIBLE.md) | Low-level file execution map and CLI REPL mechanics |

---

## Quick Reference

- **New skill?** → [IMPLEMENTATION_GUIDELINES.md](IMPLEMENTATION_GUIDELINES.md)
- **Commit conventions?** → [CONTRIBUTING.md](CONTRIBUTING.md)
- **Line length limit?** → 400 lines max per file ([CODING_STANDARDS.md](CODING_STANDARDS.md))
- **Testing policy?** → [TESTING_GUIDELINES.md](TESTING_GUIDELINES.md)
- **Adding a secret?** → [SECURITY_GUIDELINES.md](SECURITY_GUIDELINES.md)

---

## Related Sections
- [Architecture →](../architecture/README.md)
- [Skills →](../skills/README.md)
- [ADRs →](../adr/README.md)
