# Supabase Intelligence — API Reference

This document provides the API documentation for the Supabase Intelligence Service classes and interfaces.

---

## 1. SupabaseService (Abstract Interface)

**Namespace:** `aios.services.supabase`  
**Base Class:** `aios.services.base.ServiceLifecycle`, `abc.ABC`  

The main service interface registered in the AI OS Kernel container.

### Methods

#### `login`
```python
def login(
    self,
    access_token: Optional[str] = None,
    project_url: Optional[str] = None,
    service_role_key: Optional[str] = None,
    project_ref: Optional[str] = None
) -> bool
```
Authenticates using a management API Personal Access Token (PAT) or directly connects to a project using its REST endpoint and Service Role key.

---

#### `logout`
```python
def logout(self) -> bool
```
Disconnects the active connection and removes all stored credentials.

---

#### `get_status`
```python
def get_status(self) -> Dict[str, Any]
```
Returns connection state metadata.

---

#### `list_projects`
```python
def list_projects(self) -> List[Dict[str, Any]]
```
Returns a list of all configured and discovered projects.

---

#### `select_project`
```python
def select_project(self, project_ref: str) -> bool
```
Changes the active project reference for metadata queries.

---

#### `get_project_summary`
```python
def get_project_summary(self, project_ref: Optional[str] = None) -> Dict[str, Any]
```
Retrieves high-level component statistics of the target project.

---

#### `get_schema`
```python
def get_schema(self, project_ref: Optional[str] = None) -> Dict[str, Any]
```
Returns the database schema info (tables, views, functions, relationships).

---

#### `get_security_analysis`
```python
def get_security_analysis(self, project_ref: Optional[str] = None) -> Dict[str, Any]
```
Scans RLS status and provides security recommendations.

---

#### `get_migrations`
```python
def get_migrations(self, project_ref: Optional[str] = None) -> Dict[str, Any]
```
Returns applied migration history and drift check state.

---

#### `get_edge_functions`
```python
def get_edge_functions(self, project_ref: Optional[str] = None) -> Dict[str, Any]
```
Lists deployed Edge Functions and configuration state.

---

#### `get_storage`
```python
def get_storage(self, project_ref: Optional[str] = None) -> Dict[str, Any]
```
Returns storage buckets and their properties.

---

#### `get_auth_config`
```python
def get_auth_config(self, project_ref: Optional[str] = None) -> Dict[str, Any]
```
Returns GoTrue auth settings and providers state.

---

#### `generate_reports`
```python
def generate_reports(self, output_dir: Optional[Path] = None) -> Dict[str, Any]
```
Generates 6 standard markdown reports under the specified directory.

---

#### `clear_cache`
```python
def clear_cache(self) -> None
```
Clears the schema and metadata caching layer.

---

## 2. SupabaseCredentialsStore

**Namespace:** `aios.services.supabase`

Responsible for securely reading and writing connection secrets.

* **Default Path:** `.agent/supabase/credentials.json`
* **File Permissions:** 0600 (restricted access)

### Methods
* `load_all() -> Dict[str, Any]`
* `save_credentials(access_token, projects, active_project_ref) -> None`
* `delete_all() -> None`
