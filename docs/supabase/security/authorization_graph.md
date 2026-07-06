# Authorization Graph Construction Spec
**Sprint 12 · Milestone 3** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define authorization nodes, access paths, and graph matching schemas.
* **Scope**: Governs SQL graph registries, policy relationships, and access audits.
* **Audience**: Systems Architects, DBAs, and Lead Developers.
* **Related Documents**:
  * [supabase/database/relationship_mapping.md](file:///Users/anzarakhtar/aios/docs/supabase/database/relationship_mapping.md) - Relationship mapping.
  * [supabase/security/rls_analysis.md](file:///Users/anzarakhtar/aios/docs/supabase/security/rls_analysis.md) - RLS analysis.

---

## 1. Authorization Graph Topology

The **Authorization Graph** is a directed graph ($G_{auth} = (V_{nodes}, E_{edges})$) that maps user roles and access policies to table objects:

```
  +-------------------+
  |    User Role      | (e.g. "authenticated", "anon", "service_role")
  +-------------------+
            | (HAS_ACCESS_VIA)
            v
  +-------------------+
  |    RLS Policy     | (USING / WITH CHECK criteria)
  +-------------------+
            | (APPLIED_TO)
            v
  +-------------------+
  |   Table / View    | (Database target object)
  +-------------------+
```

---

## 2. Nodes & Edges Definitions

### 2.1 Nodes ($V_{nodes}$)
* **`RoleNode`**: Represents database user roles (e.g. `anon`, `authenticated`, custom roles).
* **`PolicyNode`**: Represents RLS policies.
* **`ObjectNode`**: Represents target schemas, tables, views, and functions.

### 2.2 Edges ($E_{edges}$)
* **`HAS_ACCESS_VIA`**: Links `RoleNode` to `PolicyNode`, indicating which policies apply to the role.
* **`APPLIED_TO`**: Links `PolicyNode` to `ObjectNode`, indicating the target table or view.
* **`REFERENCES`**: Links `ObjectNode` to `ObjectNode`, indicating foreign key relations.

---

## 3. Path Traversal Auditing

The authorization graph evaluates access paths:
* **Privilege Escalation Scans**: Traverses paths to identify if an `anon` user can access restricted tables through triggers or security definer functions.
* **Graph Queries**: Evaluates paths in the local SQLite database, alerting developers to potential security gaps.
