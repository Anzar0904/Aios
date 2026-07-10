# Vercel Intelligence — CLI Guide

This guide documents the command-line interface commands available for Vercel Intelligence in Personal AI OS.

---

## Commands Overview

All Vercel commands are prefixed with `aios vercel`.

```bash
aios vercel <command> [options]
```

### 1. `login`
Authenticate with a Vercel project or account using your Vercel Personal Access Token. Optionally scopes operations to a Team ID.

**Usage:**
```bash
aios vercel login [--token <token>] [--team <team_id>]
```

**Interactive Prompts:**
If no options are supplied, the CLI will interactively prompt for:
1. Vercel Personal Access Token
2. Team ID (Optional)

---

### 2. `status`
Displays current connection status, active team scope, active project ID, count of discovered projects, and team counts.

**Usage:**
```bash
aios vercel status
```

---

### 3. `projects`
Lists all discovered projects under the authenticated account/team.

**Usage:**
```bash
aios vercel projects
```

---

### 4. `deployments`
Displays recent deployments (UID, URL, and deployment state) and a list of verified rollback candidates.

**Usage:**
```bash
aios vercel deployments
```

---

### 5. `logs`
Retrieves the build logs for a specific deployment and runs the diagnostic builder to generate an AI explanation for failures.

**Usage:**
```bash
aios vercel logs <deployment_id>
```

---

### 6. `domains`
Lists custom domains configured for the active project, including verification status and SSL status.

**Usage:**
```bash
aios vercel domains
```

---

### 7. `env`
Displays environment variable metadata keys and target environments (Production, Preview, Development) without exposing secret values.

**Usage:**
```bash
aios vercel env
```

---

### 8. `summary`
Compiles project health metrics, displays deployment success rates, and generates full markdown reports under `docs/vercel/`.

**Usage:**
```bash
aios vercel summary
```
