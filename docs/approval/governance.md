# Governance Guide

This document describes the policies, actions protection list, and risk level thresholds configured in the Governance system.

---

## 1. Protected Actions Matrix

| Subsystem | Action | Default Risk Level | Default Policy |
|---|---|---|---|
| **GitHub** | Push, Merge, Release | HIGH | Require confirmation |
| | Delete Branch | CRITICAL | Manual confirm |
| **Supabase** | Migrations, Storage deletion | CRITICAL | Manual confirm |
| | Auth changes, Edge Function deploy | HIGH | Require confirmation |
| **Vercel** | Production deploy | HIGH | Require confirmation |
| | Env modifications, Domain changes | CRITICAL | Manual confirm |
| **n8n** | Workflow deploy, delete, run | MEDIUM | Dry-run preview |
| | Credential modification | CRITICAL | Manual confirm |
| **Business** | Client communication | HIGH | Require confirmation |
| | Proposal delivery, Project archival | HIGH | Require confirmation |

---

## 2. Policy Resolution Stack

Policies resolve from the most specific scope to the most general:

1. **Action-specific policy** (e.g., `action:storage_delete`)
2. **Project-specific policy** (e.g., `project:my_production_db`)
3. **Client-specific policy** (e.g., `client:acme_corp`)
4. **Global default policy** (e.g., `global`)
