# Research Integration & Caching Strategy
**Sprint 11 · Milestone 1 (Foundation)** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define scraping protocols, markdown converters, semantic vector mappings, and local caching rules.
* **Scope**: Governs web scrapers, Qdrant collection settings, and database sync processes.
* **Audience**: Search Engineers, DBAs, and Quality Auditors.
* **Related Documents**:
  * [workspace/integration_strategy.md](file:///Users/anzarakhtar/aios/docs/workspace/integration_strategy.md) - System workspace synchronization.
  * [research/capabilities.md](file:///Users/anzarakhtar/aios/docs/research/capabilities.md) - Mapped source categories.

---

## 1. Local Scrapers & Document Converters

To download external technical sources securely, the Research Intelligence module uses local scrapers:

```
[Target Source URI]
       |
       v
+--------------------------+
|  Local HTTP Adapter      | (urllib / requests / Playwright)
+--------------------------+
       |
       +---> Download raw PDF, HTML, or JSON
       |
       v
+--------------------------+
|  Markdown Converter      | (BeautifulSoup / pdfminer / pandoc)
+--------------------------+
       |
       +---> Strip HTML elements, styles, ads, tracking scripts
       |
       v
+--------------------------+
|  Clean Markdown Document  | ===> Cache in SQLite & index in Qdrant
+--------------------------+
```

1. **Static HTML Scraper**: Employs standard Python clients (e.g. `urllib` or `requests`) to download pages.
2. **Headless Browser (Playwright/Puppeteer)**: For JavaScript-heavy pages (like single-page API docs), the system spawns a local headless browser process, waits for elements to render, and dumps the HTML.
3. **PDF Compiler**: Utilizes local python libraries (e.g. `pypdf`, `pdfminer`) to parse academic publications, extracting headers, figures, and structural body text.

---

## 2. Document Chunking & Concept Indexing

Documents are partitioned into chunks based on structural boundaries:
* **Section-level Splitter**: Splits documents by heading scopes (`#`, `##`, `###`), ensuring sections (such as "Code Example" or "API Params") are kept intact.
* **Concept Embedding**: Chunks are embedded using `all-MiniLM-L6-v2` (384 dimensions, Cosine distance) and saved to Qdrant.

---

## 3. Qdrant Vector Collection Mappings

Research vectors are saved to the **`research_memory`** collection in Qdrant:
* **Dimensions**: 384 dimensions.
* **Payload Fields**:
  ```json
  {
    "workspace_id": "global_or_profile_id",
    "source": "research",
    "source_uri": "https://rfc-editor.org/rfc/rfc7519.txt",
    "source_category": "RFC",
    "title": "RFC 7519: JSON Web Token",
    "concept_name": "JWT Claims validation",
    "text_content": "Section 4.1: The exp claim..."
  }
  ```
* **Payload Indices**: `source_uri`, `source_category`, and `concept_name` are indexed in Qdrant for fast similarity search filtering.

---

## 4. Local SQLite Document Cache

To avoid duplicate network requests and preserve developer privacy:
* **Lookup Sequence**: The acquisition engine checks the SQLite `research_documents` table for the target URL. If a record exists and has not expired, it returns the cached markdown content directly.
* **Expiration TTLs**:
  * API specs & standards (W3C, IETF): **86,400s (24 hours)**.
  * Technical blogs & forums: **604,800s (7 days)**.
  * Official specifications (RFCs, publications): **Permanent (Never expire)**.
