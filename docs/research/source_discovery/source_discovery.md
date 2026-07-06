# Source Discovery Spec
**Sprint 11 · Milestone 2** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define technical specifications for search index crawling, sitemap parsing, and link harvesting.
* **Scope**: Governs domain discovery, links extraction, and sitemap parsers.
* **Audience**: Backend Developers, Systems Architects, and AI developers.
* **Related Documents**:
  * [research/README.md](file:///Users/anzarakhtar/aios/docs/research/README.md) - Research Foundation.
  * [research/source_discovery/provider_registry.md](file:///Users/anzarakhtar/aios/docs/research/source_discovery/provider_registry.md) - Providers registries.

---

## 1. Domain Discovery & Link Harvesting

The **Source Discovery** module parses search engines and target hub pages to build list maps of download targets:

```
[Agent Query / Target Domain]
              |
              +---> 1. Query Providers: Fetch SERP result links.
              +---> 2. Fetch Sitemaps: Parse sitemap XML structures.
              +---> 3. Traverse Hubs: Scrape index/docs directory listings.
              |
              v
[Link Harvester Filter] ===> Deduplicate links & match domain boundaries
              |
              v
[Target URIs Queue] ===> Send to crawler manager
```

* **Sitemap Resolvers**: Automatically checks `/sitemap.xml` and parses the standard XML format, extracting child page URLs and sorting them by modification timestamps.
* **Regex Link Harvesters**: Scrapes index pages (e.g. `https://readthedocs.org/projects/.../`) to extract relative URLs, converting them to absolute URIs and filtering out external advertisement domains.
* **Robots.txt Cache**: Before crawling, the system reads and parses the target domain's `/robots.txt` rules (using Python's `urllib.robotparser`), skipping blocked paths.
