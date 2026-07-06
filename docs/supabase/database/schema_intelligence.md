# Schema Discovery & Resource Abstraction Spec
**Sprint 12 · Milestone 2** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define PostgreSQL metadata queries, schema inspection rules, and the Infrastructure Resource abstraction.
* **Scope**: Governs schema checkers, catalog queries, and abstract resource schemas.
* **Audience**: Systems Architects, DBAs, and Lead Developers.
* **Related Documents**:
  * [supabase/architecture.md](file:///Users/anzarakhtar/aios/docs/supabase/architecture.md) - Service architecture.
  * [supabase/database/README.md](file:///Users/anzarakhtar/aios/docs/supabase/database/README.md) - Database navigation hub.

---

## 1. The Infrastructure Resource Abstraction

To represent different database objects consistently, the AI OS introduces the **Infrastructure Resource** abstraction. This provides a unified interface for all database components (tables, schemas, functions, policies):

```
                       +------------------------------+
                       |    InfrastructureResource    | (Base Model class)
                       +------------------------------+
                         /         |          \      \
                        v          v           v      v
                    [Table]    [Schema]    [View]  [Function]
```

### 1.1 Model Schema
```python
class InfrastructureResource:
    def __init__(self, resource_id: str, resource_type: str, resource_name: str, schema_name: str, metadata: dict, status: str) -> None:
        self.resource_id = resource_id        # Unique UUID value
        self.resource_type = resource_type    # SCHEMA, TABLE, VIEW, FUNCTION, INDEX, POLICY
        self.resource_name = resource_name    # Name of the object (e.g. "users_profile")
        self.schema_name = schema_name        # Name of schema (e.g. "public")
        self.metadata = metadata              # JSON dictionary holding parameters
        self.status = status                  # ACTIVE, DEPRECATED, UNTRACKED
```

---

## 2. Schema Discovery & Metadata Queries

The schema inspection engine queries the PostgreSQL system catalog (`information_schema` and `pg_catalog`) to discover resources:
* **Schema Namespaces**:
  ```sql
  SELECT schema_name FROM information_schema.schemata 
  WHERE schema_name NOT IN ('pg_catalog', 'information_schema', 'pg_toast');
  ```
* **Views Discovery**:
  ```sql
  SELECT table_name, view_definition FROM information_schema.views 
  WHERE table_schema = :schema_name;
  ```
* **Objects Registration**: Discovered tables and views are mapped to the local SQLite database as `InfrastructureResource` instances, updating the catalog.
