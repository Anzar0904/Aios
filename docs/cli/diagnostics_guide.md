# Diagnostics Guide

This document describes how to monitor and observe AI OS system status and metrics.

---

## 1. System Diagnostics (`aios diagnostics`)
To review performance metrics, run:
```bash
aios diagnostics
```
Output:
- **Boot time**: Total duration of kernel boot initialization.
- **Startup latency**: Latency of prompt input setup.
- **Loaded modules**: Total Python modules imported.
- **Memory usage**: Active overhead allocated.

---

## 2. Shell Health Indicators
Check integration state across all platforms using:
```bash
aios dashboard
```
Shows active connection status (Connected / Disconnected / Healthy / Warning) for GitHub, Supabase, Vercel, and n8n.
