# Changelog

All notable changes to the Personal AI OS project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0-rc1] - 2026-07-13

### Fixed
- **REC-001 (Security)**: Added `.agent/` and credential wildcards to git ignore to prevent hardcoded credentials leaks.
- **REC-002 (Integrity)**: Replaced mock-based database validation reports with strict live connection checks for PostgreSQL and Qdrant.
- **REC-003 (Code Quality)**: Cleaned up global file exclusions in Ruff linter and resolved over 980 import and type-resolution lints. Fixed a critical undefined variable bug in `discoverers.py`.
- **REC-004 (Performance)**: Implemented asynchronous Qdrant server connection threads and lazy-loaded SentenceTransformer model loading, decreasing startup latency below 100ms.

## [1.0.0] - 2026-07-11

### Added
- **Interactive AI OS Shell**: Boot experience startup health check loaders, tab completion, command history, and custom slash commands.
- **Diagnostics & Observability Telemetry**: Diagnostic latency metrics trackers.
- **Live Progress Engine**: Multi-step progress bars and Rich spinners.
- **Setup Onboarding Wizard**: Quick onboarding flow wizard for credentials setup.
- **Approval Engine & Governance Middleware**: Intercepts protected operations (deployments, database drops, etc.) with scoped security policy resolution.
- **Business Intelligence Subsystem**: Client portfolio profiles manager, analytics summaries, and task lists.
- **Project Intelligence Registry**: Unified project registries, dependency structures, and health metrics.

### Changed
- Bumped system version to `1.0.0` release.
