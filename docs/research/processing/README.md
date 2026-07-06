# Research Processing & Knowledge Extraction — Navigation Hub
**Sprint 11 · Milestone 3** · Version 1.0 · July 2026

---

> [!IMPORTANT]
> This directory houses the **Research Processing & Knowledge Extraction** specifications for the Personal AI OS.
> It builds upon the [Research Foundation](file:///Users/anzarakhtar/aios/docs/research/README.md) and the [Source Discovery](file:///Users/anzarakhtar/aios/docs/research/source_discovery/README.md) specifications.
>
> In accordance with local-first system guidelines, all document parsing, normalizations, concept extractions, entity recognition, relationship mappings, and summarization pipelines run locally on the host machine, utilizing PostgreSQL catalog schemas, Redis caching, and Qdrant memory collections.

---

## Documents

| Document | Purpose |
|---|---|
| [document_processing.md](file:///Users/anzarakhtar/aios/docs/research/processing/document_processing.md) | File segmentations, structural headings slicing, and section mappings |
| [content_normalization.md](file:///Users/anzarakhtar/aios/docs/research/processing/content_normalization.md) | Stripping boilerplate elements, text unicode cleansing, and code listing formatting |
| [concept_extraction.md](file:///Users/anzarakhtar/aios/docs/research/processing/concept_extraction.md) | Technical terminology identification, API definition parsing, and concept lists |
| [entity_recognition.md](file:///Users/anzarakhtar/aios/docs/research/processing/entity_recognition.md) | Named Entity Recognition (NER) mapping code APIs, libraries, endpoints, and error tags |
| [relationship_extraction.md](file:///Users/anzarakhtar/aios/docs/research/processing/relationship_extraction.md) | Direct entity relation extraction mappings (e.g. imports, conflicts, requires) |
| [summarization_pipeline.md](file:///Users/anzarakhtar/aios/docs/research/processing/summarization_pipeline.md) | Facts-retaining text summarizations, stripping fluff, and compiling diagnostics |
| [knowledge_structuring.md](file:///Users/anzarakhtar/aios/docs/research/processing/knowledge_structuring.md) | Relational SQL schema definitions, Qdrant payload setups, and Evidence Graph prep |

---

## Reading Order

1. **[`document_processing.md`](file:///Users/anzarakhtar/aios/docs/research/processing/document_processing.md)** & **[`content_normalization.md`](file:///Users/anzarakhtar/aios/docs/research/processing/content_normalization.md)**: Explore document parsing and text normalizations.
2. **[`concept_extraction.md`](file:///Users/anzarakhtar/aios/docs/research/processing/concept_extraction.md)** & **[`entity_recognition.md`](file:///Users/anzarakhtar/aios/docs/research/processing/entity_recognition.md)**: Study structural concept indexing and Named Entity mappings.
3. **[`relationship_extraction.md`](file:///Users/anzarakhtar/aios/docs/research/processing/relationship_extraction.md)**: Review how dependencies and requirements connections are parsed.
4. **[`summarization_pipeline.md`](file:///Users/anzarakhtar/aios/docs/research/processing/summarization_pipeline.md)**: Explore token optimizations and factual extractions.
5. **[`knowledge_structuring.md`](file:///Users/anzarakhtar/aios/docs/research/processing/knowledge_structuring.md)**: Read about catalog SQL tables, vector collections, and future Evidence Graph preparation.
