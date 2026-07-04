# AI OS Security Documentation: Filesystem and Terminal Tool Safeguards

This documentation outlines the security mitigations implemented in Personal AI OS v0.2 to address critical Path Traversal and Command Injection vulnerabilities in the Tool Engine.

---

## 1. Filesystem Path Traversal Mitigation

### Vulnerability Context
Previously, `FilesystemTool` allowed directory traversal, absolute path usage, and symbolic link dereferencing that could read or modify arbitrary files outside the active workspace (e.g., `/etc/passwd`, home directory files, or `.env` secrets).

### Resolution Strategy
We introduced a centralized validation module in [security.py](file:///Users/anzarakhtar/aios/core/src/aios/services/security.py) implementing a strict path-containment validation function `validate_workspace_path`.

1. **Active Workspace Resolution**:
   - The active workspace root is resolved dynamically by subscribing the `LocalToolManager` to `ContextLoadedEvent` and `SessionStartedEvent`.
   - The verified workspace root path is supplied as a provider callback to `FilesystemTool`.

2. **Normalize and Resolve**:
   - Every file path argument is resolved using Python's `Path(path_str).resolve()`. This resolves relative path segments (such as `../`) and dereferences symlinks to their canonical target.

3. **Workspace Boundary Check**:
   - Using `Path.is_relative_to(workspace_root)`, the resolved canonical path is checked to guarantee it lies inside the active workspace boundary.
   - Symbolic links pointing outside the workspace are successfully detected and blocked.

4. **Information Disclosure Prevention**:
   - Structured error messages are returned (e.g., `"Access denied: path escapes workspace."` or `"Invalid path format."`).
   - Detailed OS level exceptions or file paths are **never** exposed back to the caller/LLM to prevent leakage.

---

## 2. Command Injection Mitigation (Terminal Tool)

### Vulnerability Context
Previously, the `TerminalTool` executed commands via `subprocess.run(command, shell=True)` after filtering them with a simple keyword blacklist. This was highly vulnerable to command injection bypasses (e.g., variable padding, whitespace padding, chaining, etc.).

### Resolution Strategy
1. **Disable Shell Execution**:
   - Replaced `shell=True` with `shell=False` to execute executables directly as argument arrays, bypassing shell parsing rules.

2. **Strict Command Parsing**:
   - Parsing the incoming command string safely using `shlex.split()`.

3. **Strict Whitelisting**:
   - Execution is limited to a whitelist of approved commands: `{"echo", "pwd", "whoami", "git"}`. Any other command is immediately rejected.

4. **Metacharacter & Chaining Rejection**:
   - Any command containing characters like `;`, `&`, `|`, `<`, `>`, `$`, `(`, `)`, `` ` ``, `\`, `*`, `?`, `[`, `]`, `!`, `{`, `}`, `\n`, or `\r` is rejected before parsing.

5. **Subcommand Validation**:
   - `pwd` and `whoami` commands cannot take arguments.
   - `git` commands are validated against a strict read/status subcommand whitelist: `{"status", "branch", "log", "diff", "show", "rev-parse", "version", "help"}`.
