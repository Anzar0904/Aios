# Research Intelligence — Capabilities Matrix
**Sprint 11 · Milestone 1 (Foundation)** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define technical mappings, domain hierarchies, and processing heuristics for technical source categories.
* **Scope**: Governs source types, validation, and conceptual reasoning mappings.
* **Audience**: Systems Integrators, QA Engineers, and AI developers.
* **Related Documents**:
  * [17_KNOWLEDGE_BASE.md](file:///Users/anzarakhtar/aios/docs/17_KNOWLEDGE_BASE.md) - System definitions repository.
  * [research/architecture.md](file:///Users/anzarakhtar/aios/docs/research/architecture.md) - Technical architecture.

---

## 1. Canonical Knowledge Hierarchy

To model external technical knowledge consistently, the AI OS maps all acquired resources to a system-wide hierarchy:

**Research Domain → Knowledge Source → Document → Section → Concept → Evidence → KnowledgeNode**

```
  +----------------------+
  |    Research Domain   | (e.g. "Distributed Databases")
  +----------------------+
            | (1-to-Many)
            v
  +----------------------+
  |   Knowledge Source   | (e.g. "IETF RFC Registry")
  +----------------------+
            | (1-to-Many)
            v
  +----------------------+
  |       Document       | (e.g. "RFC 7519: JSON Web Tokens")
  +----------------------+
            | (1-to-Many)
            v
  +----------------------+
  |       Section        | (e.g. "Section 4.1: Registered Claim Names")
  +----------------------+
            | (1-to-Many)
            v
  +----------------------+
  |       Concept        | (e.g. "JWT expiration validation")
  +----------------------+
            | (1-to-Many)
            v
  +----------------------+
  |       Evidence       | (e.g. "exp claim must contain numeric date value")
  +----------------------+
            | (1-to-Many)
            v
  +----------------------+
  |    KnowledgeNode     | (Local system memory representation)
  +----------------------+
```

---

## 2. Source Categories Matrix

The system classifies and processes incoming resources based on their characteristics:

### 2.1 Documentation
* **Targets**: Official project wikis, Readthedocs pages, MDN docs, package manuals.
* **Extraction**: Strips sidebars, footers, and code editor components, keeping structural markdown and tables.

### 2.2 APIs
* **Targets**: OpenAPI JSON/YAML specifications, Swagger endpoints, GraphQL schema definitions.
* **Extraction**: Compiles REST paths, parameters, return schemas, authentication requirements, and rate limits.

### 2.3 Specifications
* **Targets**: Language spec sheets (e.g. ECMA-262, HTML Living Standard), network standards.
* **Extraction**: Extracts grammar tables, structural definitions, and type constraints.

### 2.4 RFCs
* **Targets**: IETF standard documents, W3C drafts.
* **Extraction**: Parses text files to locate sections and parses requirements tags (`MUST`, `SHOULD NOT`, `RECOMMENDED`).

### 2.5 Academic Papers
* **Targets**: ArXiv papers, PDF publication files.
* **Extraction**: Strips double-column layouts, isolates mathematical equations, extracts references list, and parses abstracts.

### 2.6 Git Repositories
* **Targets**: GitHub/GitLab READMEs, build configurations, directory trees, inline source code comments.
* **Extraction**: Maps projects using Development Workspace Intelligence scanners, indexing file layouts.

### 2.7 Issue Trackers
* **Targets**: GitHub Issues, Jira ticket conversations, bug reports.
* **Extraction**: Parses discussion threads, extracts code snippets, and tags solution paths.

### 2.8 Blogs
* **Targets**: System engineering articles (e.g. Cloudflare blog, Netflix tech blog), developer diaries.
* **Extraction**: Converts text content, filters out advertisements, and matches code samples to technical claims.

### 2.9 Technical Forums
* **Targets**: StackOverflow questions, Reddit discussion nodes.
* **Extraction**: Groups questions with accepted answers, tracking developer comments to evaluate solution reliability.

---

## 3. Acquisition, Validation, & Reasoning Pipeline

1. **Acquire**: Spawns sandboxed scrapers or API clients to download resources locally.
2. **Organize**: Parses documents into sections, mapping them to the canonical hierarchy.
3. **Validate**: Verifies claims against official specs or runs code snippets in a local environment wrapper to test statements.
4. **Reason**: Connects verified concepts to active workspace goals, helping agents design code implementations.
