# Deployment Documentation

> This section covers installation, configuration, environment setup, and operational procedures for running the Personal AI OS.

---

## Operations Manual

| Document | Purpose |
|---|---|
| [OPERATIONS_MANUAL.md](OPERATIONS_MANUAL.md) | Full installation, configuration, backups, diagnostics, and recovery procedures |

---

## Quick Start

```bash
# 1. Clone the repository
git clone <repo-url> && cd aios

# 2. Create virtual environment
python3 -m venv .venv && source .venv/bin/activate

# 3. Install dependencies
cd core && pip install -e ".[dev]"

# 4. Run the test suite
pytest tests/ --ignore=tests/test_github_skill.py -q

# 5. Start the AI OS
cd .. && python -m aios
```

---

## Environment Configuration

| Variable | Required | Purpose |
|---|---|---|
| `OPENAI_API_KEY` | For OpenAI models | GPT-4o, GPT-4o-mini provider access |
| `ANTHROPIC_API_KEY` | For Claude models | Claude 3.5 Sonnet/Haiku provider access |
| `GOOGLE_API_KEY` | For Gemini models | Gemini 2.0 Flash provider access |
| `REDIS_URL` | Optional | Redis cache/queue (defaults to `redis://localhost:6379`) |
| `QDRANT_URL` | Optional | Qdrant vector store (defaults to `http://localhost:6333`) |
| `POSTGRES_URL` | Optional | PostgreSQL production persistence |

---

## Service Dependencies

| Service | Version | Required | Role |
|---|---|---|---|
| Python | 3.12+ | ✅ Yes | Runtime |
| SQLite | 3.x | ✅ Yes | Primary persistence |
| Redis | 7.x | Optional | Cache, rate-limiting, queuing |
| Qdrant | 1.x | Optional | Vector memory / semantic search |
| PostgreSQL | 15+ | Optional | Production persistence |
| n8n | Latest | Optional | Workflow automation |

See [OPERATIONS_MANUAL.md](OPERATIONS_MANUAL.md) for detailed setup instructions for each service.

---

## Related Sections
- [Infrastructure →](../infrastructure/README.md)
- [Troubleshooting →](../troubleshooting/README.md)
- [Database →](../database/README.md)
