# Project Intelligence — API Reference

This document provides the API reference for the Project Intelligence Service classes and interfaces.

---

## 1. ProjectIntelligenceService (Abstract Interface)

**Namespace:** `aios.services.project_intelligence`  
**Base Class:** `aios.services.base.ServiceLifecycle`, `abc.ABC`  

The central service interface registered in the AI OS Kernel container.

### Methods

#### `list_projects`
```python
def list_projects(self) -> List[Dict[str, Any]]
```
Returns a list of all registered project profiles.

---

#### `get_project_profile`
```python
def get_project_profile(self, project_id: str) -> Dict[str, Any]
```
Aggregates and returns the unified project profile containing workspace details, Supabase database, Vercel deployments, etc.

---

#### `discover_project`
```python
def discover_project(self, workspace_path: str) -> Dict[str, Any]
```
Automatically scans the directory at the given path, registers it in the registry, and returns the profile.

---

#### `get_architecture_map`
```python
def get_architecture_map(self, project_id: str) -> Dict[str, Any]
```
Returns component mappings, service dependencies, and module structures.

---

#### `get_health_scorecard`
```python
def get_health_scorecard(self, project_id: str) -> Dict[str, Any]
```
Calculates test coverage, documentation status, technical debt, and provides recommendations.

---

#### `query_knowledge_graph`
```python
def query_knowledge_graph(self, project_id: str, query: str) -> Dict[str, Any]
```
Retrieves nodes and edges from the project knowledge graph.

---

#### `get_dependency_audit`
```python
def get_dependency_audit(self, project_id: str) -> Dict[str, Any]
```
Queries external packages, checks version mismatch alerts, and upgrade recommendations.

---

#### `get_timeline`
```python
def get_timeline(self, project_id: str) -> Dict[str, Any]
```
Aggregates commits, releases, and migrations history.

---

#### `get_risk_analysis`
```python
def get_risk_analysis(self, project_id: str) -> Dict[str, Any]
```
Performs checks on test coverage gaps, security configuration issues, and environmental drift.

---

#### `query_project_memory`
```python
def query_project_memory(self, project_id: str, query: str) -> List[Dict[str, Any]]
```
Performs semantic retrieval over design decisions and past resolutions.

---

#### `generate_reports`
```python
def generate_reports(self, project_id: str, output_dir: Optional[Path] = None) -> Dict[str, Any]
```
Generates the 7 markdown reports under `docs/project/`.

---

#### `clear_cache`
```python
def clear_cache(self) -> None
```
Clears the local caching layer.
