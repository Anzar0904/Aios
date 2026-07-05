# 13 — Design Requirements Document (DRD)
**Version 1.0** · *Classified: For One Person Only* · *July 2026*

---

## Document Metadata
* **Purpose**: Define the user experience (UX) principles, command-line interface (CLI) layouts, terminal render styles, design systems (colors, typography), visual block patterns, and future dashboard requirements for the Personal AI OS.
* **Scope**: Governs CLI rendering loops (`cli.py`), Markdown output formatters, terminal spinners, task progress bars, and the front-end layouts of the future Renderer.
* **Audience**: UI/UX Designers, Front-End Developers, Systems Engineers, and AI coding agents.
* **Related Documents**:
  * [00_PROJECT_VISION.md](file:///Users/anzarakhtar/aios/docs/00_PROJECT_VISION.md) - Constitutional focus on Simple, Minimal, and Fast principles.
  * [02_ARCHITECTURE_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/02_ARCHITECTURE_GUIDELINES.md) - Future Next.js Renderer specification.
  * [12_PRD.md](file:///Users/anzarakhtar/aios/docs/12_PRD.md) - Functional interface requirements and user personas.
* **Future Extensions**: This document will be expanded with CSS styles sheets and React component libraries once the Next.js/Vite dashboard implementation begins.

---

## 1. Executive Summary & Design Philosophy
The **Personal AI OS** design philosophy is **Information Dense & Keyboard-First**. The user interface must minimize visual clutter (productivity theater) and maximize cognitive efficiency. 
Whether operating in the terminal shell or accessing the future local web dashboard, the design must feel like a premium, state-of-the-art developer workspace:
* **Monospace Integrity**: Monospaced typography and clean layout alignments are maintained across all terminal and web interfaces.
* **Low Latency Feedback**: Every keystroke, transition, and state change must execute with zero observable lag.
* **Contrast Over Color**: Vibrant colors are reserved for critical events (e.g., security alerts, execution states); standard content utilizes structured gradients of slate and white.

---

## 2. Interface Principles & Interaction Design

```
+-----------------------------------------------------------------------------------+
|                            INTERFACE LAYOUT DESIGN                                |
+-----------------------------------------------------------------------------------+
| Workspace Context Header (Git Branch, Project: X)                                  |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|  [Visual Block: Uptime]     [Visual Block: Active Task]    [Visual Block: Models]  |
|                                                                                   |
+-----------------------------------------------------------------------------------+
| Active Session Terminal / Dialogue Output                                         |
| > User query goes here...                                                         |
|                                                                                   |
|  ✓ Step 1: Done  [||||||||||||||||||||||||||] 100%                                |
|  ⠋ Step 2: Running...                                                             |
+-----------------------------------------------------------------------------------+
```

### 2.1 CLI Experience & CLI Renderer
* **ANSI Formatting Standards**: Output streams must format markdown elements (bold, headers, lists) using clear ANSI escape codes.
* **Dynamic Loading Indicators**: Multi-step tasks must render inline, real-time progress bars (e.g., `[████████░░░] 72%`) and spinner characters (`⠋`, `⠙`, `⠹`, `⠸`) rather than scrolling new lines.
* **Output Isolation**: Direct tool standard output is captured and redirected to step logs, ensuring the main chat shell remains clean.

### 2.2 Command Palette & Keyboard-First Workflow
* The CLI must support shell history traversal using up/down arrow keys.
* **Tab-Completion**: Typing partial commands must trigger fuzzy match suggestions (e.g., `task r` completes to `task run`).
* **Hotkey Shortcuts**:
  * `Ctrl + C`: Immediate task interruption and step execution abort.
  * `Ctrl + L`: Clear console screen and print the active workspace header.
  * `Ctrl + P`: Open local command palette search.

---

## 3. The Visual Block System & Dashboard Design

When the Next.js local web server dashboard is deployed (per [09_ROADMAP.md](file:///Users/anzarakhtar/aios/docs/09_ROADMAP.md)), it will organize data into **Visual Blocks**:

### 3.1 Workspace Views
* Renders file trees, active Git branch diffs, and tracked file modification indicators.
* Links code symbols (classes, functions) directly to local IDE endpoints (e.g. `vscode://` or `cursor://` protocol schemas).

### 3.2 Memory Views
* Displays a split-panel interface:
  * Left: Permanent targets, career timelines, and personal principles.
  * Right: Long-lived memory blocks matching the active directory context.

### 3.3 Conversation Views
* Dialogue bubbles utilizing HSL-tailored slate borders and glassmorphism styling.
* Displays conversation summaries (technical decisions, action items, unresolved questions) in a collapsible right-side panel.

### 3.4 Task Views
* Lists active task objectives and step telemetry logs.
* Completed steps display green checkmarks; failed steps render red warning markers with direct "Resume" click actions.

### 3.5 Action Approval UI (Safety Gate)
* Displays side-by-side code diffs when mutating steps are generated.
* High-risk operations (deletions, network calls) are highlighted in amber/red alert blocks.
* Buttons default to keyboard choices (Press `Y` to Approve, `N` to Reject).

---

## 4. Visual Philosophy & Design System

The system defines a unified visual spec across all platforms:

### 4.1 Typography Philosophy
* **Monospaced Interfaces**: monospaced fonts (e.g., *JetBrains Mono*, *Fira Code*, *Source Code Pro*) are mandatory for CLI terminals and code viewer blocks.
* **Web Interfaces**: Sans-serif interfaces (e.g., *Inter*, *Outfit*, *Roboto*) are approved only for high-level web dashboards, styled with clean layouts.
* Browser default fonts (Times New Roman, Arial) are strictly prohibited.

### 4.2 Color System
```
+-----------------------------------------------------------------------------------+
|                                 SYSTEM COLOR PALETTE                              |
+-------------------+----------------------------------+----------------------------+
| Token Name        | Hex / HSL Code                   | Applied Context            |
+-------------------+----------------------------------+----------------------------+
| Deep Background   | HSL(222, 47%, 11%)               | Terminal background / Card |
| Muted Foreground  | HSL(215, 20%, 65%)               | General body / metadata    |
| Vibrant Accent    | HSL(217, 91%, 60%)               | Highlights / active states |
| Success Confirm   | HSL(142, 70%, 45%)               | Completed / Approved / OK  |
| Warning Alert     | HSL(38, 92%, 50%)                | Action approvals / High-risk|
| Error Fail        | HSL(0, 84%, 60%)                 | Fails / Aborts / Exceptions|
+-------------------+----------------------------------+----------------------------+
```

### 4.3 Animation & Motion Principles
* Animations must remain subtle. Avoid heavy bouncing motions or complex sliding transitions.
* **Transitions**: Use fast, linear fade-ins (`transition: opacity 150ms ease-in-out`) for visual blocks loading in the dashboard.
* **Spinners**: Spinner velocities in the CLI must update at **80ms** intervals to feel fluid.

---

## 5. System States

Every view or command response must explicitly define three states:

### 5.1 Empty States
* Empty directories or missing task history files must not result in blank screens.
* Render a placeholder block containing direct actionable advice:
  * *Example*: `"No active tasks found in Project X. Run 'task run [objective]' to start."`

### 5.2 Loading States
* Render progress indicators or spinner frames.
* Show text detailing the active background operation:
  * *Example*: `⠋ Connecting to Gemini provider...`

### 5.3 Error States
* Render bold, high-contrast red warning text.
* Provide an explicit, plain-language explanation of why the action failed, alongside a recovery suggestion:
  * *Example*: `"Access Denied: Path escapes workspace. Suggest checking project root settings."`

---

## 6. Accessibility & Future Considerations

* **Contrast compliance**: Maintain WCAG AAA contrast ratio standards (minimum 7:1) for all foreground text elements in dark mode.
* **Screen Reader Compatibility**: Terminal outputs must use standardized ASCII layout trees instead of complex emoji art to allow screen reader translation.
* **Mobile Considerations**: Designing responsive grids that adapt the Next.js visual dashboard layout into single-column card flows for mobile web viewports.
