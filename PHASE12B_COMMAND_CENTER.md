# Phase 12B: AI OS Command Center & UX Specification

Welcome to the **AI OS Command Center & UX** (Phase 12B) of AI OS. This update transforms the AI OS from a command-only shell into a unified keyboard-driven operating system console, enabling navigation, search, agent tracking, automation control, and natural language chat from a single terminal interface.

## System Architecture & Interaction Flow

```mermaid
graph TD
    Boot[aios clean boot] --> BootSequence[Boot Loading animation]
    BootSequence --> CommandCenter[Command Center UI]
    
    subgraph Navigation & Keyboard shortcuts
        CommandCenter --> d[d: Dashboard]
        CommandCenter --> p[p: Project Workspace]
        CommandCenter --> a[a: Agency Workspace]
        CommandCenter --> r[r: Research Workspace]
        CommandCenter --> g[g: GitHub Workspace]
        CommandCenter --> w[w: Workflow Workspace]
        CommandCenter --> t[t: Agent Workspace]
        CommandCenter --> n[n: Alerts / Notifications]
        CommandCenter --> s[s: Universal Search]
        CommandCenter --> c[c: Chat Panel]
        CommandCenter --> k[k / Ctrl+K: Command Palette]
        CommandCenter --> o[o: Theme switcher]
        CommandCenter --> q[q: Shutdown]
    end
    
    StatusBar[Status Bar: Project | Activity | Model | Memory | Alerts | Health] --> CommandCenter
```

## Component Guides
- **Live Dashboard**: A unified overview panel summarizing sprint cycles, active leads, open pull requests, and automation health. See [DASHBOARD_GUIDE.md](file:///Users/anzarakhtar/aios/DASHBOARD_GUIDE.md).
- **Workspace Navigation**: Dedicated panels aggregating project roadmaps, sales leads, academic papers, and active workflow deployments. See [WORKSPACE_GUIDE.md](file:///Users/anzarakhtar/aios/WORKSPACE_GUIDE.md).
- **Notification Center**: Track alerts from workflows, GitHub pull requests, meeting reminders, and agent statuses with read/unread, priority, and category filtering. See [NOTIFICATION_GUIDE.md](file:///Users/anzarakhtar/aios/NOTIFICATION_GUIDE.md).
- **Universal Search**: Clean command to index and scan across all projects, tasks, workflows, documents, clients, and meetings. See [SEARCH_GUIDE.md](file:///Users/anzarakhtar/aios/SEARCH_GUIDE.md).
- **Command Palette**: A searchable action palette (`Ctrl+K`) to execute registered commands. See [COMMAND_PALETTE_GUIDE.md](file:///Users/anzarakhtar/aios/COMMAND_PALETTE_GUIDE.md).

## Theme Customizations
AI OS supports four visual themes that customize terminal borders and layout densities:
1. **Default**: Modern, vibrant colors utilizing green, cyan, and magenta panels.
2. **Minimal**: Clean borderless ASCII layouts with monochrome text.
3. **Professional**: Dark-themed cobalt styles with blue and magenta accents.
4. **Compact**: Ultra-dense layouts with reduced spacing to fit maximum information on small screens.

## Shell Commands

- `aios` (launches directly into the Command Center interactive dashboard)
- `aios dashboard` (boots into the Command Center interactive dashboard)
- `aios search <query>` (scans across all OS modules and displays matching results)
- `aios notifications` (displays the list of alerts and unread counts)
- `aios workspace <project|agency|research|github|workflow|agent>` (boots directly into the specified workspace)
- `aios status` (prints the active OS status bar metrics)
