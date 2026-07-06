# Engineering Bible — Foundation
**Sprint 8 · Milestones 1, 2, 3, 4, 5, 6 & 7** · Version 1.0 · July 2026

> [!IMPORTANT]
> This directory is the **Engineering Bible Foundation** for the Personal AI OS.
> Every document here is subordinate to and derived from
> [00_PROJECT_VISION.md](file:///Users/anzarakhtar/aios/docs/00_PROJECT_VISION.md) — the project's constitutional root.
> If any statement in this directory appears to conflict with the Constitution, the Constitution wins.

---

## Purpose

`docs/engineering/` is the canonical home for the foundational engineering identity of the Personal AI OS.
It answers **four questions** that every contributor — human or AI — must be able to answer before touching the codebase:

1. **Why does this system exist, and what is it trying to become?** → [`vision.md`](vision.md)
2. **How do we think about building software here?** → [`philosophy.md`](philosophy.md)
3. **What concrete rules govern every line of code we write?** → [`engineering_principles.md`](engineering_principles.md)
4. **What design properties must the system always preserve?** → [`design_goals.md`](design_goals.md)
5. **What ethical lines must never be crossed?** → [`engineering_ethics.md`](engineering_ethics.md)

---

## Document Map

```
docs/engineering/
├── README.md                  ← This file — navigation hub
├── vision.md                  ← 10-year trajectory, mission, success horizon
├── philosophy.md              ← Three Foundational Beliefs + Guiding Principles
├── engineering_principles.md  ← Five operational engineering laws
├── design_goals.md            ← Non-negotiable system design properties
├── engineering_ethics.md      ← Ethical constraints binding all contributors
├── coding_standards/          ← Sprint 8 M2 — Coding Standards
│   ├── README.md              ← Coding standards navigation hub
│   ├── python_standards.md    ← Formatting, type hints, docstrings, budgets
│   ├── naming_conventions.md  ← Identifier naming for every entity type
│   ├── project_structure.md   ← Directory layout, nesting limits, file placement
│   ├── import_rules.md        ← Import ordering, boundary enforcement
│   ├── dependency_rules.md    ← Dependency admission and pinning policy
│   ├── error_handling.md      ← Exception design, propagation, timeouts
│   └── logging_standards.md   ← Logger acquisition, levels, redaction
├── architecture_standards/    ← Sprint 8 M3 — Architecture Standards
│   ├── architecture_standards.md ← Architecture standards entrypoint
│   ├── layering.md            ← Structural boundaries & layer constraints
│   ├── dependency_injection.md ← Constructor wiring & registry guidelines
│   ├── service_lifecycle.md   ← Service state transitions & lifecycle hooks
│   ├── event_bus.md           ← Strongly-typed event pub/sub contracts
│   ├── provider_architecture.md ← Model services & OmniRoute strategies
│   ├── skill_architecture.md  ← Plugins, command registry & discovery rules
│   ├── runtime_architecture.md ← State machine, agent runtime & rollback rules
│   └── memory_architecture.md  ← Tiered storage, Qdrant vectors & Redis cache
├── testing_standards/         ← Sprint 8 M4 — Testing Standards
│   ├── README.md              ← Testing standards navigation hub
│   ├── testing_standards.md   ← Core playbook, pyramid, and verification gates
│   ├── unit_testing.md        ← Isolated module verification and boundaries
│   ├── integration_testing.md ← Multi-service collaboration and state isolation
│   ├── regression_testing.md  ← Reproduction workflows and regression guards
│   ├── performance_testing.md ← Latency targets, capacity limits, and benchmarks
│   ├── mocking_guidelines.md  ← unittest.mock rules, factories, and traps
│   └── coverage_requirements.md ← Coverage thresholds, exclusions, and checks
├── documentation_standards/   ← Sprint 8 M5 — Documentation Standards
│   ├── README.md              ← Documentation standards navigation hub
│   ├── documentation_standards.md ← Core playbook, document taxonomy, and sync rules
│   ├── markdown_guidelines.md ← Markdown syntax, metadata blocks, and link rules
│   ├── api_documentation.md   ← Google-style docstrings, type hints, and templates
│   ├── architecture_documentation.md ← ADR templates, design logs, and cross-references
│   ├── generated_documentation.md ← Auto-generators, link checkers, and verification
│   ├── diagram_standards.md   ← Mermaid diagram rules, flowcharting, and sequence structures
│   └── writing_guidelines.md  ← Voice guidelines, direct writing, and clarity rules
├── ai_development_standards/  ← Sprint 8 M6 — AI Development Standards
│   ├── README.md              ← AI development standards navigation hub
│   ├── ai_development_standards.md ← Core playbook and tracing standards
│   ├── prompt_engineering.md  ← Prompt templates, design, and dialogue compaction
│   ├── code_generation_rules.md ← AI code style, type safety, DI, and reuse
│   ├── review_and_validation.md ← Verification loop, coverage targets, and commits
│   ├── safety_guardrails.md   ← Path safety, command validation, and risk gating
│   ├── ai_agent_workflow.md   ← Agent life cycles, subagent spawning, and tasks
│   └── model_selection.md     ← Task mappings, cost controls, and offline routing
└── certification/             ← Sprint 8 M7 — Engineering Certification
    ├── README.md              ← Engineering certification navigation hub
    ├── engineering_certification.md ← Core playbook and overall validation results
    ├── coding_compliance.md   ← PEP8, formatting, and complexity compliance audits
    ├── architecture_compliance.md ← Layering, Dependency Injection, and lifecycle compliance
    ├── testing_compliance.md  ← Pytest runs, fast execution, and coverage audits
    ├── documentation_compliance.md ← Links validation, header checks, and docstring audits
    ├── ai_development_compliance.md ← Guardrails, prompt isolation, and commit compliance
    └── engineering_health_score.md ← Health metric calculations, grades, and actions
```

---

## Reading Order

| Step | Document | When to Read |
|------|----------|--------------|
| 1 | [`vision.md`](vision.md) | First — establish context before anything else |
| 2 | [`philosophy.md`](philosophy.md) | Before proposing any architectural change |
| 3 | [`engineering_principles.md`](engineering_principles.md) | Before writing or reviewing code |
| 4 | [`design_goals.md`](design_goals.md) | Before creating services or interfaces |
| 5 | [`engineering_ethics.md`](engineering_ethics.md) | Before any AI-assisted contribution |
| 6 | [`coding_standards/README.md`](coding_standards/README.md) | Before writing Python code or naming entities |
| 7 | [`architecture_standards/architecture_standards.md`](architecture_standards/architecture_standards.md) | Before adding services, extensions, or modifying systems |
| 8 | [`testing_standards/README.md`](testing_standards/README.md) | Before writing unit, integration, or regression tests |
| 9 | [`documentation_standards/README.md`](documentation_standards/README.md) | Before writing or updating markdown or docstrings |
| 10 | [`ai_development_standards/README.md`](ai_development_standards/README.md) | Before using AI agents to prompt, generate, or review code |
| 11 | [`certification/README.md`](certification/README.md) | To audit and verify system-wide standards compliance |

AI coding agents **must** read this README and the document chain above before beginning any session.

---

## Relationship to the Broader Documentation Suite

This directory is the **foundation layer** of the Engineering Bible. It is not a standalone reference; it is the root that makes every other document below coherent.

```
docs/engineering/           ← YOU ARE HERE (Foundation)
     │
     ├── Informs ──▶  docs/01_ENGINEERING_GUIDELINES.md    (SDLC gates, DoD checklists)
     ├── Informs ──▶  docs/02_ARCHITECTURE_GUIDELINES.md   (Kernel/service boundaries)
     ├── Informs ──▶  docs/05_SECURITY_GUIDELINES.md       (Threat model, privacy gates)
     ├── Informs ──▶  docs/06_TESTING_GUIDELINES.md        (Test strategy, coverage)
     ├── Informs ──▶  docs/07_DOCUMENTATION_GUIDELINES.md  (Markdown, docstrings)
     ├── Summarised in ──▶  docs/16_ENGINEERING_BIBLE.md   (Comprehensive reference)
     ├── Expanded in ──▶  coding_standards/                (Sprint 8 M2 — Coding Standards)
     ├── Expanded in ──▶  architecture_standards/          (Sprint 8 M3 — Architecture Standards)
     ├── Expanded in ──▶  testing_standards/               (Sprint 8 M4 — Testing Standards)
     ├── Expanded in ──▶  documentation_standards/         (Sprint 8 M5 — Documentation Standards)
     ├── Expanded in ──▶  ai_development_standards/        (Sprint 8 M6 — AI Development Standards)
     └── Expanded in ──▶  certification/                   (Sprint 8 M7 — Engineering Certification)
```

Cross-references use absolute file links. All paths assume the monorepo root is
`/Users/anzarakhtar/aios`.

---

## Versioning & Stability Contract

| Property | Rule |
|----------|------|
| Version  | All files in this directory share the same version as the Engineering Bible |
| Mutations | Changes must be committed in a dedicated `docs:` commit, never mixed with feature work |
| Deprecation | No section may be removed without a replacement — only extended or superseded |
| AI Authorship | AI-generated commits carry `Co-authored-by: AI-agent <assistant@personal-ai-os.local>` |

---

*Engineering Bible Foundation · Personal AI OS · Sprint 8 M7 · Governed by [00_PROJECT_VISION.md](file:///Users/anzarakhtar/aios/docs/00_PROJECT_VISION.md)*
