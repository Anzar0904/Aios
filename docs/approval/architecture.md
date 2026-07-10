# Approval Engine & Governance — Architecture Guide

This document details the system design, data flows, and secure storage implementation of the Approval Engine and Governance Middleware.

---

## 1. Governance Architecture

All protected actions (like production deployments, db migrations, and branch deletions) route directly through the central `ApprovalMiddleware`.

```
                         +--------------------------+
                         |     Protected Action     |
                         +--------------------------+
                                      |
                                      v
                         +--------------------------+
                         |    ApprovalMiddleware    |
                         +--------------------------+
                                      |
                       +--------------+--------------+
                       |                             |
                 [Always Approve]             [Requires Approval]
                       |                             |
                       v                             v
               Auto-Execution                  Queue Request
               (Assign Token)             (.agent/approval/queue.json)
                                                     |
                                                     v
                                              Manual Confirm
                                              (Approve / Reject)
                                                     |
                                                     v
                                              Log Audit Trail
                                          (.agent/approval/audit.json)
```

---

## 2. Secure Persistent Cache

All data files live under `.agent/approval/` and are secured with `0600` owner-only permissions:

* `queue.json`: Stores queued and active action requests.
* `history.json`: Stores successfully executed governance decisions.
* `policies.json`: Configurable mapping of action/project policies.
* `audit.json`: Continuous audit trail of all manual approvals, automatic executions, and rejections.
