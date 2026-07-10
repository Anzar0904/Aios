# Approval Engine Guide

The **Approval Engine** is the execution gatekeeper for AI OS. It ensures that no high-impact changes (such as database wipes, branch merges, production rollouts, or proposal deliveries) occur without passing policy checks or receiving explicit user approval.

---

## Key Features

1. **Mandatory Execution Gate**: Centralized middleware inspects actions before they execute.
2. **Single-Use Approval Tokens**: Prevent replay attacks and enforce idempotency.
3. **Risk Classification**: Classifies actions dynamically (LOW, MEDIUM, HIGH, CRITICAL).
4. **Persistent Queue**: Stores and manages requests securely.
5. **Audit Trail Logging**: Records all approvals, rejections, cancellations, and execution results.

---

## Middleware Flow

1. Subsystem requests action: `process_action(action, project, client, provider, details)`.
2. Middleware classifies the risk and evaluates the policy resolution stack (Action -> Project -> Client -> Global).
3. If allowed, returns `status: executed` and a single-use token.
4. Otherwise, registers a pending request under `.agent/approval/queue.json` and returns `status: queued`.
