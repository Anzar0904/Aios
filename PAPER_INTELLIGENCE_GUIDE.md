# Paper Intelligence Guide

The Paper Ingestion Engine parses academic/technical documents and tracks structural findings.

---

## 1. Database Schema

Stored in the database:

```sql
CREATE TABLE ingested_papers (
    paper_id          TEXT PRIMARY KEY,
    research_id       TEXT NOT NULL,
    title             TEXT NOT NULL,
    authors           TEXT NOT NULL DEFAULT '[]', -- JSON list
    summary           TEXT NOT NULL DEFAULT '',
    methodology       TEXT NOT NULL DEFAULT '',
    findings          TEXT NOT NULL DEFAULT '[]', -- JSON list
    citations         TEXT NOT NULL DEFAULT '[]', -- JSON list
    timestamp         REAL NOT NULL
);
```

---

## 2. Extraction & Ingestion

Ingested papers extract:
- **Methodology**: Experimental parameters or software configurations.
- **Findings**: Quantitative/qualitative outcomes.
- **Citations**: Academic or RFC document links.

---

## 3. CLI Management

```bash
# Analyze and ingest a research paper
aios research paper "Generative Agentic Operating Systems"
```
