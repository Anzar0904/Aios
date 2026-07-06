# Supabase Intelligence — Security & Trust Model
**Sprint 12 · Milestone 1 (Foundation)** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define API credential isolation, SQL injection guards, and RLS policy verification checks.
* **Scope**: Governs key storage, query validators, and RLS verification rules.
* **Audience**: Security Auditors, System Architects, and Integration Developers.
* **Related Documents**:
  * [05_SECURITY_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/05_SECURITY_GUIDELINES.md) - Core system security.
  * [supabase/supabase_intelligence.md](file:///Users/anzarakhtar/aios/docs/supabase/supabase_intelligence.md) - Conceptual vision.

---

## 1. Credentials Isolation & Key Vaults

Accessing Supabase APIs requires sensitive authentication keys:
* **Service Role Keys (`service_role`)**: Service role keys bypass RLS checks and must never be exposed to agents. They are encrypted using SQLCipher (AES-256-GCM) and are accessible only to registered migration adapters.
* **Anon Keys (`anon`)**: Used for executing standard user queries.
* **Header Sanitization**: Connection adapters strip authorization headers from logs, preventing keys from leaking.

---

## 2. SQL Injection Guards & AST Validation

Before executing raw SQL queries, the system parses the input using `pg_query` to check for security violations:

```python
# Pseudo-implementation of query validation
def validate_database_query(sql_query: str) -> bool:
    parsed_ast = pg_query.parse_query(sql_query)
    
    # Block destructive DDL queries from standard execution paths
    for node in parsed_ast.nodes:
        if node.type in ('DropStmt', 'TruncateStmt', 'AlterTableStmt'):
            raise DestructiveSQLBlocked(f"Blocked query containing: {node.type}")
            
    return True
```

* **DDL Query Blocks**: Standard query tools block destructive commands (e.g. `DROP`, `TRUNCATE`, `ALTER`). Modifying tables requires generating explicit migration files.
* **Parameterized Queries**: Where possible, queries use prepared statements and parameters, preventing SQL injection vulnerabilities.

---

## 3. RLS Policy Auditing

* **RLS Status Checks**: The inspection engine flags tables that do not have Row-Level Security enabled, warning the developer.
* **Policy Rule Verifications**: Analyzes `USING` and `WITH CHECK` clauses, alerting developers to weak validation criteria (e.g., policies using `true` for public access).
* **Local Test Suites**: The system runs query tests locally under mock user identities to verify policy behavior before deployment.
