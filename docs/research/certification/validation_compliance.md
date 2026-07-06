# Research Intelligence — Knowledge Validation Compliance
**Sprint 11 · Milestone 7 (Certification)** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Verify compliance of HTTPS validation gates, SSRF blocklists, confidence scoring calculations, and contradiction checks.
* **Scope**: Governs SSL verifications, IP checks, and confidence scores.
* **Audience**: Quality Auditors, Systems Architects, and AI developers.
* **Related Documents**:
  * [research/validation/README.md](file:///Users/anzarakhtar/aios/docs/research/validation/README.md) - Knowledge Validation hub.
  * [research/validation/confidence_scoring.md](file:///Users/anzarakhtar/aios/docs/research/validation/confidence_scoring.md) - Confidence scoring.

---

## 1. Compliance Audit Objectives

This audit verifies that the **Knowledge Validation & Evidence Graph** layer checks target connection security, blocks SSRF attempts, calculates confidence scores, and detects conflicting claims.

---

## 2. Validation Verification Matrix

```
+------------------------------------+------------------------------------+----------+
| Validation Requirement             | Verification Check                 | Status   |
+------------------------------------+------------------------------------+----------+
| 1. SSL Certificate Gates           | Blocks connections to domains with | PASS     |
|                                    | invalid or expired certificates.   |          |
+------------------------------------+------------------------------------+----------+
| 2. SSRF Guards                     | Domain resolver blocks loopback   | PASS     |
|                                    | (127.0.0.1) and private IP ranges. |          |
+------------------------------------+------------------------------------+----------+
| 3. Confidence Score Formulas       | Calculates scores based on source, | PASS     |
|                                    | consensus, age, and code tests.    |          |
+------------------------------------+------------------------------------+----------+
| 4. Contradiction Detection         | Semantic checks detect conflicting | PASS     |
|                                    | claims, triggering alerts.         |          |
+------------------------------------+------------------------------------+----------+
| 5. Citation Management             | Tracks precise citations linked    | PASS     |
|                                    | to source document line offsets.   |          |
+------------------------------------+------------------------------------+----------+
```

---

## 3. Compliance Verification Details

### 3.1 Network Security & SSRF
* SSRF validation checks resolve domains to IPs, blocking connection requests to loopback or private ranges.
* SSL verifiers block connections to domains with invalid certificates.

### 3.2 Confidence & Contradiction
* Confidence tests confirm that verified facts require a score above `0.80`, and running code examples successfully boosts confidence ratings.
* Contradiction checks scan the database for conflicting claims, mapping a `CONTRADICTS` edge in the Evidence Graph and lowering confidence scores until resolved.
