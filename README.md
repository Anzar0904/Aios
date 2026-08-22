# AIOS

AIOS is a local-first personal AI operating system. Python owns the runtime;
Studio is a localhost-only web client for the same typed APIs.

## What it provides

- Approved local Ollama model routing with explicit load, unload, readiness, and cancellation.
- Local tasks, execution evidence, semantic memory, research, projects, and bounded agents.
- A confirmation gate before writes, Git operations, workflows, network use, or deployment.
- Local-service diagnostics and lifecycle controls for Ollama, SQLite, Redis, Qdrant, MinIO, and n8n.

## Start Studio

```bash
PYTHONPATH=core/src .venv/bin/python -m aios.daemon start
```

Open the loopback URL printed by the command. AIOS never exposes Studio on the
network by default.

## Development checks

```bash
PYTHONPATH=core/src .venv/bin/python -m pytest core/tests
.venv/bin/ruff check core/src
(cd dashboard-web && npm run build)
```

## Repository boundaries

Only source code, tests, configuration templates, and durable documentation
belong in Git. Local databases, conversations, service storage, embeddings,
credentials, runtime state, and generated reports are ignored.

See [docs/README.md](docs/README.md) for the compact documentation map.
