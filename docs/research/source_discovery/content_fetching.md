# Content Fetching & Download Spec
**Sprint 11 · Milestone 2** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define technical specifications for low-level HTTP protocols, header configurations, and PDF downloads.
* **Scope**: Governs HTTP clients, connection pools, and redirect boundaries.
* **Audience**: Systems Integrators, DBAs, and Lead Developers.
* **Related Documents**:
  * [research/security_model.md](file:///Users/anzarakhtar/aios/docs/research/security_model.md) - Security path guards.
  * [research/source_discovery/crawler_architecture.md](file:///Users/anzarakhtar/aios/docs/research/source_discovery/crawler_architecture.md) - Crawler structures.

---

## 1. Network Protocol Configuration

The **Content Fetching** layer handles the raw HTTP socket connections for retrieving web pages, specifications, and academic publications:
* **Connection Pooling**: Reuses TCP connections (via Python `urllib3` connection pools or `requests.Session`) to minimize SSL handshake overhead when crawling a single domain.
* **Redirect Limits**: Follows redirects (HTTP 301, 302, 307, 308) up to a maximum depth of **3 hops**. Exceeding 3 hops halts the request and logs a redirect-loop failure.
* **Timeout Boundaries**:
  * Connection Timeout: **5 seconds**.
  * Read Timeout: **10 seconds**.
  * Total request duration cap: **15 seconds**.

---

## 2. Content Encoding & Headers

To minimize bandwidth consumption and handle modern server compressions:
* **Accept-Encoding**: Appends `gzip, deflate, br` headers. Decodes compressed streams automatically using native libraries (`zlib`, `brotli`).
* **Headers**: Uses standard browser user-agents:
  ```
  User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36
  Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
  Accept-Language: en-US,en;q=0.5
  ```

---

## 3. PDF Parsing & Storage

When retrieving academic publications (such as arXiv papers):
1. **Byte Stream Downloading**: Downloads PDFs as raw byte streams, writing them directly to `docs/research/scratch/raw_downloads/[document_id].pdf`.
2. **Layout Parsing**: Passes PDF paths to local Python libraries (e.g. `pdfminer.high_level`) to extract structured text.
3. **Markdown Conversion**: Formats headers and inserts paragraph markers, ensuring text tables are mapped to markdown grids.
