# AI OS v1.0 — ARCHITECTURE OVERVIEW
## System Architecture, Decoupling & Event Pipeline Spec

This document details the architectural layers and service boundaries that form the core of the Personal AI OS.

---

## 1. Structural Layer Diagram

AI OS is organized as a decoupled monorepo, separating core infrastructure, business domain services, and client interfaces:

```text
       ┌─────────────────────────────────────────────────────────┐
       │                       aios CLI                          │
       │           (Interactive Shell, REPL, Boot UX)            │
       └────────────────────────────┬────────────────────────────┘
                                    │ Calls
                                    ▼
       ┌─────────────────────────────────────────────────────────┐
       │                     Kernel Bootstrap                    │
       │      (Composition Root, config.toml, dependency injection)│
       └────────────────────────────┬────────────────────────────┘
                                    │ Registers
                                    ▼
       ┌─────────────────────────────────────────────────────────┐
       │                     Service Registry                    │
       │         (Inversion of Control [IoC] Container)          │
       └────────────────────────────┬────────────────────────────┘
                                    │ Resolves
                                    ▼
       ┌─────────────────────────────────────────────────────────┐
       │                Domain Services Layer                    │
       │  (Notion, Supabase, Vercel, n8n, Workspace, Research)   │
       └────────────────────────────┬────────────────────────────┘
                                    │ Leverages
                                    ▼
       ┌─────────────────────────────────────────────────────────┐
       │                OmniRoute & LLM Engine                   │
       │ (universal_provider_registry, universal_routing_engine) │
       └───────────────┬─────────────────────────┬───────────────┘
                       │                         │
                       ▼                         ▼
       ┌────────────────────────┐       ┌────────────────────────┐
       │       Local LLM        │       │       Cloud LLM        │
       │    (Ollama / HDD)      │       │     (OpenRouter)       │
       └────────────────────────┘       └────────────────────────┘
```

---

## 2. Core Modules & Decoupling

- **Dependency Inversion**: High-level domain services do not depend directly on database clients or network drivers. Instead, they depend on abstract interfaces (e.g. `AIProvider`, `RepositoryMixin`). The bootstrap process resolves these dependencies via a centralized `ServiceRegistry` container.
- **Registries**:
  - `universal_provider_registry`: Holds references to instantiated providers (`OllamaProvider`, `OpenRouterProvider`).
  - `universal_model_registry`: Tracks available models, pricing parameters, capabilities, and families.
- **Data Persistence**:
  - The local database (`aios.db`) handles SQLite storage.
  - Local caching utilizes Redis for string K/V, TTL, and locks.
  - High-impact data is synchronized to a PostgreSQL production instance.
  - Semantic vector indices reside in Qdrant collections.

---

## 3. Event Loop & Pipeline Execution

1. **Boot**:
   - `bootstrap_kernel()` loads config from `config.toml`.
   - Initializes local drivers (Redis, Qdrant, SQLite).
   - Probes external ports and registers discoverable providers.
2. **Execution**:
   - Commands are dispatched via `CommandRegistry` inside the CLI loop.
   - Operations requiring external interactions (e.g. Supabase, Vercel) check active project context.
3. **Governance interception**:
   - Sensitive actions are blocked, generating an approval ticket.
   - Execution resumes only after confirmation and receipt of a cryptographic token.
4. **Fallback & Monitoring**:
   - Network timeouts or offline states trigger fallback handlers.
   - Operations log telemetry data to monitor average latency.
