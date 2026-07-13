# AI OS v1.0 — TECHNOLOGY STACK
## Core Languages, Libraries, and Runtimes

AI OS adheres to a **Boring-by-Default & Local-First** technology selection philosophy. Every component of our stack is evaluated for minimal dependency footprint, private local-first operations, and strict version locking.

---

## 1. Core Platform & Runtime
- **Target Platform**: macOS (Apple Silicon / Intel)
- **Programming Language**: Python 3.12+ (specifically validated on Python 3.14.5 in production virtual environment)
- **Package Manager**: Poetry (using standard dependency resolutions)

---

## 2. Core Python Dependencies

| Package | Pin Version | Purpose |
|---|---|---|
| `httpx` | `0.28.1` | Asynchronous, concurrent HTTP networking |
| `rich` | `15.0.0` | Terminal formatting, OS loading UX, tables, progress loaders |
| `pydantic` | `*` | Data serialization, API contracts, JSON schemas |

### Optional / Feature Packages (Sprint Bootstrapped)
- **PostgreSQL Database**: `psycopg2-binary==2.9.9`
- **Vector Database**: `qdrant-client==1.18.0`
- **K/V Cache & Locks**: `redis==8.0.1`
- **Embeddings Pipeline**: `sentence-transformers==3.0.1`
- **Development & Testing**: `pytest==9.1.1`, `ruff==0.15.20`

---

## 3. Supported Database Engines
1. **SQLite**:
   - Location: Local file `aios.db`
   - Purpose: Main relational storage, configurations, timeline logs, and cache indexes.
2. **Qdrant**:
   - Port: `localhost:6333`
   - Purpose: Local vector search index (`research_memory`, `workspace_memory`, etc.).
3. **Redis**:
   - Port: `localhost:6379`
   - Purpose: Key/value session parameters, distributed locks, and cache telemetry.
4. **PostgreSQL**:
   - Port: `localhost:5432` (database: `postgres_live`)
   - Purpose: Persistent database storing structured entities, workflows, and audits.

---

## 4. External Integrations & API Runtimes

- **Local LLM Daemon**: Ollama v0.31.2 (accessing models from external HDD `/Volumes/AI_MODELS/models`).
- **Cloud LLM API**: OpenRouter REST API (serving as primary gateway and fallback).
- **Workflow Runtime**: n8n v2.29.10 (running locally on port `5678` with API key auth).
- **Backend-as-a-Service**: Supabase (running REST API and Applied Migrations DB).
- **Document Hub**: Notion API (integrating with Notion databases/workspaces).
- **Version Control**: GitHub REST API & CLI client tools.
