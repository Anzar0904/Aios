# Database & Schema Intelligence — Navigation Hub
**Sprint 12 · Milestone 2** · Version 1.0 · July 2026

---

> [!IMPORTANT]
> This directory houses the **Database & Schema Intelligence** specifications for the Personal AI OS.
> It builds upon the [Supabase Intelligence Foundation](file:///Users/anzarakhtar/aios/docs/supabase/README.md) and maps the physical database structures to the hierarchy:
> **Infrastructure → Supabase Project → Database → Schema → Object → Record → Metadata → KnowledgeNode**.
>
> In accordance with local-first system design guidelines, all schema discoveries, index analyses, query checks, migration comparisons, and health metrics are executed locally, utilizing PostgreSQL catalogs, SQLite databases, and Redis caches.

---

## Documents

| Document | Purpose |
|---|---|
| [schema_intelligence.md](file:///Users/anzarakhtar/aios/docs/supabase/database/schema_intelligence.md) | Schema discovery mechanics, catalog queries, and the Infrastructure Resource abstraction |
| [table_analysis.md](file:///Users/anzarakhtar/aios/docs/supabase/database/table_analysis.md) | Analyzing columns datatypes, JSONB validation, and size estimations |
| [relationship_mapping.md](file:///Users/anzarakhtar/aios/docs/supabase/database/relationship_mapping.md) | Mapping primary/foreign key connections and cascade cycles in local catalogs |
| [index_analysis.md](file:///Users/anzarakhtar/aios/docs/supabase/database/index_analysis.md) | Index scans, B-tree/GIN configurations, and query optimization flags |
| [query_intelligence.md](file:///Users/anzarakhtar/aios/docs/supabase/database/query_intelligence.md) | Explaining query plans, AST verifications, and execution metrics |
| [migration_analysis.md](file:///Users/anzarakhtar/aios/docs/supabase/database/migration_analysis.md) | Reconciling migration logs, local file changes, and schema histories |
| [database_health.md](file:///Users/anzarakhtar/aios/docs/supabase/database/database_health.md) | Index bloat metrics, lock counts, cache hit ratios, and repair loops |

---

## Reading Order

1. **[`schema_intelligence.md`](file:///Users/anzarakhtar/aios/docs/supabase/database/schema_intelligence.md)**: Start here to study metadata queries and the Resource abstraction.
2. **[`table_analysis.md`](file:///Users/anzarakhtar/aios/docs/supabase/database/table_analysis.md)** & **[`relationship_mapping.md`](file:///Users/anzarakhtar/aios/docs/supabase/database/relationship_mapping.md)**: Explore column and relation mappings.
3. **[`index_analysis.md`](file:///Users/anzarakhtar/aios/docs/supabase/database/index_analysis.md)** & **[`query_intelligence.md`](file:///Users/anzarakhtar/aios/docs/supabase/database/query_intelligence.md)**: Learn about index tuning and query plan validation.
4. **[`migration_analysis.md`](file:///Users/anzarakhtar/aios/docs/supabase/database/migration_analysis.md)**: Review DDL diff validations and migration ledgers.
5. **[`database_health.md`](file:///Users/anzarakhtar/aios/docs/supabase/database/database_health.md)**: Examine database health metrics and diagnostics.
