# Resource Scheduling & Throttling Spec
**Sprint 10 · Milestone 6** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define CPU core allocations, job scheduling queues, and power status adapters.
* **Scope**: Governs backend process spawners, build schedules, and system limits.
* **Audience**: DBAs, Backend Developers, and System Architects.
* **Related Documents**:
  * [workspace/development_tools/terminal_management.md](file:///Users/anzarakhtar/aios/docs/workspace/development_tools/terminal_management.md) - Terminal stream controls.
  * [workspace/orchestration/workspace_orchestration.md](file:///Users/anzarakhtar/aios/docs/workspace/orchestration/workspace_orchestration.md) - Coordinator.

---

## 1. Concurrency Scheduler

Running concurrent compilers (e.g. `cargo build`) and large test suites can cause CPU bottlenecks and system lag. The **Resource Scheduler** manages process resource allocations dynamically.

```
                    [Task Queue: Run builds & checks]
                                   |
                                   v
                      [Evaluate Resource Signals]
            - Current CPU Load (%)
            - Power State (AC Power vs Battery)
            - System Temperature (Thermal throttling)
                                   |
                                   v
                     [Configure Process Limits]
            - Set niceness value (CPU priority).
            - limit max concurrent compiler threads.
            - Restrict max heap memory quotas.
```

---

## 2. Job Priority Queuing

Tasks are executed based on three priority levels:
1. **Interactive (High)**: Editor completions, Go to Definition requests, and manual REPL queries. Executed immediately with no resource limits.
2. **Standard (Medium)**: Build tasks and test runs initiated by agents. Allocates up to **50% of CPU cores**.
3. **Background (Low)**: Watcher scans, vector embedding loops, and repository history calculations. Throttled to **1 thread** and set to low process priority (`nice -n 19`).

---

## 3. Power & Thermal Adaptive Scaling

The scheduler monitors host system metrics to adjust resource usage:
* **Battery Power State**: If the host device switches to battery power, the scheduler reduces background indexing cycles to every 5 minutes (instead of real-time) and disables parallel build runs.
* **Thermal Throttling**: If CPU temperatures exceed **85°C**, background tasks are paused until temperatures normalize.
