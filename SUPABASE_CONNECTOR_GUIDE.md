# Supabase Connector Guide

The Supabase Connector tracks database schemas, table updates, and migration histories.

---

## 1. Capabilities

- **Project Discovery**: Links active Supabase projects.
- **Migration Auditing**: Tracks SQL migration histories and alerts for schema changes.
- **Function Mapping**: Scans edge functions deployed.

---

## 2. CLI Invocation

To authenticate and trigger syncs:

```bash
# Connect using service key
aios integrations connect supabase service_key supabase_service_role_key

# Trigger database schema discoveries
aios integrations sync supabase
```
