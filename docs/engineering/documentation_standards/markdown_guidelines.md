# Markdown Formatting & Link Guidelines
**Engineering Bible — Milestone 5**
**Version 1.0** · *Classified: For One Person Only* · *July 2026*

---

## 1. Document Metadata Header Schema

Every system documentation file (.md) must begin with the following metadata header block to provide immediate context for both human developers and AI agents:

```markdown
# [Document Title]
**Engineering Bible — [Milestone/Section Name]**
**Version [X.Y]** · *Classified: For One Person Only* · *[Month Year]*

---

## Document Metadata

* **Purpose**: [1-2 sentences explaining what this document specifies.]
* **Scope**: [Define the files, submodules, or workspaces this document governs.]
* **Audience**: [Specify target readers: e.g., AI Architects, Developers, etc.]
* **Related Documents**:
  * [Link Title](file:///path/to/related_document.md)
* **Future Extensions**: [Outline planned changes or next iterations.]

---
```

---

## 2. Link Formatting Standards

To ensure that hyperlinks render correctly across different markdown viewers and developer tools, the following formatting rules must be followed:

* **The `file:///` Path Scheme**: Links referencing repository files must use absolute paths prefixed with the `file:///` scheme.
  
  ```markdown
  # CORRECT link formatting
  [02_ARCHITECTURE_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/02_ARCHITECTURE_GUIDELINES.md)
  ```
  
  ```markdown
  # INCORRECT link formatting (breaks in some markdown parsers)
  [02_ARCHITECTURE_GUIDELINES.md](../02_ARCHITECTURE_GUIDELINES.md)
  ```

* **No Hyperlink Backticks**: Do not wrap link text in backticks. Doing so breaks markdown rendering in some tools.
  
  * *Correct*: `[naming_conventions.md](file:///Users/anzarakhtar/aios/docs/engineering/coding_standards/naming_conventions.md)`
  * *Incorrect*: `[`naming_conventions.md`](file:///Users/anzarakhtar/aios/docs/engineering/coding_standards/naming_conventions.md)`

---

## 3. Formatting Codes, Tables & Alerts

* **GitHub Alerts**: Use standard GitHub alert blocks (`> [!NOTE]`, `> [!TIP]`, `> [!IMPORTANT]`, `> [!WARNING]`, `> [!CAUTION]`) to draw attention to critical requirements or safety constraints. Do not place consecutive alerts or nest them within other elements.
* **Code Block Formatting**: Specify the language identifier in all fenced code blocks (e.g. ````python`) to enable proper syntax highlighting.
* **Tables**: Use standard markdown tables to present configuration settings, model routing rules, and file mappings clearly.

---

*Engineering Bible Documentation Standards · Personal AI OS · Sprint 8 M5 · Governed by [07_DOCUMENTATION_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/07_DOCUMENTATION_GUIDELINES.md)*
