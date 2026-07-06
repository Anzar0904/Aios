# Deployment Metrics & Web Vitals Spec
**Sprint 13 · Milestone 2** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define Web Vitals auditing parameters, page speed latency checks, and server statistics.
* **Scope**: Governs metrics caches, logger files, and performance alerts.
* **Audience**: AI Prompt Engineers, Integration Engineers, and Quality Auditors.
* **Related Documents**:
  * [vercel/capabilities.md](file:///Users/anzarakhtar/aios/docs/vercel/capabilities.md) - Capabilities.
  * [vercel/deployments/deployment_health.md](file:///Users/anzarakhtar/aios/docs/vercel/deployments/deployment_health.md) - Deployment health.

---

## 1. Web Vitals & Page Latency

The **Deployment Metrics** module evaluates application performance using Core Web Vitals:
* **Largest Contentful Paint (LCP)**: Target **< 2.5 seconds** to ensure fast visual loading.
* **First Input Delay (FID)**: Target **< 100 milliseconds** to verify interactivity.
* **Cumulative Layout Shift (CLS)**: Target **< 0.1** to prevent layout shifts.
* **Page Speed Logs**: Records response times for target paths, logging latency spikes exceeding **1500ms** to `docs/vercel/scratch/slow_pages.log`.
* **Metadata Caching**: Stores performance metrics in SQLite and Qdrant, enabling agents to optimize page speed.
