# Vercel Intelligence Guide

Vercel Intelligence is a production-ready subsystem in Personal AI OS designed to explore, monitor, analyze, secure, and troubleshoot Vercel projects and deployments.

---

## Capabilities

1. **Scoping:** Fully supports Personal and Team account setups.
2. **Project Exploration:** Discovers frameworks, custom domains, environments, and build commands.
3. **Deployment Tracking:** Lists active and history deployments, noting runtimes and rollback options.
4. **Build Diagnostics:** Gathers build logs and analyzes failures to output actionable AI/rule-based explanation summaries.
5. **Environment Audit:** Sweeps target environments (Production, Preview, Development) to list variables metadata without revealing sensitive values.
6. **Health Metrics:** Computes overall health indicators, average deploy durations, and error rates.

---

## Quick Start

1. Log in to your Vercel account:
   ```bash
   aios vercel login
   ```
2. Verify active status and scopes:
   ```bash
   aios vercel status
   ```
3. Run project summary to generate health, deployment, build, domain, and environment reports:
   ```bash
   aios vercel summary
   ```
   Reports will be output under `docs/vercel/`.
