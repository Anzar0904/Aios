# Services Documentation

> This section documents individual service modules, their APIs, and integration patterns.

---

## Core Services

| Document | Purpose |
|---|---|
| [PROVIDERS.md](PROVIDERS.md) | AI provider registry: models, routing, failover, and cost tracking |
| [COMMANDS.md](COMMANDS.md) | CLI command registry: all slash commands and their handlers |
| [SECURITY.md](SECURITY.md) | Security service: secrets, encryption, and trust boundaries |
| [DEVELOPER_SERVICE.md](DEVELOPER_SERVICE.md) | Developer service: code generation, analysis, and review pipeline |

---

## Runtime Service Reports

Detailed runtime diagnostics and status reports are located in:
- [`docs/infrastructure/`](../infrastructure/README.md) — Infrastructure services (n8n, source control)
- [`docs/database/`](../database/README.md) — Persistence services (SQLite, PostgreSQL, Redis, Qdrant)
- [`docs/runtime/`](../runtime/README.md) — Runtime intelligence diagnostics

---

## Related Sections
- [Architecture →](../architecture/README.md)
- [Skills →](../skills/README.md)
- [Troubleshooting →](../troubleshooting/README.md)
