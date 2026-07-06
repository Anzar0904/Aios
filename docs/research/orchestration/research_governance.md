# Research Governance & Approvals Spec
**Sprint 11 · Milestone 6** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define approval challenge rules, domain reputation filters, and credential safeguards for research tasks.
* **Scope**: Governs HTTP security settings, client parameters, and key storage.
* **Audience**: Security Auditors, System Architects, and Integration Developers.
* **Related Documents**:
  * [research/security_model.md](file:///Users/anzarakhtar/aios/docs/research/security_model.md) - Security model.
  * [research/validation/source_validation.md](file:///Users/anzarakhtar/aios/docs/research/validation/source_validation.md) - Source validation.

---

## 1. Outbound Scraper Approvals

Web crawling can consume significant local CPU and bandwidth resources. The **Research Governance** module coordinates with the local **Approval Engine** to check task risks:
* **Interactive Challenges**: High-volume scrapers (e.g. downloading more than 50 pages or fetching raw files > 5MB) prompt the developer for permission before execution.
* **REPL Console Prompts**:
  ```
  [Research Approval Challenge]
  Agent requests to download 120 documentation pages from target domain: 'docs.nextjs.org'.
  Estimated bandwidth: 12MB.
  Confirm crawling run? [y/N]
  ```

---

## 2. Low-Reputation Site Filters

To prevent loading malicious or inaccurate information:
* **Blacklisted Domains**: Outbound searches exclude domains known for low-quality content, content farms, or security risks.
* **SCS Gates**: Content from sources with credibility scores below **0.40** (e.g., untrusted forums or personal blogs) are blocked from automated downloading.

---

## 3. API Key Vault Guards

* **Search Credentials**: API keys for external search services are stored in the database using SQLCipher. Access is limited to registered crawler adapters, preventing plaintext keys from leaking in console outputs or logs.
