# N8N, Supabase, Notion, Vercel — Live Validation Evidence
**Date:** 2026-07-13T20:01:54+05:30

---

## N8N

### Credential Discovery

| Source | Value |
|--------|-------|
| `N8N_API_KEY` env | Not set |
| `.aios_n8n_cache/connection_state.json` | `{"url":"http://localhost:5678","connected":true,"auth_type":"none"}` |
| `.aios_n8n_cache/workflow_memory.json` | Contains cached workflow data (Shopify → Slack example) |

### Commands Executed

```bash
GET http://localhost:5678/healthz          # → 200 {"status":"ok"}
GET http://localhost:5678/api/v1/workflows # → 401 {"message":"'X-N8N-API-KEY' header required"}
GET http://localhost:5678/rest/settings    # → 200 (public settings visible)
GET http://localhost:5678/api/v1/credentials # → 401 (requires X-N8N-API-KEY)
```

### Results

| Check | Status |
|-------|--------|
| N8N daemon running | ✅ ONLINE (localhost:5678) |
| `/healthz` | ✅ 200 OK |
| Auth method | Email-based (userManagement enabled) |
| API key configured | ❌ NO (N8N_API_KEY not set) |
| Workflow access | ❌ BLOCKED (requires X-N8N-API-KEY header) |
| Cached workflows | ✅ Present (workflow_memory.json) |

### Code Assessment

- ✅ `N8NLiveConnectionManager` fully implemented
- ✅ `N8NConnectionManager`, `N8NClient`, `N8NCapabilityManager` all importable
- ✅ Auto-discovery implemented (scans ports 5678, 5679, 8000)
- ✅ State persistence working

**VERDICT: ⚠️ PARTIAL — Service ONLINE, API key needed for workflow operations (environmental)**

---

## Supabase

### Credential Discovery

| Source | Value |
|--------|-------|
| `.agent/supabase/credentials.json` | `{"ref":"xyz","url":"https://xyz.supabase.co","key":"mock-key"}` — **placeholder** |
| `SUPABASE_URL` env | Not set |
| `SUPABASE_ANON_KEY` env | Not set |

### Result

All Supabase credentials are placeholders. No real project URL or key available.

- ✅ `services/supabase.py` + `services/supabase_impl.py` fully implemented
- ✅ `test_supabase.py` — all tests PASS with mock
- ❌ Live connection: **BLOCKED** — no real Supabase project credentials

**VERDICT: SKIP — ENVIRONMENTAL BLOCKER (no real Supabase credentials)**

---

## Notion

### Credential Discovery

| Source | Value |
|--------|-------|
| `.agent/notion/credentials.json` | `{"PersonalWorkspace": "secret_mock_token"}` — **placeholder** |
| `NOTION_TOKEN` env | Not set |
| `NOTION_API_KEY` env | Not set |

### Test Failure Analysis

`test_notion.py::test_local_notion_service_crawl_and_cache` — **FAILED**

```
RuntimeError: Cannot add memory: no active workspace context
core/src/aios/services/memory_impl.py:378
```

This is a **code defect**: `LocalNotionService` attempts to call `memory_service.add_memory()` without initializing a workspace context first. The memory service requires `_workspace_id` to be set before adding memories.

### Code Assessment

- ✅ `NotionService`, `LocalNotionService` implemented
- ✅ `NotionCredentialsStore` implemented
- ❌ Live connection: no real token
- ⚠️ `test_local_notion_service_crawl_and_cache`: **CODE DEFECT** — workspace context not initialized before memory write

**VERDICT: ⚠️ PARTIAL — Code defect in Notion memory integration + no real token**

---

## Vercel

### Credential Discovery

| Source | Value |
|--------|-------|
| `.agent/vercel/credentials.json` | `{"access_token":"mock-token"}` — **placeholder** |
| `VERCEL_TOKEN` env | Not set |

### Result

- ✅ `services/vercel.py` + `services/vercel_impl.py` fully implemented
- ✅ `test_vercel.py` — all tests PASS with mock
- ✅ Cached project data in `.agent/vercel/` (project: my-project, framework: nextjs)
- ❌ Live connection: **BLOCKED** — no real Vercel token

**VERDICT: SKIP — ENVIRONMENTAL BLOCKER (no real Vercel token)**
