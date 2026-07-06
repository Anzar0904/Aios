# Technical Concept Extraction Spec
**Sprint 11 · Milestone 3** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define technical specifications for parsing core concepts, API definitions, and mathematical structures.
* **Scope**: Governs concept extractors, term registries, and document metadata mappings.
* **Audience**: AI Prompt Engineers, Integration Engineers, and Quality Auditors.
* **Related Documents**:
  * [research/capabilities.md](file:///Users/anzarakhtar/aios/docs/research/capabilities.md) - Capabilities domains.
  * [research/processing/document_processing.md](file:///Users/anzarakhtar/aios/docs/research/processing/document_processing.md) - Document parsing.

---

## 1. Concept Extraction Engine

The **Concept Extraction Engine** identifies core technical topics, architectural designs, API endpoints, and system definitions from normalized text:

```
[Normalized Markdown Section]
              |
              v
[Terminology Extractor] ===> Identify high-frequency noun phrases
              |
              v
[Pattern Matcher] ===> Match definition indicator blocks (e.g. "Definition: ...")
              |
              v
[Compile Concept Nodes] ===> Link to document section coordinates
```

* **Terminology Extraction**: Extracts high-frequency noun phrases and definitions (e.g. "JSON Web Tokens", "RRF Hybrid Search").
* **Constraint Extraction**: Scans text for requirement keywords (e.g. `MUST`, `SHOULD NOT`, `REQUIRED`), mapping them to corresponding concept nodes.
* **Metadata Association**: Links extracted concepts to their source document IDs and section line ranges, allowing agents to retrieve the exact source context when analyzing a concept.
