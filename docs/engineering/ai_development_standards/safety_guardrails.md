# Security Guardrails & Risk Gating
**Engineering Bible — Milestone 6**
**Version 1.0** · *Classified: For One Person Only* · *July 2026*

---

## 1. Path Containment Checks

To prevent path traversal attacks, all file operations must resolve target paths and verify containment within the active workspace root.

### Path Safety Code Pattern
* **Canonical Resolution**: Convert paths to absolute paths using `.resolve()`.
* **Containment Verification**: Check that target paths reside within the workspace using `.is_relative_to(workspace_root)`. Symbolic links that point outside the workspace must be blocked.

```python
from pathlib import Path

def validate_workspace_path(target_path: str, workspace_root: str) -> Path:
    """
    Validates that the target path is resolved and contained in the workspace.
    """
    resolved_root = Path(workspace_root).resolve()
    resolved_target = Path(target_path).resolve()
    
    if not resolved_target.is_relative_to(resolved_root):
        raise PermissionError(f"Access denied: target path {resolved_target} is outside workspace")
        
    return resolved_target
```

---

## 2. Command Execution Safety

To prevent command injection:
* **Disable Shell Execution**: All subprocess executions must run with `shell=False`.
* **Argument Splitting**: Input arguments must be parsed and split using `shlex.split()` before being passed to `subprocess.run()`.
* **Command Whitelisting**: Subprocesses must only execute whitelisted CLI binaries (`git`, `pytest`, `ruff`). Other binaries must be blocked.

```python
import shlex
import subprocess

def safe_run_command(cmd_string: str) -> subprocess.CompletedProcess:
    """
    Safely executes a whitelisted CLI command.
    """
    args = shlex.split(cmd_string)
    if args[0] not in ["git", "pytest", "ruff"]:
        raise ValueError(f"Command binary {args[0]} is not in the whitelist")
        
    return subprocess.run(args, shell=False, capture_output=True)
```

---

## 3. Risk Gating & Approval Workflows

Mutating operations are categorized by risk level to determine when user approval is required:

| Risk Category | Example Operations | Gating Requirement |
|---------------|--------------------|---------------------|
| **`LOW`** | File reading, listing directories, check git status. | Execute automatically. |
| **`MEDIUM`** | Workspace file writes/edits, staging git changes. | Execute with logging. |
| **`HIGH`** | Deleting files, modifying files outside the workspace, running terminal scripts. | Require user confirmation. |

HIGH-risk operations must prompt the user for confirmation via the CLI before execution. The approval engine logs details of the request and the user's decision.

---

*Engineering Bible AI Development Standards · Personal AI OS · Sprint 8 M6 · Governed by [04_AI_MODEL_STRATEGY.md](file:///Users/anzarakhtar/aios/docs/04_AI_MODEL_STRATEGY.md)*
