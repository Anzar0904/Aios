# Business Intelligence — API Reference

This document provides the API reference for the Business Intelligence Service classes and interfaces.

---

## 1. BusinessIntelligenceService (Abstract Interface)

**Namespace:** `aios.services.business`  
**Base Class:** `aios.services.base.ServiceLifecycle`, `abc.ABC`  

The central operational service registered in the AI OS Kernel container.

### Methods

#### `list_organizations`
```python
def list_organizations(self) -> List[Dict[str, Any]]
```
Returns a list of all registered agency organizations.

---

#### `save_organization`
```python
def save_organization(self, org_id: str, org_data: Dict[str, Any]) -> None
```
Creates or updates an organization profile.

---

#### `list_clients`
```python
def list_clients(self) -> List[Dict[str, Any]]
```
Returns all registered client records.

---

#### `save_client`
```python
def save_client(self, client_id: str, client_data: Dict[str, Any]) -> None
```
Registers or updates details for a client.

---

#### `list_leads`
```python
def list_leads(self) -> List[Dict[str, Any]]
```
Returns all sales leads in the pipeline.

---

#### `save_lead`
```python
def save_lead(self, lead_id: str, lead_data: Dict[str, Any]) -> None
```
Registers or updates a lead.

---

#### `list_projects`
```python
def list_projects(self) -> List[Dict[str, Any]]
```
Lists active/completed portfolio projects mapped to client ownership.

---

#### `get_proposal`
```python
def get_proposal(self, proposal_id: str) -> Dict[str, Any]
```
Fetches project proposal estimations and timlines.

---

#### `save_proposal`
```python
def save_proposal(self, proposal_id: str, proposal_data: Dict[str, Any]) -> None
```
Registers or updates proposal versions.

---

#### `list_workflows`
```python
def list_workflows(self) -> List[Dict[str, Any]]
```
Lists workflows, success rates, and client owners.

---

#### `list_tasks`
```python
def list_tasks(self) -> List[Dict[str, Any]]
```
Lists backlogs, priorities, deadlines, and milestone dependencies.

---

#### `get_analytics`
```python
def get_analytics(self) -> Dict[str, Any]
```
Calculates active clients, online workflows, success rates, and agency revenue metrics.

---

#### `get_client_timeline`
```python
def get_client_timeline(self, client_id: str) -> Dict[str, Any]
```
Compiles meetings, deployments, issues, and releases.

---

#### `generate_reports`
```python
def generate_reports(self, output_dir: Optional[Path] = None) -> Dict[str, Any]
```
Writes the 6 markdown reports under `docs/business/`.

---

#### `clear_cache`
```python
def clear_cache(self) -> None
```
Clears caching layers.
