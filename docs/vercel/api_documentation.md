# Vercel Intelligence — API Reference

This document provides the API reference for the Vercel Intelligence Service classes and interfaces.

---

## 1. VercelService (Abstract Interface)

**Namespace:** `aios.services.vercel`  
**Base Class:** `aios.services.base.ServiceLifecycle`, `abc.ABC`  

The main service interface registered in the AI OS Kernel container.

### Methods

#### `login`
```python
def login(self, access_token: str, team_id: Optional[str] = None) -> bool
```
Authenticates using a Vercel Personal Access Token. Sets active credentials and runs project discovery.

---

#### `logout`
```python
def logout(self) -> bool
```
Clears the active session and credentials.

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
Lists all discovered projects under the account/team.

---

#### `select_project`
```python
def select_project(self, project_id: str) -> bool
```
Changes the active project reference for metadata queries.

---

#### `get_project_summary`
```python
def get_project_summary(self, project_id: Optional[str] = None) -> Dict[str, Any]
```
Retrieves framework, production URL, preview URLs, and build configuration.

---

#### `get_deployments`
```python
def get_deployments(self, project_id: Optional[str] = None) -> Dict[str, Any]
```
Returns recent deployments list and rollback candidates.

---

#### `get_build_analysis`
```python
def get_build_analysis(self, deployment_id: str) -> Dict[str, Any]
```
Retrieves build events/logs and performs AI failure diagnosis.

---

#### `get_domains`
```python
def get_domains(self, project_id: Optional[str] = None) -> Dict[str, Any]
```
Returns custom domains and verification status.

---

#### `get_environments`
```python
def get_environments(self, project_id: Optional[str] = None) -> Dict[str, Any]
```
Lists environment variable keys and targets without exposing secret values.

---

#### `get_monitoring_data`
```python
def get_monitoring_data(self, project_id: Optional[str] = None) -> Dict[str, Any]
```
Retrieves deployment success rate, build counts, and health status.

---

#### `generate_reports`
```python
def generate_reports(self, output_dir: Optional[Path] = None) -> Dict[str, Any]
```
Generates 5 markdown reports under the specified directory.

---

#### `clear_cache`
```python
def clear_cache(self) -> None
```
Clears the local caching layer.

---

## 2. VercelCredentialsStore

**Namespace:** `aios.services.vercel`

Handles secure storage of Vercel credentials.

* **Default Path:** `.agent/vercel/credentials.json`
* **File Permissions:** 0600 (restricted access)

### Methods
* `load_all() -> Dict[str, Any]`
* `save_credentials(access_token, team_id, active_project_id, projects, teams) -> None`
* `delete_all() -> None`
