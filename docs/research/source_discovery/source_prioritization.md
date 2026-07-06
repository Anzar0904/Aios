# Source Prioritization & Credibility Spec
**Sprint 11 · Milestone 2** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define credibility scoring rules, domain weights, and ranking formulas for discovered search URLs.
* **Scope**: Governs domain rankings, relevance scores, and prioritization queues.
* **Audience**: AI Prompt Engineers, Integration Engineers, and Quality Auditors.
* **Related Documents**:
  * [research/capabilities.md](file:///Users/anzarakhtar/aios/docs/research/capabilities.md) - Capabilities domains.
  * [research/source_discovery/source_discovery.md](file:///Users/anzarakhtar/aios/docs/research/source_discovery/source_discovery.md) - Source discovery.

---

## 1. Source Credibility Scores

Not all information on the internet is equally reliable. The **Source Prioritization** engine assigns a **Source Credibility Score (SCS)** to discovered URLs using domain weights:

```
+------------------------------------+------------------------------------+----------+
| Source Category                    | Domain Indicator / Example         | Weight   |
+------------------------------------+------------------------------------+----------+
| 1. Specifications & RFCs           | rfc-editor.org, w3.org, ietf.org   | 100 / 100|
+------------------------------------+------------------------------------+----------+
| 2. Official Documentation          | docs.python.org, developer.mozilla | 90 / 100 |
+------------------------------------+------------------------------------+----------+
| 3. Academic Papers                 | arxiv.org, semanticscholar.org     | 80 / 100 |
+------------------------------------+------------------------------------+----------+
| 4. Git Repositories / Issues       | github.com/owner/project           | 70 / 100 |
+------------------------------------+------------------------------------+----------+
| 5. Technical Blogs & Forums        | stackoverflow.com, engineering...  | 50 / 100 |
+------------------------------------+------------------------------------+----------+
```

---

## 2. Priority Ranking Formula

Before downloading targets from the crawl queue, the system calculates a **Priority Rank Score (PRS)** to order download tasks:

$$\text{PRS} = (\text{Source Credibility Score} \times 0.6) + (\text{Search Hit Relevance} \times 0.4)$$

* **Search Hit Relevance**: Derived from the search provider result index (e.g. Rank 1 on Google yields 100 points, Rank 10 yields 10 points).
* **Execution Ordering**: The crawler queue processes tasks in descending order of PRS, ensuring official specifications and documentations are downloaded and indexed before forums or developer blogs.
