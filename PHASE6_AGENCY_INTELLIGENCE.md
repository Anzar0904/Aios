# Phase 6: Agency Intelligence

> **Status:** ✅ Production — 27/27 Tests passing

## Overview

Phase 6 transforms AI OS into a **Commercial Agency Operating System**. It establishes a Contact Intelligence Layer, lead progression workflows, automated proposals, dynamic follow-up triggers, meetings and outcomes tracking, and revenue forecasting analytics.

All entities (`Person`, `Company`, `Lead`, `Client`, `Meeting`, `Proposal`, `Contract`) are mapped natively into the Universal Knowledge Graph using WORKS_FOR, ATTENDED, SENT_TO, and RELATED_TO relationships.

---

## Subsystems

1. **Contact Intelligence Layer**: Track and link contacts, decision makers, and companies.
2. **Lead Pipeline**: Stage progression (New, Qualified, Contacted, Meeting Scheduled, Proposal Sent, Negotiation, Won, Lost), lead scores, expected value models.
3. **Proposal Engine**: Procedural generator for cold outreach, custom consulting, automations, and custom AI developments.
4. **Outreach Engine**: Generate tailored follow-ups, LinkedIn connection hooks, and discovery questionnaires.
5. **Meeting Intelligence**: Capture agendas, notes, action items, participants, and outcomes.
6. **Follow-Up Schedule**: Tracks pending and overdue follow-up tasks with visual indicators.
7. **Revenue Pipeline**: Calculates expected (weighted by stage probability), closed, and total lead values.

---

## Database Schemas

See [CRM_GUIDE.md](file:///Users/anzarakhtar/aios/CRM_GUIDE.md) for full relational SQLite specifications.

---

## CLI Command Summary

```bash
aios agency dashboard               # Render dashboard and pipeline forecast
aios agency leads                   # List leads or create a new lead
aios agency clients                 # View active closed clients
aios agency companies               # List registered companies
aios agency meetings                # View meeting agenda & outcomes
aios agency proposals               # Draft proposals or display document index
aios agency pipeline                # Render expected & closed revenue statistics
aios agency outreach                # Generate cold email/LinkedIn connection hooks
aios agency followups               # View follow-up actions and alerts
```
