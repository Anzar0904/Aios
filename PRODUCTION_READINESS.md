# AI OS v1.0 — PRODUCTION READINESS
## Operations & Deployment Manual

This guide outlines the procedures for starting, configuring, and operating AI OS in a production environment.

---

## 1. External Drive & Model Directory Setup

AI OS is configured to load Ollama models from an external storage drive to save local disk space.

### Pre-requisites
1. Mount the external HDD named `AI_MODELS` at `/Volumes/AI_MODELS`.
2. Confirm the presence of the models directory:
   ```bash
   ls -la /Volumes/AI_MODELS/models
   ```

### Configuration Linkage
To ensure that the Ollama daemon (whether started via LaunchAgent or CLI) automatically loads models from the HDD, establish a symlink:
```bash
# Move existing default directory (if empty)
mv ~/.ollama/models ~/.ollama/models.bak

# Symlink to the external HDD models directory
ln -s /Volumes/AI_MODELS/models ~/.ollama/models
```

---

## 2. Daemon Management

### Starting the Ollama Daemon
Start the Ollama daemon from your terminal to verify logging, or let the desktop app launch automatically:
```bash
# Start manually in background
OLLAMA_MODELS=/Volumes/AI_MODELS/models /usr/local/bin/ollama serve > /tmp/ollama_serve.log 2>&1 &
```

### Verifying Discovered Models
Verify that the daemon sees all 11 models from the external drive:
```bash
curl -s http://localhost:11434/api/tags | jq '.models[].name'
```

---

## 3. Credential Setup & File Permissions

Ensure all API keys and service configurations have owner-only permissions.

```bash
# Secure the agent credentials
chmod 700 /Users/anzarakhtar/aios/.agent
chmod 600 /Users/anzarakhtar/aios/.agent/credentials/*.json
chmod 600 /Users/anzarakhtar/aios/.agent/n8n/credentials.json
chmod 600 /Users/anzarakhtar/aios/.agent/supabase/credentials.json
chmod 600 /Users/anzarakhtar/aios/.agent/notion/credentials.json
```

---

## 4. Provider Fallback Operations

OmniRoute handles failover logic automatically. If one LLM provider goes down:
1. **Cloud Outage (OpenRouter fails)**:
   - OmniRoute will catch the error and dispatch requests to the local Ollama instance (`gemma3:4b` or `qwen3.5:9b`).
2. **Local Outage (Ollama fails)**:
   - OmniRoute will reroute the query to OpenRouter (`google/gemma-4-26b-a4b-it:free` or active free models).

---

## 5. Diagnostic Checks

Run the following quick diagnostics to check system status:
```bash
# Check Python environment
source /Users/anzarakhtar/aios/.venv/bin/activate
python3 -c "import aios; print('AI OS Package Importable')"

# Check external service ports
lsof -i :11434 # Ollama
lsof -i :5678  # n8n
lsof -i :5432  # PostgreSQL
lsof -i :6379  # Redis
lsof -i :6333  # Qdrant
```

---
*Created: 2026-07-13T22:45:00+05:30*  
*Agent: Antigravity E2E Orchestrator*
