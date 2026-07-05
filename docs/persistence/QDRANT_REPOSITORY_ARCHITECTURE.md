# Qdrant Repository Architecture

This document describes the design patterns, inheritance mapping, and synchronization pipelines of the vector repositories.

---

## 1. Inheritance Hierarchy

All repositories share a common interface structure to avoid code duplication:

```text
       +-------------------------+
       |    ServiceLifecycle     |
       +-------------------------+
                    ▲
                    │
       +-------------------------+
       | VectorMemoryRepository  |
       +-------------------------+
         ▲                     ▲
         │ (Inherits Interface)│ (Implements Operations)
         │                     │
+--------+--------+  +---------+------------+
|  Engineering    |  | QdrantRepositoryImpl |
|MemoryRepository |  +---------+------------+
+--------+--------+            │
         ▲                     │
         │                     │
         +----------+----------+
                    │
  +-----------------+-----------------+
  | EngineeringMemoryRepositoryImpl   |
  +-----------------------------------+
```

---

## 2. Synchronization Strategy (PostgreSQL & Qdrant)

The system maintains a transactional relationship where PostgreSQL is the source of truth:
1. **Save/Insert**: The document metadata is saved to PostgreSQL, then converted to an embedding, and finally upserted to Qdrant.
2. **Failure Mitigation**: If embedding generation or Qdrant upsert fails, the record in PostgreSQL is flagged with `pending_index=True`.
3. **Background Daemon**: A recurring background task scans for PostgreSQL records with `pending_index=True`, processes their embeddings, and indexes them in Qdrant.
