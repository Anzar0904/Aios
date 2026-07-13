# AI OS v1.0 — DEMO SCRIPT
## Step-by-Step System Demonstration & Walkthrough Guide

This script guides you through a complete end-to-end live demonstration of the Personal AI OS, showcasing its CLI experience, local model execution, cloud routing, third-party integrations, and governance safety.

---

## Preparation Check
1. Ensure the external HDD is mounted at `/Volumes/AI_MODELS` and the models are symlinked:
   ```bash
   ls -la ~/.ollama/models
   ```
2. Verify all local services are running on their default ports:
   - Ollama: `http://localhost:11434`
   - n8n: `http://localhost:5678`
   - PostgreSQL: `localhost:5432`
   - Redis: `localhost:6379`
   - Qdrant: `localhost:6333`

---

## 🎬 Act 1: The Boot Experience & Telemetry

### Step 1: Launch the Interactive OS Shell
Run the launcher command to boot the kernel and initialize the Composition Root:
```bash
aios
```
* **What you see**: A stylized, premium OS loading sequence showcasing ASCII logo art, active provider registration checks (Ollama & OpenRouter), database connectivity status (SQLite, Redis, Qdrant, PostgreSQL), and initial telemetry diagnostics.

### Step 2: Check System Health Telemetry
Inside the shell, query the diagnostics monitor:
```bash
/status
# Or:
aios diagnostics
```
* **What you see**: Active latencies, registry sizes, and system RAM footprint. Displays that 11 models are successfully resolved from the external HDD.

---

## 🎬 Act 2: Local vs. Cloud Routing (OmniRoute)

### Step 1: Run Local Inference
Instruct the system to execute a local-only chat operation on the offline `gemma3:4b` model:
```bash
aios model generate --provider ollama --model gemma3:4b "Reply with: AIOS_LOCAL_OK"
```
* **What you see**: First-time model loading logs. Subsequent local execution runs in ~190ms, returning the exact text `"AIOS_LOCAL_OK"`.

### Step 2: Run Cloud Inference
Instruct the system to execute a cloud chat operation via OpenRouter:
```bash
aios model generate --provider openrouter --model google/gemma-4-26b-a4b-it:free "Reply with: AIOS_CLOUD_OK"
```
* **What you see**: The routing engine targets OpenRouter, returns the text, and displays token count tracking (e.g. 38 tokens).

### Step 3: Trigger Outage Fallback
Simulate a cloud outage by disabling connectivity, then run a query:
```bash
aios model generate "Answer: Resiliency Test"
```
* **What you see**: The engine catches the OpenRouter timeout, automatically fallbacks to local Ollama, resolves the response, and logs the failover event to the console.

---

## 🎬 Act 3: n8n Workflow Operations

### Step 1: Deploy a Workflow Live
Deploy a local workflow configuration file to the live n8n instance:
```bash
aios workflow deploy path/to/my_workflow.json
```
* **What you see**: Validation logs checking for circular references, node connectivity, and missing credentials. Uploads the workflow, returning a live `workflow_id`.

### Step 2: Check Executions & Drift
```bash
aios workflow sync path/to/my_workflow.json
```
* **What you see**: Comparison report showing zero drift between local source and live server configurations.

---

## 🎬 Act 4: Supabase Security Audit

### Step 1: Scan Table Policies
Execute a live security audit on the Supabase database schema:
```bash
aios supabase security
```
* **What you see**: A compiled list of database tables. Flags any table missing Row-Level Security (RLS) policies and warns about public exposures.

---

## 🎬 Act 5: Governance and Action Approvals

### Step 1: Trigger a High-Risk Command
Attempt to delete a workflow from the n8n server:
```bash
aios workflow delete <workflow_id>
```
* **What you see**: The Governance Middleware intercepts the request. The command is **blocked**, and an approval ticket is queued.
  ```text
  [BLOCKED] Action: delete_workflow (Risk: HIGH)
  Request ID: app-req-5f21bc
  Awaiting confirmation. Run 'aios approval approve app-req-5f21bc' to execute.
  ```

### Step 2: Review and Approve the Action
List the pending queue and authorize the action:
```bash
aios approval queue
aios approval approve app-req-5f21bc
```
* **What you see**: The approval token is consumed, the action executes, the workflow is deleted from n8n, and the audit log is updated.
