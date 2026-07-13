# Upgrade Guide — Personal AI OS v1.0.0 (Release Candidate)

This document provides instructions for upgrading from pre-1.0.0 experimental branches to the v1.0.0 production release candidate.

## 1. Upgrading Dependencies
Version 1.0.0 enforces Python >= 3.12. Ensure your virtual environment is updated:

```bash
# Deactivate old environment
deactivate

# Recreate with Python 3.12+
python3 -m venv .venv
source .venv/bin/activate

# Reinstall with clean core targets
pip install -e ./core
```

## 2. Configuration Configuration Migration
The `config/config.toml` structure has been standardized:
Ensure you do not have legacy database parameters under `[database]` blocks. Set the active provider under `[llm]` block:

```toml
[runtime]
name = "Personal AI OS"
version = "1.0.0"
debug = false

[llm]
provider = "openrouter"
default_model = "qwen/qwen3-coder"
```

## 3. Database Schema Migrations
If utilizing PostgreSQL:
- Ensure PostgreSQL is running.
- Run migrations manually:
  ```bash
  python -m aios.migrations
  ```
If utilizing local-only SQLite mode, the schema migrations will run automatically on the first boot of `aios`.

## 4. Troubleshooting Upgrades
- If you see `KeyError: 'Service ... is not registered'`, perform a clean install of dependencies:
  ```bash
  pip install --force-reinstall -e ./core
  ```
- If Qdrant connection blocks boot, verify that you are running the latest v1.0.0 branch where Qdrant initialization was shifted to a background daemon thread.
