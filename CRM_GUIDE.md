# CRM Guide

The AI OS CRM is built on top of a transactional SQLite storage engine, enabling lead pipeline execution, client portfolio tracking, and follow-up schedules.

---

## 1. Database Schema

The CRM records are stored in `~/.aios_agency.db`. Here are the schema definitions:

```sql
CREATE TABLE contacts (
    contact_id    TEXT PRIMARY KEY,
    name          TEXT NOT NULL,
    email         TEXT NOT NULL UNIQUE,
    phone         TEXT NOT NULL DEFAULT '',
    company_id    TEXT NOT NULL DEFAULT '',
    role          TEXT NOT NULL DEFAULT '',
    linkedin      TEXT NOT NULL DEFAULT '',
    website       TEXT NOT NULL DEFAULT '',
    status        TEXT NOT NULL DEFAULT 'active',
    source        TEXT NOT NULL DEFAULT '',
    notes         TEXT NOT NULL DEFAULT '',
    tags          TEXT NOT NULL DEFAULT '[]',
    created_at    REAL NOT NULL,
    last_contact  REAL NOT NULL
);

CREATE TABLE companies (
    company_id    TEXT PRIMARY KEY,
    name          TEXT NOT NULL UNIQUE,
    industry      TEXT NOT NULL DEFAULT '',
    website       TEXT NOT NULL DEFAULT '',
    size          TEXT NOT NULL DEFAULT '',
    location      TEXT NOT NULL DEFAULT '',
    services      TEXT NOT NULL DEFAULT '[]',
    decision_makers TEXT NOT NULL DEFAULT '[]',
    lead_count    INTEGER NOT NULL DEFAULT 0,
    client_status TEXT NOT NULL DEFAULT 'none',
    projects      TEXT NOT NULL DEFAULT '[]',
    created_at    REAL NOT NULL
);

CREATE TABLE leads (
    lead_id         TEXT PRIMARY KEY,
    company_id      TEXT NOT NULL,
    contact_id      TEXT NOT NULL,
    title           TEXT NOT NULL,
    stage           TEXT NOT NULL DEFAULT 'new',
    priority        TEXT NOT NULL DEFAULT 'medium',
    score           INTEGER NOT NULL DEFAULT 50,
    expected_value  REAL NOT NULL DEFAULT 0.0,
    next_action     TEXT NOT NULL DEFAULT '',
    followup_date   REAL NOT NULL DEFAULT 0.0,
    created_at      REAL NOT NULL,
    updated_at      REAL NOT NULL
);
```

---

## 2. Lead Stages & Probabilities

The expected revenue is calculated using probability weights applied to each stage:

| Lead Stage | Weight | Description |
|---|---|---|
| `new` | 10% | Incoming prospect. |
| `qualified` | 30% | Verified target domain fit. |
| `contacted` | 40% | Discovery message sent. |
| `meeting_scheduled` | 60% | Meeting date set. |
| `proposal_sent` | 80% | Proposal document dispatched. |
| `negotiation` | 90% | Pricing/contract alignment. |
| `won` | 100% | Signed contract / closed client. |
| `lost` | 0% | No-go or archived deal. |

---

## 3. Follow-Up Engine

The Follow-Up schedule is resolved dynamically:
- Pending follow-ups are sorted by closest due date first.
- If the current timestamp is past the due date and status is `pending`, the CLI highlights the task as `OVERDUE` in bold red panels.
- Mark follow-ups completed via `aios agency followups complete <id>`.
