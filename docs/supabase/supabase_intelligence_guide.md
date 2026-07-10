# Supabase Intelligence Guide

Supabase Intelligence is a production-ready subsystem in Personal AI OS designed to explore, monitor, analyze, secure, and document Supabase projects.

---

## Capabilities

1. **Connection Management**: Connect using Personal Access Tokens (PAT) or specific URL + Service Role Key credentials.
2. **Auto-Discovery**: Automatically index tables, views, functions, triggers, and storage buckets.
3. **Database Analytics**: Map schema constraints, relationships, row counts, and output ER metadata.
4. **Security Scan**: Discover missing RLS policies, public database tables, and insecure exposures.
5. **Migration Drift Checking**: Analyze applied schema migrations, comparing them against the target database.
6. **Edge Functions & Storage**: List storage policies, public/private accessibility state, and edge function deploy status.

---

## Getting Started

To get started, authenticate with your project:

```bash
aios supabase login
```

Then run a general summary of the project to check counts:

```bash
aios supabase summary
```

---

## Performance and Caching

* Metadata caching is automatically configured.
* Discoveries are cached in `.agent/supabase/cache_{project_ref}.json` for 5 minutes (300s TTL).
* Running `summary` automatically generates fresh markdown reports under `docs/supabase/`.
