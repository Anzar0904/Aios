# AI OS v1.0.0 — RELEASE NOTES
## Official Release of the Personal AI OS Kernel

We are proud to announce the official release of **AI OS v1.0.0**. This release introduces a local-first, modular command and runtime environment designed to orchestrate software projects, local model engines, and external cloud workflows.

---

## 🚀 Key Features

### 💻 Interactive AI OS Shell & Boot Loader
- Premium startup sequence rendering ASCII art, DB checks, and telemetry statistics.
- Auto-completion (Tab), command history, and custom slash commands (e.g. `/status`, `/models`, `/palette`).
- Diagnostic observability telemetry dashboard tracking latencies.

### 🧠 Resilient LLM Gateway (OmniRoute)
- Instantiates `universal_provider_registry` to register local (Ollama) and cloud (OpenRouter) engines.
- Automatic routing logic selects providers based on criteria, costs, and availability.
- **Fail-Safe Fallbacks**: Catch connection timeouts, automatically re-routing inference requests between cloud and local engines in <2.2s.

### 🛡️ Governance Middleware & Cryptographic Approvals
- Intercepts protected high-impact operations (Supabase resets, Vercel production deploys, n8n workflow deletions) at the kernel boundary.
- Stores request tickets in an owner-only queue (`queue.json`).
- Prevents replay attacks using single-use verification tokens.

### 🤖 n8n Workflow Intelligence & Runtime
- Generates, validates, and optimizes workflow graphs locally.
- Syncs local configurations against live n8n servers, offering deployment version control, history audits, and safe rollback capabilities.

### ⚡ Supabase & Vercel Subsystems
- **Supabase**: Discovers database tables, identifies Row-Level Security (RLS) policies, and audits storage/auth configs.
- **Vercel**: Tracks production builds, checks custom DNS certificates, and delivers AI-powered build diagnostics.

---

## 📦 Installation Instructions

### Setup Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Install Dependencies in Editable Mode
```bash
pip install -e ./core pytest ruff
```

### Boot System
```bash
aios
```

---

## ⚠️ Known Limitations
- **Local Model Load Latency**: Loading large local models (14B+) from an external HDD partition can cause a first-time load latency of 20-80s depending on host RAM and disk transfer rates (subsequent tokens process at ~41/sec).
- **PostgreSQL Concurrent Suite Pollution**: Running the full test suite concurrently can cause intermittent db schema locks. Individual test runs are 100% clean.

---

## 🗺️ Roadmap (v1.1)
- **Web UI Dashboard**: Constructing a React/Next.js dashboard using TypeScript and Tailwind CSS to replace terminal commands with interactive visual controls.
- **Multi-Agent Orchestration**: Introducing parallel event buses to allow multiple subagents to process independent project tasks concurrently.
