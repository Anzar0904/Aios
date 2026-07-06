# Build Systems & Compiler Integration Spec
**Sprint 10 · Milestone 5** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define technical interfaces for invoking local build chains and parsing compiler diagnostics.
* **Scope**: Governs build task runners, error parsers, and diagnostic schemas.
* **Audience**: Systems Integrators, DBAs, and Lead Developers.
* **Related Documents**:
  * [workspace/capabilities.md](file:///Users/anzarakhtar/aios/docs/workspace/capabilities.md) - Capabilities domains.
  * [workspace/development_tools/terminal_management.md](file:///Users/anzarakhtar/aios/docs/workspace/terminal_management.md) - Terminal execution.

---

## 1. Compiler Toolchains Coordination

The **Build Systems** module coordinates compile commands and watches file trees:
* **Cargo**: Runs `cargo build` / `cargo check`, parsing stdout/stderr lines.
* **Npm / Webpack / Next**: Runs `npm run build`, capturing error messages.
* **Make / CMake**: Invokes compiler targets, monitoring exit codes.

```
[Agent: Build Codebase] ===> BuildManager
                                    |
                           [Identify Toolchain] (e.g. pyproject.toml -> Poetry)
                                    |
                            [Execute Command] ===> run poetry build
                                    |
                           [Stdout/Stderr Stream]
                                    |
                           [Regex Log Parser] ===> Isolate errors & warnings
                                    |
                        [Map Diagnostic Entities] ===> Tag target files and lines
```

---

## 2. Compile Log Diagnostic Parsing

To help agents correct syntax errors, compiler log lines are parsed using regex definition patterns:
* **Error Patterns**: Matches standard formats:
  * GCC/Clang: `filename:line:column: error: message`
  * Rustc: `error[E0xxx]: message ... --> filename:line:column`
  * Python Traceback: `File "filename", line line_number, in symbol ...`
* **Diagnostic Struct Mappings**:
  ```python
  @dataclass
  class BuildDiagnostic:
      file_path: str
      line_number: int
      severity: str  # 'ERROR', 'WARNING'
      message: str
      error_code: Optional[str]
  ```

---

## 3. Diagnostic Code Symbol Tagging

Parsed diagnostics are mapped to the codebase symbol catalog:
1. Locate the file path and line number in the `BuildDiagnostic`.
2. Query the `codebase_symbols` table to find the class or function scope containing that line.
3. Tag the symbol with the diagnostic (e.g. `def sync_document` contains a syntax warning). This lets the agent query target scopes directly to resolve build issues.
