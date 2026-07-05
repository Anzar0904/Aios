# 07 — Documentation Guidelines
**Version 1.0** · *Classified: For One Person Only* · *July 2026*

---

## Document Metadata
* **Purpose**: Define the writing standards, markdown formatting rules, Mermaid diagram parameters, metadata block schemas, and synchronization rules for all documentation files in the Personal AI OS.
* **Scope**: Governs all markdown files inside `docs/`, `skills/*/README.md`, package-level readmes, and Python inline docstrings.
* **Audience**: Technical Writers, Core Developers, and AI Documentation Agents.
* **Related Documents**:
  * [00_PROJECT_VISION.md](file:///Users/anzarakhtar/aios/docs/00_PROJECT_VISION.md) - Constitutional clarity guidelines.
  * [01_ENGINEERING_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/01_ENGINEERING_GUIDELINES.md) - Definition of Done (DoD) documentation updates.
  * [03_IMPLEMENTATION_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/03_IMPLEMENTATION_GUIDELINES.md) - Playbooks for adding code and logging changes.
  * [16_ENGINEERING_BIBLE.md](file:///Users/anzarakhtar/aios/docs/16_ENGINEERING_BIBLE.md) - Technical monorepo file structure maps.
  * [17_KNOWLEDGE_BASE.md](file:///Users/anzarakhtar/aios/docs/17_KNOWLEDGE_BASE.md) - Personal research notes organization.
  * [18_INTERVIEW_GUIDE.md](file:///Users/anzarakhtar/aios/docs/18_INTERVIEW_GUIDE.md) - Interactive chat transcripts logs.
* **Future Extensions**: Automated markdown linting and broken link check configurations will be integrated as monorepo hook pipelines are set up.

---

## 1. Documentation Philosophy

The Personal AI OS treats **Documentation as Code**. Because this system is maintained across disconnected chat sessions by AI coding agents, outdated or inaccurate documentation acts as a source of system regressions. 

Our documentation strategy is guided by three principles:
1. **Single Source of Truth**: Each document has exactly one responsibility. Duplicate explanations of component behaviors or designs are prohibited.
2. **Readability for Both Humans and AI**: Documents must use precise, structured terminology, explicit markdown links, and tabular metrics so that both human owners and LLM contexts can parse details.
3. **Simultaneous Lifecycle updates**: A code modification is not "Done" until the accompanying documentation files, change lists, and inline docstrings are updated in the same commit.

---

## 2. Documentation Architecture & Hierarchy

Documentation is organized into distinct categories under the following structure:

```text
/ (root)
├── README.md               # Repository entry point, onboarding, and documentation index map.
├── docs/                   # System-wide guidelines and specifications.
│   ├── README.md           # Internal documentation table of contents.
│   ├── 00_PROJECT_VISION.md# Constitutional root of the project.
│   ├── 01_ENGINEERING_GUIDELINES.md to 08_CODING_STANDARDS.md (Guidelines).
│   └── 09_ROADMAP.md to 18_INTERVIEW_GUIDE.md (Roadmaps, logs, and PM specifications).
├── skills/<skill_id>/
│   └── README.md           # Skill manual detailing user commands and prompt variables.
└── core/src/aios/services/README_SECURITY.md # Deep service-level security specs.
```

### 2.1 Category Descriptions
* **Constitutional Core**: Establishes permanent philosophy and guiding design targets.
* **System Guidelines**: Defines strict rules for coding, testing, security, and model strategy.
* **PM Specifications**: Defines roadmap horizons, product requirements, and interface designs (PRD, DRD).
* **Technical Manuals**: Defines low-level execution loops and code files structures (Engineering Bible).
* **Dynamic Logs**: Tracks chronological Architecture Decision Records (ADRs) and user feedback.

---

## 3. Metadata & Document Formatting Standards

Every documentation file (.md) must begin with the following metadata header block:

```markdown
# [ID] — [Document Title]
**Version [X.Y]** · *Classified: [Classification]* · *[Month Year]*

---

## Document Metadata
* **Purpose**: [1-2 sentences explaining what this document specifies.]
* **Scope**: [Define the files, submodules, or workspaces this document governs.]
* **Audience**: [Specify target readers: e.g., AI Architects, Developers, etc.]
* **Related Documents**:
  * [Relative Link Title](file:///path/to/related_document.md)
* **Future Extensions**: [Outline planned changes or next iterations.]

---
```

### 3.1 Markdown Conventions
* **Alert strategic positioning**: Use GitHub alerts (`[!NOTE]`, `[!WARNING]`, `[!IMPORTANT]`) to highlight core parameters or security gates. Do not place consecutive alerts or nest them.
* **Tables**: Organizing configurations, model costs, or file paths in clear Markdown tables.
* **Code blocks**: Language identifiers must be declared for syntax highlighting (e.g. ````python`).

### 3.2 Mermaid Diagram Standards
* Use clear flowcharts, sequence diagrams, and block states to map system operations.
* **Syntax Rules**:
  * Quote node labels that contain special characters (e.g., brackets, parentheses) to prevent parser errors (e.g., `id["Label (Context)"]`).
  * Avoid raw HTML tags inside node text.
  * Capitalize diagram keywords (`graph TD`, `sequenceDiagram`, `loop`, `opt`).

### 3.3 Cross-Referencing Rules
* Cross-references must use absolute file links with the `file:///` scheme (e.g., `[README.md](file:///Users/anzarakhtar/aios/README.md)`).
* Do **not** wrap links or code symbols in backticks when linking, as backticks break markdown hyperlink rendering.
  * *Correct*: `[utils.py](file:///path/to/utils.py)`
  * *Incorrect*: `[`utils.py`](file:///path/to/utils.py)`

---

## 4. Writing & Language Standards

Documentation must conform to the **Personal AI OS Voice** (defined in [00_PROJECT_VISION.md](file:///Users/anzarakhtar/aios/docs/00_PROJECT_VISION.md)):
* **Direct**: Remove conversational filler (e.g., "In this section we will discuss..."). Begin sections with immediate, descriptive subheadings and clear bullet points.
* **Precise**: Distinguish between implemented features, planned capabilities, and alternative configurations.
* **Honest**: List tradeoffs, known limitations, and performance costs.

---

## 5. Inline Code Documentation Standards

All Python code must include inline documentation:
* **Google-Style Docstrings**: Public classes, methods, and modules require docstrings detailing args, return types, exceptions, and side effects.
* **Example Python Docstring**:
  ```python
  def execute_command(self, cmd_name: str, args: List[str]) -> CommandResult:
      """
      Executes a registered CLI command inside the active session.

      Args:
          cmd_name: The exact name string of the command in the registry.
          args: List of parameter strings split by shlex.

      Returns:
          A CommandResult object containing success status and stdout logs.

      Raises:
          KeyError: If the command is not registered in the CommandRegistry.
      """
  ```

---

## 6. System synchronization Rules

Documentation must remain synchronized across components:
1. **Engineering Bible Synchronization**: Low-level code maps in [16_ENGINEERING_BIBLE.md](file:///Users/anzarakhtar/aios/docs/16_ENGINEERING_BIBLE.md) must be updated immediately when file paths are created or removed.
2. **Knowledge Base Synchronization**: Technical details written in research guides under [17_KNOWLEDGE_BASE.md](file:///Users/anzarakhtar/aios/docs/17_KNOWLEDGE_BASE.md) must reference the guidelines documents to prevent design drift.
3. **Interview Guide Synchronization**: Interview conclusion ADRs recorded via the `/grill-me` templates must be logged in [10_DECISION_LOG.md](file:///Users/anzarakhtar/aios/docs/10_DECISION_LOG.md).

---

## 7. Documentation Quality Checklist

Verify these points before staging documentation changes:

- [ ] Metadata blocks are present at the beginning of all created/modified files.
- [ ] No file paths are hardcoded; relative or absolute links use the `file:///` scheme.
- [ ] No hyperlinks are wrapped inside backticks.
- [ ] Diagram Mermaid syntax compiles successfully without parser warnings.
- [ ] Google-style docstrings are written for all modified Python classes and methods.
- [ ] The changelog or roadmaps are updated to reflect the new feature release version.
- [ ] Verified that no secrets, personal keys, or private workspace configurations are exposed.

---

## 8. Future Documentation Roadmap
* **Automated Link Checker**: Deploying git hook scripts (e.g., `markdown-link-check`) to scan files and flag broken links automatically.
* **Inline API Doc Gen**: Configuring automated doc generators (e.g., `pydocstyle`, Sphinx API builders) to compile system HTML manuals.
