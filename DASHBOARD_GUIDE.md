# Live Dashboard Guide

The **Live Dashboard** is the command center home screen of AI OS. It aggregates metrics, statuses, and logs from all running subsystems in real-time.

## Dashboard Components

When launching `aios` or typing `d` in the menu, the dashboard displays:

1. **Current Project**: Active workspace context and git branch.
2. **Active Sprint**: Progression of current development cycles.
3. **Open Tasks**: Pending, running, completed, or failed multi-agent tasks.
4. **Agency Status**: Lead pipelines, closed clients, and forecasted revenue.
5. **Research Status**: Ingested papers, active research topics, and findings summaries.
6. **Workflow Status**: Active n8n deployments and automation execution states.
7. **GitHub Status**: PR checks, issues tracking, and release versions.
8. **Integrations**: Telemetry status for Notion, Supabase, n8n, and GitHub.
9. **Core Agents**: Run status and success rates of core engineering agents.

---

## The Status Bar

The Status Bar is pinned at the bottom of every workspace screen, providing system indicators:

* **Project**: The active context workspace (e.g. `aios`).
* **Activity**: Current agent execution description (e.g. `agent SoftwareEngineer executing task`).
* **Model**: Active LLM model routing preference (e.g. `qwen3-coder`).
* **Memory Usage**: Cache size consumed by memory systems.
* **Unread Alerts**: Count of unread alerts in the Notification Center.
* **System Health**: Health percentage computed from system checks.

---

## Pinned Theme System

Type `o` in the Command Center menu to change visual themes:

1. **Default**:
   * Bordures: green and magenta panels.
   * Colors: vibrant terminal palettes.
2. **Minimal**:
   * Borders: ASCII space layouts (no border lines).
   * Colors: Monochrome clean text.
3. **Professional**:
   * Borders: Pinned solid double line borders.
   * Colors: Cobalt blue and magenta highlight accents.
4. **Compact**:
   * Borders: Borderless dense layouts.
   * Colors: Compact padding and spacing with bright cyan borders.
