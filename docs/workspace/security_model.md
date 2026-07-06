# Workspace Intelligence — Security & Trust Model
**Sprint 10 · Milestone 1 (Foundation)** · Version 1.0 · July 2026

---

## Document Metadata
* **Purpose**: Define path verification protocols, CLI command sanitizers, process containment boundaries, and credential safeguards.
* **Scope**: Dictates system validation rules for workspace execution tools and terminal shells.
* **Audience**: Security Auditors, System Architects, and Integration Developers.
* **Related Documents**:
  * [05_SECURITY_GUIDELINES.md](file:///Users/anzarakhtar/aios/docs/05_SECURITY_GUIDELINES.md) - Core system security.
  * [workspace/workspace_intelligence.md](file:///Users/anzarakhtar/aios/docs/workspace/workspace_intelligence.md) - Conceptual vision.

---

## 1. Zero-Trust Path Containment

To prevent malicious directory traversal attacks, where a compromised agent tries to read or modify files outside the development workspace (e.g., accessing `/etc/passwd` or ssh keys under `~/.ssh`), Workspace Intelligence enforces **strict path containment checks**:

```python
# Canonical path check implementation
def check_path_containment(workspace_root: str, target_path: str) -> bool:
    """Verify that target_path resolves strictly within workspace_root."""
    resolved_root = os.path.realpath(workspace_root)
    resolved_target = os.path.realpath(target_path)
    
    # Check if target is a subdirectory of root
    common_prefix = os.path.commonpath([resolved_root, resolved_target])
    return common_prefix == resolved_root
```

* **Absolute Resolution**: All paths are resolved to their canonical real path before checks, resolving symlinks, relative segments (`..`), and aliases.
* **Verification Gates**: The `LocalWorkspace` adapter intercepts all reads and writes, raising a `SecurityBoundaryViolation` error if validation fails.

---

## 2. Command Sanitization & Sandboxing

The terminal tool executes shell commands in a wrapped sandbox, enforcing strict rules:

### 2.1 Blacklisted Tokens
The CLI runner scans command strings for high-risk tokens and shell structures, blocking execution if matches occur:
```
- Destructive commands: rm -rf /, rm -rf ~
- System directories access: /etc, /var/log, /private
- Background daemon forks: nohup, systemctl, service, cron
- Arbitrary script pipe downloads: curl * | bash, wget * | sh
```

### 2.2 Shell Argument Sanitization
Commands are parsed into discrete token arrays using Python's `shlex.split`, avoiding raw shell evaluations (`subprocess.Popen(..., shell=False)`). This prevents injection attacks where commands are concatenated using `;`, `&&`, or `|` operators.

### 2.3 Sandbox Limits
* **Timeout Guards**: All commands run with an absolute timeout limit (defaulting to 300 seconds) to prevent infinite loops.
* **Environment Cleanse**: The system strip-down environment variables, removing access keys, cloud credentials, or shell credentials unless explicitly whitelisted.
* **Resource Quotas**: Command processes are restricted using OS limits (`rlimit`), restricting max memory usage, file creation size, and thread counts.

---

## 3. Credential Isolation

* **SSH Key Isolation**: AI OS agent tools are strictly blocked from listing, reading, or reading directories matching `/Users/*/.ssh/` or `/root/.ssh/`.
* **Git Token Isolation**: Git commands use local SSH agent keys or system keychain helpers. Staging tokens are never stored as plaintext in git configurations, preventing accidental leakage.

---

## 4. Human-in-the-Loop Approval Matrix

The **Approval Engine** triggers validation challenges based on operation risks:

```
+------------------+-----------------------+---------------------------------------+
| Operation Risk   | Representative Action | Required Approval Loop                |
+------------------+-----------------------+---------------------------------------+
| Low Risk         | Read file, git status | Auto-allow (log to REPL console).     |
+------------------+-----------------------+---------------------------------------+
| Medium Risk      | Edit file, run tests  | Prompt developer in terminal with     |
|                  |                       | file diffs / command arguments.       |
+------------------+-----------------------+---------------------------------------+
| High Risk        | git commit, install   | Explicit keyboard verification [y/N]  |
|                  | packages              | by the user.                          |
+------------------+-----------------------+---------------------------------------+
| Critical Risk    | git push --force,     | High-level prompt requiring text      |
|                  | branch deletion       | confirmation code (e.g. "CONFIRM").   |
+------------------+-----------------------+---------------------------------------+
```
