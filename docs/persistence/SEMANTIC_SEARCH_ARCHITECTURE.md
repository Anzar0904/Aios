# Semantic Search Architecture

This document describes the query routing, caching, and cross-collection querying patterns of the Semantic Search Engine.

---

## 1. Search Pipeline

1. **Embedding Resolution**: Resolves query text to a vector coordinates array using `EmbeddingEngine`.
2. **Metadata Merging**: Merges specific pre-filtering keys (`workspace_id`, `project_id`) into payload parameters.
3. **Execution**: Routes queries to the corresponding vector memory repository.
4. **Pagination**: Applies pagination offsets (`offset`) and limits (`limit`) before returning results.

---

## 2. Multi & Cross-Collection Search

The search engine supports searching across multiple collections simultaneously by querying each collection, combining results, sorting globally by similarity score, and truncating to the requested top-k limit.

---

## 3. Query Cache

To maximize performance, query result lists are cached in-memory using keys derived from:
`collection_name:query_text:serialized_filters:limit:offset`
Any changes to the source collections invalidate cache segments automatically.
