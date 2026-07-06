# Research Intelligence — Certification Playbook
**Sprint 11 · Milestone 7 (Certification)** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define the compliance validation playbook, audit scopes, and verification procedures for certifying Sprint 11 milestones.
* **Scope**: Governs all verification gates and health scoring indices for Research integrations.
* **Audience**: Quality Auditors, Systems Architects, and AI developers.
* **Related Documents**:
  * [16_ENGINEERING_BIBLE.md](file:///Users/anzarakhtar/aios/docs/16_ENGINEERING_BIBLE.md) - Core reference guidelines.
  * [research/certification/README.md](file:///Users/anzarakhtar/aios/docs/research/certification/README.md) - Navigation hub.

---

## 1. Playbook Framework & Scope

The **Research Intelligence Certification Playbook** verifies that all Sprint 11 milestones (Milestones 1–6) conform to the security, local-first, and structural guidelines of the Personal AI OS.

This certification is a **Design and Schema Compliance Audit**. It evaluates source discoverers, content fetchers, text normalizers, NER classifiers, confidence score engines, database tables, and AI orchestration without altering active execution behaviors.

---

## 2. Validation Targets (M1–M6)

The compliance audit evaluates six target areas:

```
+------------------------------------+------------------------------------------+
| Validation Domain                  | Core Verification Criteria               |
+------------------------------------+------------------------------------------+
| 1. Research Foundation (M1)        | Local-first interfaces, provider         |
|                                    | registries, and path boundaries.         |
+------------------------------------+------------------------------------------+
| 2. Source Discovery (M2)           | Sitemap walkers, robots.txt lints,       |
|                                    | token-buckets, and back-off delays.      |
+------------------------------------+------------------------------------------+
| 3. Research Processing (M3)        | Heading parsers, element cleans, NER     |
|                                    | tags, and relationship extractors.       |
+------------------------------------+------------------------------------------+
| 4. Knowledge Validation (M4)       | SSL cert checks, SSRF guards, confidence  |
|                                    | score formulas, and citation ledgers.    |
+------------------------------------+------------------------------------------+
| 5. Research Memory (M5)            | SQLite databases, Qdrant layouts, and    |
|                                    | Redis invalidation triggers.             |
+------------------------------------+------------------------------------------+
| 6. AI Orchestration (M6)           | Research planners, context compression,  |
|                                    | background walkers, and approvals.       |
+------------------------------------+------------------------------------------+
```

---

## 3. Compliance Methodologies

* **Structural Review**: Verify that database schemas, adapter classes, and process execution modules are syntactically complete.
* **Security Scans**: Confirm that outbound SSRF checks block private range IPs, and verify that HTML parsers strip malicious elements.
* **Vector Layout Validation**: Verify dimension compatibility (384d Cosine distance) with the local Sentence Transformer model.
* **Consent Auditing**: Ensure that the AI OS prompts the developer before executing high-risk scraping operations.
