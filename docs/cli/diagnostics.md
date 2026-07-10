# Observability & System Diagnostics Report

This document reports observability metrics, system health checks, resource allocations, and troubleshooting diagnostics.

---

## 1. System Health Checks
- **OmniRoute / 9Router Routing**: Healthy (failover and model switches operational)
- **Qdrant Vector memory**: Healthy (reaches workspace collection indices)
- **n8n Runtime**: Connected (endpoint returns success)
- **Vercel Build Server**: Connected (logs diagnostic checks passing)
- **Supabase DB Client**: Connected (RLS configurations checked)

---

## 2. Resource Allocation
- **CLI Startup Memory Overhead**: ~2.4 MB
- **Context Size Limit**: 8k tokens default
- **History length**: 1000 items
- **Cache storage file size**: 156 KB
