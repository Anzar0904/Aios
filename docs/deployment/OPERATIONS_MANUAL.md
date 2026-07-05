# 20 — Operations Manual (SysOps Playbook)
**Version 1.0** · *Classified: For One Person Only* · *July 2026*

---

## Document Metadata
* **Purpose**: Define system installation, workspace configuration, backing up, database migration, diagnostics, troubleshooting, and recovery procedures for the Personal AI OS.
* **Scope**: Governs all runtime operations, environmental settings, and diagnostic logs across the monorepo.
* **Audience**: Systems Operators, core developers, and AI maintenance agents.
* **Related Documents**:
  * [00_PROJECT_VISION.md](file:///Users/anzarakhtar/aios/docs/00_PROJECT_VISION.md) - Constitutional privacy and security parameters.
  * [01_ENGINEERING_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/01_ENGINEERING_GUIDELINES.md) - Boring-by-default tech criteria and version locks.
  * [05_SECURITY_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/05_SECURITY_GUIDELINES.md) - Path containment checks and whitelisted commands.
  * [14_TECH_STACK.md](file:///Users/anzarakhtar/aios/docs/14_TECH_STACK.md) - Runtimes and package management.
* **Future Extensions**: This manual will be updated as background daemons, unix socket streams, and docker containers are integrated.

---

## 1. Installation & Environment Provisioning

### 1.1 Local Workspace Installation
The Personal AI OS runs locally inside an isolated virtual environment (`.venv/`):

1. **Clone & Bootstrap**:
   ```bash
   git clone git@github.com:Anzar0904/Aios.git
   cd Aios
   python3 -m venv .venv
   source .venv/bin/activate
   ```
2. **Editable Dependencies Setup**:
   Install the core modules, pytest execution frameworks, and quality checkers:
   ```bash
   pip install -e ./core pytest ruff
   ```
3. **Verify Environment**:
   Confirm that the package resolves and all 88 unit tests run green:
   ```bash
   PYTHONPATH=. pytest
   ```

---

## 2. Configuration & Key Management

### 2.1 Environmental Variables
Outbound API requests require provider keys. Set these in your shell profile (e.g. `.zshrc`):

```bash
# Provider API Tokens
export OPENROUTER_API_KEY="your-openrouter-key"
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
export GEMINI_API_KEY="your-gemini-key"
```

### 2.2 Active Configuration (`config/config.toml`)
Configure provider preferences, offline runtimes, and local paths:
```toml
[runtime]
version = "0.5.0"
offline_mode = false

[provider]
preferred_provider = "openai"
preferred_local_model = "llama3"
preferred_remote_model = "gpt-4o"
fallback_chain = ["openai", "ollama", "lmstudio"]
```

---

## 3. Storage, Backup & Disaster Recovery

### 3.1 Backup Strategy
The active session states, dialogue trees, and memory data reside in the local directory:
* **Directories to Backup**:
  * `.aios_conversations/`: Dialogue history records.
  * `.aios_tasks/`: Pipeline step execution states.
  * `.aios_actions/`: Planned file backups.
  * `config/`: Configurations and memory files (`memory.json`).
* **Automated Backup Command (Cron Example)**:
  Compress and copy target folders to a secure secondary volume daily:
  ```bash
  tar -czf /Volumes/SecureBackup/aios_backup_$(date +%F).tar.gz \
    .aios_conversations/ .aios_tasks/ .aios_actions/ config/
  ```

### 3.2 Recovery Procedures (Disaster Recovery)
If the local database is corrupted or files are deleted by rogue commands:
1. **Wipe State**: Delete corrupted runtime directories.
2. **Restore Files**: Extract the target backup archive back to the project root:
   ```bash
   tar -xzf /Volumes/SecureBackup/aios_backup_[target_date].tar.gz -C ./
   ```
3. **Reset Repository**: If source code was altered, reset the Git working tree:
   ```bash
   git reset --hard HEAD
   ```

---

## 4. Diagnostics & Troubleshooting

```
+-----------------------------------------------------------------------------------+
|                            TROUBLESHOOTING RUNBOOK                                |
+------------------------+---------------------------------+------------------------+
| Error / Issue          | Diagnosis                       | Resolution             |
+------------------------+---------------------------------+------------------------+
| HTTP 429 Rate Limit    | Remote provider key has         | OmniRoute automatically|
|                        | exceeded billing limits.        | fallbacks to Ollama.   |
+------------------------+---------------------------------+------------------------+
| Path Traversal Warn    | Command tried accessing         | Verify project root    |
|                        | absolute paths (e.g. /etc/).    | config variables.      |
+------------------------+---------------------------------+------------------------+
| Broken Database File   | memory.json contains            | Restore from last      |
|                        | syntax formatting errors.       | verified backup file.  |
+------------------------+---------------------------------+------------------------+
| Port Conflict 11434    | Ollama server port is           | Restart local Ollama   |
|                        | occupied or offline.            | engine server instance.|
+------------------------+---------------------------------+------------------------+
```

### 4.1 Diagnostic Logs
* Structured JSON telemetry logs are saved under `.aios_tasks/`.
* Audit plans and user approvals histories are logged in `.aios_actions/`.
* Inline debug details can be traced using standard caplog handlers during testing runs.

---

## 5. System Maintenance & Tuning
* **Memory Pruning**: The Memory Engine automatically prunes short-term records during graceful system shutdowns.
* **Vulnerability Audits**: Periodically scan dependencies for security CVEs:
  ```bash
  pip install safety
  safety check
  ```
* **Performance Tuning**: If model response latencies exceed target parameters, set `offline_mode = True` inside `config/config.toml` to route all queries locally.
