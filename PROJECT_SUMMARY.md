# AI OS v1.0 — PROJECT SUMMARY
## The Central Command Engine for Autonomous Operations & Local Intelligence

Personal AI OS is a modular, local-first runtime environment designed to function as a unified command center. It bridges the gap between local execution capabilities (offline databases, CPU/GPU local model inference, semantic workspace intelligence) and cloud services (API triggers, live deployments, structured integrations), enabling seamless execution of complex automation workflows.

---

## 1. Key Value Propositions
- **Privacy & Security First**: Keeps all personal data, credential configurations, and memory layers strictly local. Employs SSRF outbound guards and owner-only file permission enforcements.
- **Unified Semantic Context**: Keeps an active vector-database-backed memory of code modules, design choices, research facts, and user-aligned directives.
- **Fail-Safe Orchestration**: Dynamic fallback engine (OmniRoute) redirects inference tasks between local offline models (Ollama) and cloud APIs (OpenRouter) on provider disruption.

---

## 2. Core Subsystems

### 🧠 OmniRoute Engine & LLM Gateway
- Implements the `universal_provider_registry` and `universal_routing_engine`.
- Selects the optimal model/provider based on request requirements, capabilities, latency, and costs.
- Integrates local Ollama models with cloud OpenRouter models, and enforces graceful fallback chains.

### 📁 Workspace & AST Intelligence
- Indexes source files, directories, imports, and documentation formats.
- Generates dependency trees and structure mappings dynamically.

### 🛡️ Governance Middleware & Approval Engine
- Intercepts protected actions (e.g. Supabase DB wipes, Vercel production rollbacks, workflow deletions).
- Manages an owner-only queued approvals sequence (`aios approval queue`) requiring manual confirmation with single-use cryptographic tokens.

### 🤖 n8n Workflow Intelligence
- Generates, validates, and optimizes complex workflow JSON.
- Integrates with live n8n server instances to deploy, monitor, roll back, and sync workflows.

### ⚡ Supabase & Vercel Subsystems
- **Supabase**: Scans database schemas, identifies missing Row-Level Security (RLS) tables, and audits storage/auth configs.
- **Vercel**: Tracks production deployments, queries custom DNS health, and provides AI-driven build failure diagnostics.

---

## 3. Technical Accomplishments & Performance
- **Boot Time**: <100ms (achieved via async model imports and lazy loading).
- **Core Coverage**: >80% test coverage across 1,417 test cases.
- **Local Capabilities**: Offline chat and embedding generation fully validated against an external HDD model repository.
