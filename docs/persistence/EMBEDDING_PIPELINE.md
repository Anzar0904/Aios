# Embedding Generation Pipeline

This document describes the flow of raw text through the embedding pipeline.

---

## 1. Pipeline Stages

```text
  [ Raw Text ]
       │
       ▼
  [ Chunking ]  (Paragraph, sliding window or fixed size)
       │
       ▼
  [ Cache Check ] ---> (Hit: Return vector immediately)
       │ (Miss)
       ▼
  [ Provider Embed ] (SentenceTransformer / Mock)
       │
       ▼
  [ Validation ] (Dimensions count, NaN, Infinite check)
       │
       ▼
  [ Qdrant Index ]
       │
       ▼
  [ Stats & Telemetry ]
```

---

## 2. Validation Constraints

* **Dimensions**: Must exactly match the configured provider dimensions (e.g. 1536 for OpenAI, 384 for SentenceTransformers).
* **Float Integrity**: Checks that no elements in the vector array are `NaN` or `Infinite`.
* **Payload Corruption**: Validates JSON structure of payload attachments before pushing points to Qdrant.
