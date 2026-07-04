import subprocess
import os
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


from aios.providers.models import DIInitializeMixin


class LocalGitExecutor(DIInitializeMixin):
    """Wrapper executing native git CLI shell subprocess commands inside target working directories."""

    def __init__(self, workspace_root: Optional[str] = None) -> None:
        self.workspace_root = workspace_root or os.getcwd()

    def run_git(self, args: List[str], cwd: Optional[str] = None) -> str:
        target_cwd = cwd or self.workspace_root
        cmd = ["git"] + args
        try:
            res = subprocess.run(cmd, cwd=target_cwd, capture_output=True, text=True, check=True)
            return res.stdout.strip()
        except subprocess.CalledProcessError as e:
            logger.error(f"Git execution failed: {e.cmd} -> {e.stderr.strip()}")
            raise ValueError(f"Git command failed: {e.stderr.strip()}")

    def clone(self, url: str, path: str) -> str:
        # Runs 'git clone <url> <path>'
        cmd = ["clone", url, path]
        # Make parent directory if needed
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        return self.run_git(cmd, cwd=os.path.dirname(os.path.abspath(path)))

    def init(self, path: str) -> str:
        cmd = ["init", path]
        os.makedirs(path, exist_ok=True)
        return self.run_git(cmd, cwd=path)

    def status(self, cwd: Optional[str] = None) -> str:
        return self.run_git(["status"], cwd=cwd)

    def fetch(self, remote: str = "origin", cwd: Optional[str] = None) -> str:
        return self.run_git(["fetch", remote], cwd=cwd)

    def pull(self, remote: str = "origin", branch: str = "main", cwd: Optional[str] = None) -> str:
        return self.run_git(["pull", remote, branch], cwd=cwd)

    def push(self, remote: str = "origin", branch: str = "main", cwd: Optional[str] = None) -> str:
        return self.run_git(["push", remote, branch], cwd=cwd)

    def checkout(self, target: str, cwd: Optional[str] = None) -> str:
        return self.run_git(["checkout", target], cwd=cwd)

    def switch(self, branch_name: str, cwd: Optional[str] = None) -> str:
        return self.run_git(["switch", branch_name], cwd=cwd)

    def create_branch(self, branch_name: str, cwd: Optional[str] = None) -> str:
        return self.run_git(["checkout", "-b", branch_name], cwd=cwd)

    def delete_branch(self, branch_name: str, force: bool = False, cwd: Optional[str] = None) -> str:
        flag = "-D" if force else "-d"
        return self.run_git(["branch", flag, branch_name], cwd=cwd)

    def merge(self, source_branch: str, cwd: Optional[str] = None) -> str:
        return self.run_git(["merge", source_branch], cwd=cwd)

    def rebase(self, upstream: str, cwd: Optional[str] = None) -> str:
        return self.run_git(["rebase", upstream], cwd=cwd)

    def cherry_pick(self, sha: str, cwd: Optional[str] = None) -> str:
        return self.run_git(["cherry-pick", sha], cwd=cwd)

    def stash_push(self, message: Optional[str] = None, cwd: Optional[str] = None) -> str:
        cmd = ["stash", "push"]
        if message:
            cmd += ["-m", message]
        return self.run_git(cmd, cwd=cwd)

    def stash_pop(self, cwd: Optional[str] = None) -> str:
        return self.run_git(["stash", "pop"], cwd=cwd)

    def restore(self, path: str, cwd: Optional[str] = None) -> str:
        return self.run_git(["restore", path], cwd=cwd)

    def reset(self, target: str, mode: str = "--hard", cwd: Optional[str] = None) -> str:
        return self.run_git(["reset", mode, target], cwd=cwd)

    def tag(self, name: str, message: Optional[str] = None, cwd: Optional[str] = None) -> str:
        cmd = ["tag", name]
        if message:
            cmd += ["-a", "-m", message]
        return self.run_git(cmd, cwd=cwd)

    def stage(self, path: str, cwd: Optional[str] = None) -> str:
        return self.run_git(["add", path], cwd=cwd)

    def unstage(self, path: str, cwd: Optional[str] = None) -> str:
        return self.run_git(["reset", "HEAD", path], cwd=cwd)

    def commit(self, message: str, amend: bool = False, cwd: Optional[str] = None) -> str:
        cmd = ["commit"]
        if amend:
            cmd.append("--amend")
        cmd += ["-m", message]
        return self.run_git(cmd, cwd=cwd)

    def diff(self, base: Optional[str] = None, head: Optional[str] = None, cwd: Optional[str] = None) -> str:
        cmd = ["diff"]
        if base and head:
            cmd.append(f"{base}..{head}")
        elif base:
            cmd.append(base)
        return self.run_git(cmd, cwd=cwd)

    def log(self, max_count: int = 20, cwd: Optional[str] = None) -> str:
        return self.run_git(["log", f"-n", str(max_count), "--oneline"], cwd=cwd)

    def detect_conflicts(self, cwd: Optional[str] = None) -> List[str]:
        """Scans workspace for conflict marker tags."""
        conflict_files = []
        try:
            # git diff --name-only --diff-filter=U lists unmerged files
            out = self.run_git(["diff", "--name-only", "--diff-filter=U"], cwd=cwd)
            if out:
                conflict_files = [line.strip() for line in out.split("\n") if line.strip()]
        except Exception:
            pass
        return conflict_files
