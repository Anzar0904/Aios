# Content Normalization Spec
**Sprint 11 · Milestone 3** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define unicode normalizations, HTML element stripping, and code listing cleanups.
* **Scope**: Governs markdown normalizers, text formatters, and code parsers.
* **Audience**: Systems Integrators, DBAs, and Lead Developers.
* **Related Documents**:
  * [research/capabilities.md](file:///Users/anzarakhtar/aios/docs/research/capabilities.md) - Mapped source categories.
  * [research/processing/document_processing.md](file:///Users/anzarakhtar/aios/docs/research/processing/document_processing.md) - Document segmentations.

---

## 1. Boilerplate Stripping & Elements Cleanup

Raw web pages contain noise (navigation panels, footer links, privacy notifications, sidebars, cookie banners) that bloat context windows.
* **HTML Element Stripping**: The parser strips elements before markdown conversion:
  ```python
  ELEMENTS_TO_STRIP = {
      "nav", "footer", "header", "aside", "script", "style", "form",
      "iframe", "noscript", ".cookie-consent", ".sidebar", ".ad-wrapper"
  }
  ```
* **Link Filtering**: Removes links pointing to social platforms or external advertisements while preserving links pointing to internal API documentation.

---

## 2. Text Unicode Normalization

To ensure consistent text comparison:
* **Unicode Normalization**: Converts all text to Unicode Normalization Form KC (NFKC) compatibility decomposition.
* **Whitespace Compacting**: Collapses consecutive blank lines into single line breaks, and converts carriage returns (`\r\n`) to standard line feed (`\n`) characters.
* **Broken Layout Fixes**: Glues together word segments split across lines by PDF paragraph wraps.

---

## 3. Code Block Normalization

To help code generation models analyze snippets:
* **Language Identifier Tagging**: Inspects code classes in HTML (e.g. `<code class="language-python">`) and inserts corresponding markdown code tags (e.g. ` ```python `).
* **Indentation Fixes**: Replaces non-breaking space characters (`\u00A0`) and tab combinations with standard 4-space indentations.
