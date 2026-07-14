# Intent Engine Guide

This document describes the design and operation of the Intent Engine in the AI OS Natural Language Operating System.

## 1. Overview
The Intent Engine is responsible for detecting, classifying, and resolving plain English queries into structured, actionable system actions. It operates using a hybrid strategy:
1. **Rule-Based Heuristic Matcher**: High-performance, deterministic matching of common phrases and patterns.
2. **LLM classifier fallback**: Deep semantic classification when rule-based patterns do not match.

## 2. Intent Types
The Intent Engine supports the following core types:
* `PROJECT`: Operating project lifecycle actions.
* `AGENCY`: CRM, lead management, proposal generation, and outreach campaigns.
* `WORKFLOW`: Deploying and managing n8n automation workflows.
* `GITHUB`: Querying repositories, branches, commits, PRs, issues, and actions.
* `RESEARCH`: Searching literature, learning topics, and digesting academic materials.
* `PERSONAL`: Goals, tasks, schedules, streaks, and calendar events.
* `SYSTEM`: Diagnostics, tools listings, and kernel state checks.
* `MEMORY`: Semantic memory indexing.
* `CONTEXT`: Context state management.
* `SESSION`: Shell session controls.

## 3. Classification and Routing
When a query is resolved:
1. **Classification**: The engine evaluates the query to resolve its category and action.
2. **Confidence Scoring**: It assigns a confidence value based on keyword overlap or LLM certainty.
3. **Routing**: The resolved intent is mapped to the appropriate target service (e.g. `GitHubService`, `ProjectIntelligenceService`).

## 4. Usage
To test or inspect intent engine routing, run:
```bash
aios intent "Show open GitHub PRs"
```

Output:
```
==================================================
Intent Engine Analysis
==================================================
Raw Query: Show open GitHub PRs
Intent Type: GITHUB
Classified Group: GITHUB
Target Service: GitHubService
Resolved Action: prs
Confidence Score: 1.00
Parameters: {}
==================================================
```
