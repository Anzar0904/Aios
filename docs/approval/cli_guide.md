# Approval Engine & Governance — CLI Guide

This guide details all command-line interface commands available for the Governance Approval Engine.

---

## Commands Overview

All commands are prefixed with `aios approval`.

```bash
aios approval <command> [options]
```

### 1. `queue`
Lists all requests currently registered in the approval queue.

**Usage:**
```bash
aios approval queue
```

---

### 2. `pending`
Lists pending governance requests waiting for execution confirmation.

**Usage:**
```bash
aios approval pending
```

---

### 3. `approve`
Manually approves a pending request by ID.

**Usage:**
```bash
aios approval approve [request_id]
```

---

### 4. `reject`
Manually rejects a pending request by ID.

**Usage:**
```bash
aios approval reject [request_id]
```

---

### 5. `cancel`
Cancels an active or queued request by ID.

**Usage:**
```bash
aios approval cancel [request_id]
```

---

### 6. `history`
Displays the complete history of executed decisions and audit log items.

**Usage:**
```bash
aios approval history
```

---

### 7. `policies`
Lists all currently configured scope policies mapping targets.

**Usage:**
```bash
aios approval policies
```

---

### 8. `preview`
Generates and displays the action summary, affected files, rollback availability, and risk estimation before execution.

**Usage:**
```bash
aios approval preview [request_id]
```

---

### 9. `status`
Displays the current status (pending, approved, rejected, cancelled, executed, or expired) of a request.

**Usage:**
```bash
aios approval status [request_id]
```
