"""
GitHub Memory — Sprint 25.

Persists repository metadata, recent PRs, issues, branches, releases, and
workflow run history to .aios_github_cache/ so the intelligence engine can
work incrementally without re-fetching unchanged data.
"""

import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

_CACHE_DIR = Path(".aios_github_cache")
_CACHE_DIR.mkdir(exist_ok=True)


class GitHubMemory:
    """Persistent in-process cache for GitHub Intelligence metadata."""

    def __init__(self, cache_dir: Optional[str] = None) -> None:
        self._dir = Path(cache_dir) if cache_dir else _CACHE_DIR
        self._dir.mkdir(parents=True, exist_ok=True)

    def _repo_file(self, repo_name: str) -> Path:
        safe = repo_name.replace("/", "__")
        return self._dir / f"repo_{safe}.json"

    # ── Repository metadata ──────────────────────────────────────────────────

    def save_repo(self, repo_name: str, data: Dict[str, Any]) -> None:
        record = {"saved_at": time.time(), "repo": data}
        self._repo_file(repo_name).write_text(json.dumps(record, indent=2), encoding="utf-8")

    def load_repo(self, repo_name: str) -> Optional[Dict[str, Any]]:
        f = self._repo_file(repo_name)
        if f.exists():
            try:
                return json.loads(f.read_text(encoding="utf-8")).get("repo")
            except Exception:
                pass
        return None

    # ── Recent PRs ───────────────────────────────────────────────────────────

    def save_prs(self, repo_name: str, prs: List[Dict[str, Any]]) -> None:
        f = self._dir / f"prs_{repo_name.replace('/', '__')}.json"
        f.write_text(json.dumps({"saved_at": time.time(), "prs": prs}, indent=2), encoding="utf-8")

    def load_prs(self, repo_name: str) -> List[Dict[str, Any]]:
        f = self._dir / f"prs_{repo_name.replace('/', '__')}.json"
        if f.exists():
            try:
                return json.loads(f.read_text(encoding="utf-8")).get("prs", [])
            except Exception:
                pass
        return []

    # ── Recent Issues ────────────────────────────────────────────────────────

    def save_issues(self, repo_name: str, issues: List[Dict[str, Any]]) -> None:
        f = self._dir / f"issues_{repo_name.replace('/', '__')}.json"
        f.write_text(
            json.dumps({"saved_at": time.time(), "issues": issues}, indent=2), encoding="utf-8"
        )

    def load_issues(self, repo_name: str) -> List[Dict[str, Any]]:
        f = self._dir / f"issues_{repo_name.replace('/', '__')}.json"
        if f.exists():
            try:
                return json.loads(f.read_text(encoding="utf-8")).get("issues", [])
            except Exception:
                pass
        return []

    # ── Branches ─────────────────────────────────────────────────────────────

    def save_branches(self, repo_name: str, branches: List[Dict[str, Any]]) -> None:
        f = self._dir / f"branches_{repo_name.replace('/', '__')}.json"
        f.write_text(
            json.dumps({"saved_at": time.time(), "branches": branches}, indent=2), encoding="utf-8"
        )

    def load_branches(self, repo_name: str) -> List[Dict[str, Any]]:
        f = self._dir / f"branches_{repo_name.replace('/', '__')}.json"
        if f.exists():
            try:
                return json.loads(f.read_text(encoding="utf-8")).get("branches", [])
            except Exception:
                pass
        return []

    # ── Releases ─────────────────────────────────────────────────────────────

    def save_releases(self, repo_name: str, releases: List[Dict[str, Any]]) -> None:
        f = self._dir / f"releases_{repo_name.replace('/', '__')}.json"
        f.write_text(
            json.dumps({"saved_at": time.time(), "releases": releases}, indent=2), encoding="utf-8"
        )

    def load_releases(self, repo_name: str) -> List[Dict[str, Any]]:
        f = self._dir / f"releases_{repo_name.replace('/', '__')}.json"
        if f.exists():
            try:
                return json.loads(f.read_text(encoding="utf-8")).get("releases", [])
            except Exception:
                pass
        return []

    # ── Workflow runs ────────────────────────────────────────────────────────

    def save_workflows(self, repo_name: str, runs: List[Dict[str, Any]]) -> None:
        f = self._dir / f"workflows_{repo_name.replace('/', '__')}.json"
        f.write_text(
            json.dumps({"saved_at": time.time(), "runs": runs}, indent=2), encoding="utf-8"
        )

    def load_workflows(self, repo_name: str) -> List[Dict[str, Any]]:
        f = self._dir / f"workflows_{repo_name.replace('/', '__')}.json"
        if f.exists():
            try:
                return json.loads(f.read_text(encoding="utf-8")).get("runs", [])
            except Exception:
                pass
        return []

    # ── List all cached repos ────────────────────────────────────────────────

    def list_cached_repos(self) -> List[str]:
        return [
            f.stem.replace("repo_", "").replace("__", "/") for f in self._dir.glob("repo_*.json")
        ]
