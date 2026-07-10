# Supabase Intelligence — CLI Guide

This guide documents the command-line interface commands available for Supabase Intelligence in Personal AI OS.

---

## Commands Overview

All Supabase commands are prefixed with `aios supabase`.

```bash
aios supabase <command> [options]
```

### 1. `login`
Authenticate with a Supabase project or account. Supports Personal Access Tokens (PAT) for project discovery or direct Project URL + Service Role Key authentication.

**Usage:**
```bash
aios supabase login [--token <token>] [--url <url>] [--key <key>] [--ref <ref>]
```

**Interactive Prompts:**
If no options are supplied, the CLI will interactively prompt for:
1. Supabase Personal Access Token (PAT) (Optional)
2. Project URL (Optional)
3. Service Role Key (Optional)

---

### 2. `status`
Displays current connection status, active project reference, API URL, credential status, and count of discovered projects.

**Usage:**
```bash
aios supabase status
```

---

### 3. `projects`
Lists all discovered projects under the authenticated Supabase PAT.

**Usage:**
```bash
aios supabase projects
```

---

### 4. `schema`
Explores and displays tables, views, columns, types, and database functions from the active Supabase database schema.

**Usage:**
```bash
aios supabase schema
```

---

### 5. `security`
Runs a security scan over database tables and policies, warning about disabled Row Level Security (RLS), public tables, and insecure credential exposure.

**Usage:**
```bash
aios supabase security
```

---

### 6. `storage`
Lists all storage buckets and their properties, detailing whether they are public or private, and file size limits.

**Usage:**
```bash
aios supabase storage
```

---

### 7. `auth`
Inspects auth provider configurations (Email, OAuth providers) and Multi-Factor Authentication (MFA) status.

**Usage:**
```bash
aios supabase auth
```

---

### 8. `migrations`
Displays migration history status, applied versions, timestamps, drift detection indicators, and pending migrations.

**Usage:**
```bash
aios supabase migrations
```

---

### 9. `functions`
Lists all remote Edge Functions deployed on the active Supabase project, showing function name, status, and JWT validation settings.

**Usage:**
```bash
aios supabase functions
```

---

### 10. `summary`
Displays a high-level summary of the active project (counts of tables, views, buckets, functions, region, and URL) and generates full markdown reports under `docs/supabase/`.

**Usage:**
```bash
aios supabase summary
```
