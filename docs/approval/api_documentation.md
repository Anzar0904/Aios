# Approval Engine & Governance — API Reference

This document provides the API specifications for the Governance Approval Engine components.

---

## 1. ApprovalEngineService (Extended Interface)

**Namespace:** `aios.services.approval`  
**Base Class:** `aios.services.base.ServiceLifecycle`, `abc.ABC`

### Additional Methods

#### `list_queue`
```python
def list_queue(self) -> List[Dict[str, Any]]
```
Lists all requests currently in the approval queue.

---

#### `list_pending`
```python
def list_pending(self) -> List[Dict[str, Any]]
```
Lists pending governance requests.

---

#### `approve_request`
```python
def approve_request(self, request_id: str) -> bool
```
Approves a pending request.

---

#### `reject_request`
```python
def reject_request(self, request_id: str) -> bool
```
Rejects a pending request.

---

#### `cancel_request`
```python
def cancel_request(self, request_id: str) -> bool
```
Cancels a request.

---

#### `retry_request`
```python
def retry_request(self, request_id: str) -> bool
```
Retries execution of an approved or failed request.

---

#### `execute_request`
```python
def execute_request(self, request_id: str) -> Dict[str, Any]
```
Executes an approved request.

---

#### `expire_requests`
```python
def expire_requests(self) -> None
```
Scans and transitions expired requests.

---

#### `get_policies`
```python
def get_policies(self) -> Dict[str, Any]
```
Gets all configured policies.

---

#### `update_policy`
```python
def update_policy(self, policy_id: str, config: Dict[str, Any]) -> None
```
Updates policy configurations.

---

#### `get_preview`
```python
def get_preview(self, request_id: str) -> Dict[str, Any]
```
Generates or retrieves preview details.

---

#### `list_audit_trail`
```python
def list_audit_trail(self) -> List[Dict[str, Any]]
```
Retrieves the audit log trail.

---

## 2. ApprovalMiddleware

**Namespace:** `aios.services.approval_impl`  

Coordinates risk classification, policy checks, and gating logic for every protected action.

### Methods

#### `process_action`
```python
def process_action(
    self,
    action: str,
    project: str,
    client: str,
    provider: str,
    details: Dict[str, Any]
) -> Dict[str, Any]
```
Resolves risk and policy. Returns execution outcomes, request IDs, and single-use approval tokens.
