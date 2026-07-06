# DNS Record Verification Spec
**Sprint 13 · Milestone 4** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define DNS checks, A/CNAME record audits, and DNS propagation checking.
* **Scope**: Governs DNS configurations, records checkers, and verification logs.
* **Audience**: Systems Engineers, DBAs, and Lead Developers.
* **Related Documents**:
  * [vercel/environment/domain_intelligence.md](file:///Users/anzarakhtar/aios/docs/vercel/environment/domain_intelligence.md) - Domain intelligence.
  * [vercel/environment/ssl_management.md](file:///Users/anzarakhtar/aios/docs/vercel/environment/ssl_management.md) - SSL management.

---

## 1. DNS Verification Checks

Before routing production traffic to a domain:
* **Record Verification**: Verifies A and CNAME records, checking if DNS records point correctly to Vercel's IP address (`76.76.21.21`) or target alias.
* **Nameserver Checks**: Validates domain nameserver (NS) settings to ensure DNS records are managed correctly.
* **DNS Propagation**: Queries DNS resolvers in different geographic locations to track DNS propagation status.
* **Log Results**: Logs DNS records status to the SQLite database.
