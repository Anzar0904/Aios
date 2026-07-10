# Business Intelligence — CLI Guide

This guide details all command-line interface commands available for Business Intelligence.

---

## Commands Overview

All commands are prefixed with `aios business`.

```bash
aios business <command> [options]
```

### 1. `organizations`
Lists registered agency profiles, company structures, and team configurations.

**Usage:**
```bash
aios business organizations
```

---

### 2. `clients`
Lists and filters registered agency clients, contact emails, and status.

**Usage:**
```bash
aios business clients
```

---

### 3. `leads`
Displays prospective lead intake pipelines, source references, and lead scoring.

**Usage:**
```bash
aios business leads
```

---

### 4. `projects`
Lists all active, completed, or archived portfolio projects linked to clients, repositories, and databases.

**Usage:**
```bash
aios business projects
```

---

### 5. `proposals`
Displays active project proposal details, scope deliverables, and timelines.

**Usage:**
```bash
aios business proposals
```

---

### 6. `workflows`
Inspects client workflow ownership, runtime statistics, runs count, and success rate details.

**Usage:**
```bash
aios business workflows
```

---

### 7. `tasks`
Lists operational task backlogs, priority levels, deadlines, and milestone progress.

**Usage:**
```bash
aios business tasks
```

---

### 8. `analytics`
Retrieves aggregated agency statistics across active projects, online workflows, success rates, and revenue.

**Usage:**
```bash
aios business analytics
```

---

### 9. `timeline`
Generates a consolidated client activity timeline detailing meetings, deployments, issues, and releases.

**Usage:**
```bash
aios business timeline [client_id]
```

---

### 10. `summary`
Compiles all client, organizational, project, and analytics data, and writes the 6 markdown reports to `docs/business/`.

**Usage:**
```bash
aios business summary
```
