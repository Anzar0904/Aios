import os
import subprocess
from pathlib import Path
from typing import Any, Dict, List

from aios.services.developer_workspace import DeveloperWorkspaceInfo, DeveloperWorkspaceService


class LocalDeveloperWorkspace(DeveloperWorkspaceService):
    def initialize(self) -> None:
        pass

    def get_workspace_info(self, workspace_root: str) -> DeveloperWorkspaceInfo:
        root_path = Path(workspace_root).resolve()

        # 1. Resolve Git information
        git_status = ""
        git_diff_summary = ""
        staged_files: List[str] = []
        unstaged_files: List[str] = []
        untracked_files: List[str] = []
        git_branch = None

        try:
            # Git status --porcelain
            res_status = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=str(root_path),
                capture_output=True,
                text=True,
                shell=False
            )
            if res_status.returncode == 0:
                git_status = res_status.stdout.strip()
                for line in res_status.stdout.splitlines():
                    if len(line) < 4:
                        continue
                    code = line[:2]
                    filepath = line[3:].strip().strip('"')
                    
                    if code[0] in ("A", "M", "R", "C"):
                        staged_files.append(filepath)
                    if code[1] in ("M", "D"):
                        unstaged_files.append(filepath)
                    if code == "??":
                        untracked_files.append(filepath)

            # Git diff --stat
            res_diff = subprocess.run(
                ["git", "diff", "--stat"],
                cwd=str(root_path),
                capture_output=True,
                text=True,
                shell=False
            )
            if res_diff.returncode == 0:
                git_diff_summary = res_diff.stdout.strip()

            # Git branch
            res_branch = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=str(root_path),
                capture_output=True,
                text=True,
                shell=False
            )
            if res_branch.returncode == 0:
                git_branch = res_branch.stdout.strip()

        except Exception:
            pass

        # 2. Test Discovery
        detected_tests: List[str] = []
        default_ignores = {".git", "node_modules", ".venv", "venv", "__pycache__", "dist", "build"}
        try:
            for current_root, dirs, files in os.walk(root_path):
                current_path = Path(current_root)
                rel_dir = current_path.relative_to(root_path)
                if any(p in default_ignores for p in rel_dir.parts):
                    continue
                dirs[:] = [d for d in dirs if d not in default_ignores]

                for file in files:
                    if (file.startswith("test_") and file.endswith(".py")) or file.endswith("_test.py"):
                        detected_tests.append(str(rel_dir / file))
                    elif file.endswith(".test.js") or file.endswith(".spec.ts"):
                        detected_tests.append(str(rel_dir / file))
        except Exception:
            pass

        # 3. Build systems & linters detection
        build_systems: List[str] = []
        linters: List[str] = []

        try:
            if (root_path / "pyproject.toml").is_file():
                build_systems.append("poetry")
                content = (root_path / "pyproject.toml").read_text(encoding="utf-8", errors="ignore")
                if "ruff" in content:
                    linters.append("ruff")
                if "black" in content:
                    linters.append("black")

            if (root_path / "package.json").is_file():
                build_systems.append("npm/yarn")
                content = (root_path / "package.json").read_text(encoding="utf-8", errors="ignore")
                if "eslint" in content:
                    linters.append("eslint")

            if (root_path / "Cargo.toml").is_file():
                build_systems.append("cargo")
                linters.append("clippy")

            if (root_path / "go.mod").is_file():
                build_systems.append("go")
        except Exception:
            pass

        # 4. Workspace diagnostics
        diagnostics = {
            "uncommitted_files_count": len(staged_files) + len(unstaged_files),
            "untracked_files_count": len(untracked_files),
            "tests_count": len(detected_tests),
        }

        return DeveloperWorkspaceInfo(
            git_status=git_status,
            git_diff_summary=git_diff_summary,
            staged_files=staged_files,
            unstaged_files=unstaged_files,
            untracked_files=untracked_files,
            detected_tests=detected_tests,
            build_systems=build_systems,
            linters=linters,
            diagnostics=diagnostics,
            extra={"git_branch": git_branch}
        )

    def execute_safe_command(self, command: str, args: List[str], workspace_root: str) -> Dict[str, Any]:
        whitelist = {"pytest", "ruff", "black", "npm", "cargo"}
        if command not in whitelist:
            return {"success": False, "error": f"Command '{command}' is not whitelisted."}

        # Check metacharacters for command injection mitigation
        metacharacters = {";", "&", "|", "<", ">", "$", "(", ")", "`", "\n"}
        for arg in args:
            if any(char in arg for char in metacharacters):
                return {"success": False, "error": f"Safety check failed: suspicious character in argument '{arg}'"}

        try:
            full_command = [command] + args
            res = subprocess.run(
                full_command,
                cwd=workspace_root,
                capture_output=True,
                text=True,
                shell=False
            )
            return {
                "success": True,
                "returncode": res.returncode,
                "stdout": res.stdout,
                "stderr": res.stderr
            }
        except Exception as e:
            return {"success": False, "error": f"Execution failed: {str(e)}"}
