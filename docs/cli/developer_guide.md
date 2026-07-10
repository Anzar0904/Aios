# Developer UX Guide

This document describes how developers can integrate with the UI / UX enhancements.

---

## 1. Using Spinners
To display a live progress indicator during long-running tasks:
```python
from aios.ux import LiveProgressEngine

with LiveProgressEngine(description="Loading Workspace...") as progress:
    # Run long task
    progress.update("Re-indexing...")
```

---

## 2. Using Error Reporting
Always wrap command execution errors in the `ErrorReporter` panel block:
```python
from aios.ux import ErrorReporter

try:
    execute_operation()
except Exception as e:
    ErrorReporter.report(
        e,
        cause="Subsystem database connection dropped.",
        fix="Ensure credentials are valid and check local server status."
    )
```
