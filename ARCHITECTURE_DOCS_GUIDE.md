# Architecture Documentation Guide

The Architecture Generator maps service flows, component diagrams, and graph linkages.

---

## 1. Document Structure

The generated Architecture guide contains:
1. **System Overview**: High level description of the design.
2. **Component Diagrams**: Mermaid flowchart showing CLI, Kernel, and Database connections.
3. **Data Flow**: Descriptions of SQL database transactional scopes and Graph update events.

---

## 2. CLI Invocation

```bash
# Generate architecture manual for project 'core'
aios docs architecture core
```
