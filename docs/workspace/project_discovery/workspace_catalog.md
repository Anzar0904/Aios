# Workspace Catalog Database Schema
**Sprint 10 · Milestone 2** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define the local SQL database schema mapping the development hierarchy.
* **Scope**: Governs SQLite data definitions, relation constraints, and foreign key cascades.
* **Audience**: Database Administrators, Systems Engineers, and AI developers.
* **Related Documents**:
  * [workspace/architecture.md](file:///Users/anzarakhtar/aios/docs/workspace/architecture.md) - Component and storage architecture.
  * [workspace/project_discovery/README.md](file:///Users/anzarakhtar/aios/docs/workspace/project_discovery/README.md) - Project Discovery hub.

---

## 1. Database Model Hierarchy

The workspace catalog is stored locally in an encrypted SQL database. The schema mirrors the system-wide hierarchy:

**Workspace → Project → Repository → Package → Module → File → Symbol**

```
  +--------------------+
  |     workspaces     |
  +--------------------+
            | (1-to-Many)
            v
  +--------------------+
  |      projects      |
  +--------------------+
            | (1-to-Many)
            v
  +--------------------+
  |    repositories    |
  +--------------------+
            | (1-to-Many)
            v
  +--------------------+
  |      packages      |
  +--------------------+
            | (1-to-Many)
            v
  +--------------------+
  |      modules       | (Files)
  +--------------------+
            | (1-to-Many)
            v
  +--------------------+
  |      symbols       |
  +--------------------+
```

---

## 2. SQLite Schema Blueprint

The database uses foreign key constraints with `ON DELETE CASCADE` to maintain consistency when projects or files are deleted.

```sql
-- 1. Workspaces Table (Central root directory configuration)
CREATE TABLE IF NOT EXISTS workspaces (
    workspace_id TEXT PRIMARY KEY,
    workspace_path TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Projects Table (Typed logical project subfolders)
CREATE TABLE IF NOT EXISTS projects (
    project_id TEXT PRIMARY KEY,
    workspace_id TEXT NOT NULL,
    project_path TEXT NOT NULL UNIQUE,
    project_name TEXT NOT NULL,
    language_stack TEXT NOT NULL,          -- 'python', 'typescript', 'rust', etc.
    framework TEXT,                        -- 'django', 'react', 'nextjs', etc.
    build_system TEXT NOT NULL,            -- 'cargo', 'npm', 'poetry', etc.
    package_manager TEXT NOT NULL,         -- 'cargo', 'npm', 'poetry', etc.
    FOREIGN KEY(workspace_id) REFERENCES workspaces(workspace_id) ON DELETE CASCADE
);

-- 3. Repositories Table (VCS directories)
CREATE TABLE IF NOT EXISTS repositories (
    repository_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    repository_root TEXT NOT NULL UNIQUE,
    vcs_type TEXT CHECK(vcs_type IN ('git', 'hg')) NOT NULL,
    active_branch TEXT NOT NULL,
    latest_commit_hash TEXT NOT NULL,
    remote_url TEXT,
    FOREIGN KEY(project_id) REFERENCES projects(project_id) ON DELETE CASCADE
);

-- 4. Packages Table (External dependencies installed)
CREATE TABLE IF NOT EXISTS packages (
    package_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    package_name TEXT NOT NULL,
    version_tag TEXT NOT NULL,
    is_dev_dependency INTEGER CHECK(is_dev_dependency IN (0, 1)) NOT NULL,
    FOREIGN KEY(project_id) REFERENCES projects(project_id) ON DELETE CASCADE,
    UNIQUE(project_id, package_name)
);

-- 5. Modules Table (Physical files containing code)
CREATE TABLE IF NOT EXISTS modules (
    module_id TEXT PRIMARY KEY,
    repository_id TEXT NOT NULL,
    relative_path TEXT NOT NULL,
    absolute_path TEXT NOT NULL UNIQUE,
    file_size_bytes INTEGER NOT NULL,
    sha256 TEXT NOT NULL,
    last_modified TIMESTAMP NOT NULL,
    FOREIGN KEY(repository_id) REFERENCES repositories(repository_id) ON DELETE CASCADE
);

-- 6. Symbols Table (Classes, methods, structs, functions)
CREATE TABLE IF NOT EXISTS symbols (
    symbol_id TEXT PRIMARY KEY,
    module_id TEXT NOT NULL,
    symbol_name TEXT NOT NULL,
    symbol_type TEXT CHECK(symbol_type IN ('CLASS', 'METHOD', 'FUNCTION', 'STRUCT', 'VARIABLE')) NOT NULL,
    start_line INTEGER NOT NULL,
    end_line INTEGER NOT NULL,
    docstring TEXT,
    FOREIGN KEY(module_id) REFERENCES modules(module_id) ON DELETE CASCADE
);
```
