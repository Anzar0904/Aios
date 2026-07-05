# Skills Documentation

> Skills are composable, prompt-driven capability modules that extend the AI OS. Each skill encapsulates a domain of expertise (e.g., developer tools, career coaching, research) and exposes it through structured prompts and tool integrations.

---

## Overview

| Document | Purpose |
|---|---|
| [SKILLS_OVERVIEW.md](SKILLS_OVERVIEW.md) | Complete skills registry: all available skills and their capabilities |
| [GITHUB_SKILL.md](GITHUB_SKILL.md) | GitHub skill: PR review, issue triage, branch comparison, CI analysis |
| [GITHUB_SKILL_README.md](GITHUB_SKILL_README.md) | GitHub skill implementation guide and prompt reference |

---

## Skill Categories

| Category | Location | Description |
|---|---|---|
| **Developer** | `skills/developer/` | Code review, architecture analysis, refactoring suggestions |
| **GitHub** | `skills/github/` | PR review, CI failure analysis, release notes, issue management |
| **Career** | `skills/career/` | Resume tailoring, ATS scoring, cover letter generation, interview prep |
| **Research** | `skills/research/` | Information synthesis, topic analysis, knowledge extraction |
| **Conversation** | `skills/conversation/` | Conversation history summarization |

---

## Adding a New Skill

See [Implementation Guidelines](../guides/IMPLEMENTATION_GUIDELINES.md) for the step-by-step process of creating, registering, and testing new skills.

---

## Related Sections
- [Services →](../services/README.md)
- [Guides →](../guides/README.md)
