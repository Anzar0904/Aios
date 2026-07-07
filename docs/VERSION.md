# Version Dashboard
**Version 0.5.0** · *Classified: For One Person Only* · *July 2026*

---

## Authoritative Version Source

> **The canonical version for this project is declared in `pyproject.toml` (monorepo root).**
>
> All documentation, configuration, and code defaults MUST reflect the version found in that file.
> Do not edit version numbers anywhere else without first updating `pyproject.toml`.

```toml
# /pyproject.toml  ← Single Source of Truth
[project]
name = "aios"
version = "0.5.0"
```

See [ADR-0017](adr/DECISION_LOG.md#adr-0017-pyprojecttoml-as-single-version-source-of-truth) for the architectural decision record.

---

## Document Metadata
* **Purpose**: Track project, architecture, documentation, and API release versions alongside quality statuses and audit dates for the Personal AI OS.
* **Scope**: Governs release tags and audit parameters across the monorepo.
* **Audience**: Technical Directors, core maintainers, and release managers.
* **Related Documents**:
  * [09_ROADMAP.md](09_ROADMAP.md) - Release sprint planning.
  * [10_DECISION_LOG.md](10_DECISION_LOG.md) - ADR histories.
  * [CHANGELOG.md](CHANGELOG.md) - Chronological release details.
  * [adr/DECISION_LOG.md](adr/DECISION_LOG.md) - ADR-0017: Versioning policy.
* **Future Extensions**: This version file is updated automatically on git release tagging runs. The version number shown here must always match `pyproject.toml`.

---

## 1. Version Matrix

```
+-----------------------------------------------------------------------------------+
|                                 SYSTEM VERSION MATRIX                             |
+------------------------+---------------------------------+------------------------+
| Parameter Scope        | Current Version Tag             | Lifecycle Status       |
+------------------------+---------------------------------+------------------------+
| Project Version        | v0.5.0                          | Active Development     |
+------------------------+---------------------------------+------------------------+
| Architecture Version   | v1.0.0                          | Standardized           |
+------------------------+---------------------------------+------------------------+
| Documentation Version  | v1.0.0                          | Complete               |
+------------------------+---------------------------------+------------------------+
| API Version            | v0.5.0                          | In Progress (Beta)     |
+------------------------+---------------------------------+------------------------+
```

> **Note**: "Project Version" is the canonical software release version. It is the only version
> that must be kept in sync with `pyproject.toml`. Architecture and Documentation versions track
> their respective maturity independently.

---

## 2. Git Tagging Policy

Git tags MUST follow the Semantic Versioning (`MAJOR.MINOR.PATCH`) format prefixed with `v`.

| Tag Format | When to use |
|---|---|
| `vMAJOR.MINOR.PATCH` | Standard release (e.g. `v0.5.0`) |
| `vMAJOR.MINOR.PATCH-LABEL` | Pre-release or feature-certified cut (e.g. `v0.5.0-alpha`) |

Steps for tagging a release:
1. Bump the `version` field in `/pyproject.toml`.
2. Bump the `version` field in `/core/pyproject.toml` to the same value.
3. Bump the `version` field in `/config/config.toml` to the same value.
4. Update `docs/VERSION.md` (this file) to the same value.
5. Add an entry to `docs/CHANGELOG.md`.
6. Commit, then create a signed git tag: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`.

---

## 3. Release & Audit Telemetry

* **Repository Status**: Clean (0 uncommitted files, 100% staged).
* **Documentation Completion %**: **100%**. All 22 system-wide specifications, manuals, guidelines, and homepages are fully written.
* **Engineering Status**: Stable. Dependency Inversion parameters and Composition Root registries verified.
* **Current Release**: v0.5.0 (Documentation Foundation Phase release).
* **Next Release**: v0.6.0 (Security Hardening Phase release).
* **Last Audit**: July 6, 2026.
* **Last Updated**: July 6, 2026.
