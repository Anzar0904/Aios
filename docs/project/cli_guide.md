# Project Intelligence — CLI Guide

This guide details all command-line interface commands available for Project Intelligence.

---

## Commands Overview

All commands are prefixed with `aios project`.

```bash
aios project <command> [options]
```

### 1. `list`
Lists all registered projects in the Project Registry, along with their Project ID, framework, and creation date.

**Usage:**
```bash
aios project list
```

---

### 2. `status`
Displays system-wide status, including the active project ID and count of total registered projects.

**Usage:**
```bash
aios project status
```

---

### 3. `summary`
Compiles project framework, workspace paths, last activity, and automatically writes the 7 markdown reports to `docs/project/`.

**Usage:**
```bash
aios project summary [project_id]
```

---

### 4. `graph`
Queries and lists connections between files, modules, databases, and commits in the project knowledge graph.

**Usage:**
```bash
aios project graph [project_id]
```

---

### 5. `health`
Displays a comprehensive health scorecard showing overall health score, test coverage, technical debt hours, and recommendations.

**Usage:**
```bash
aios project health [project_id]
```

---

### 6. `timeline`
Generates an aggregated timeline showing commits, deployments, and database migration history.

**Usage:**
```bash
aios project timeline [project_id]
```

---

### 7. `risks`
Displays risk assessments checking for coverage gaps, security configuration issues, and environmental drift.

**Usage:**
```bash
aios project risks [project_id]
```

---

### 8. `architecture`
Retrieves components service maps and module mappings.

**Usage:**
```bash
aios project architecture [project_id]
```

---

### 9. `memory`
Queries architectural design decisions and historical issue resolutions using semantic memory.

**Usage:**
```bash
aios project memory [project_id] [query]
```

---

### 10. `analyze`
Triggers auto-discovery on a given workspace directory to detect framework, package manager, and git configuration.

**Usage:**
```bash
aios project analyze [path]
```
