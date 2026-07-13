"""
GitHub Connection Manager — Sprint 25.

Responsibilities:
- Credential loading (PAT / GITHUB_TOKEN env var)
- Connection testing (ping /user endpoint)
- User info retrieval
- Organisation listing
- Repository discovery for authenticated user
"""

import json
import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger(__name__)

_STATE_FILE = Path(".aios_github_cache/connection_state.json")
_STATE_FILE.parent.mkdir(exist_ok=True)

_API_BASE = "https://api.github.com"
_DEFAULT_HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}


class GitHubConnectionManager:
    """Manages GitHub authentication, connection state, and user/org discovery."""

    def __init__(self, token: Optional[str] = None) -> None:
        self._token = token or os.environ.get("GITHUB_TOKEN") or os.environ.get("GITHUB_PAT")
        self._state: Dict[str, Any] = self._load_state()

    # ── State persistence ────────────────────────────────────────────────────

    def _load_state(self) -> Dict[str, Any]:
        if _STATE_FILE.exists():
            try:
                return json.loads(_STATE_FILE.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {
            "connected": False,
            "user": None,
            "token_hint": None,
            "last_connected": None,
        }

    def _save_state(self, state: Dict[str, Any]) -> None:
        _STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")
        self._state = state

    # ── HTTP helper ──────────────────────────────────────────────────────────

    def _headers(self) -> Dict[str, str]:
        h = dict(_DEFAULT_HEADERS)
        if self._token:
            h["Authorization"] = f"Bearer {self._token}"
        return h

    def _get(self, path: str, params: Optional[Dict] = None) -> Any:
        url = f"{_API_BASE}/{path.lstrip('/')}"
        with httpx.Client(timeout=10.0) as client:
            res = client.get(url, headers=self._headers(), params=params or {})
        if res.status_code == 401:
            raise PermissionError("GitHub authentication failed — invalid or missing token.")
        res.raise_for_status()
        return res.json()

    # ── Public interface ─────────────────────────────────────────────────────

    def login(self, token: Optional[str] = None) -> Dict[str, Any]:
        """
        Test credentials and persist connection state.
        Returns dict with keys: success, user, message.
        """
        if token:
            self._token = token

        try:
            user_data = self._get("user")
            login = user_data.get("login", "unknown")
            name = user_data.get("name") or login
            hint = f"{self._token[:4]}…" if self._token else "none"
            state = {
                "connected": True,
                "user": login,
                "name": name,
                "token_hint": hint,
                "last_connected": time.time(),
            }
            self._save_state(state)
            return {
                "success": True,
                "user": login,
                "name": name,
                "message": f"Logged in as {login}",
            }
        except Exception as e:
            return {"success": False, "user": None, "message": str(e)}

    def logout(self) -> None:
        """Clear stored connection state."""
        self._save_state(
            {
                "connected": False,
                "user": None,
                "token_hint": None,
                "last_connected": None,
            }
        )

    def get_status(self) -> Dict[str, Any]:
        """Return current connection state without making a new API call."""
        return dict(self._state)

    def get_user_info(self) -> Dict[str, Any]:
        """Fetch live user profile from GitHub API."""
        try:
            return self._get("user")
        except Exception as e:
            return {"error": str(e)}

    def list_user_repos(
        self,
        visibility: str = "all",
        sort: str = "updated",
        per_page: int = 30,
    ) -> List[Dict[str, Any]]:
        """List repositories for the authenticated user."""
        try:
            return self._get(
                "user/repos",
                params={"visibility": visibility, "sort": sort, "per_page": per_page},
            )
        except Exception as e:
            logger.warning(f"list_user_repos failed: {e}")
            return []

    def list_orgs(self) -> List[Dict[str, Any]]:
        """List organisations the authenticated user belongs to."""
        try:
            return self._get("user/orgs")
        except Exception as e:
            logger.warning(f"list_orgs failed: {e}")
            return []

    def test_connection(self) -> Dict[str, Any]:
        """Ping the GitHub API and return latency + status."""
        try:
            start = time.time()
            data = self._get("user")
            latency_ms = (time.time() - start) * 1000.0
            return {
                "reachable": True,
                "user": data.get("login"),
                "latency_ms": round(latency_ms, 2),
            }
        except Exception as e:
            return {"reachable": False, "error": str(e), "latency_ms": 0.0}

    @property
    def is_authenticated(self) -> bool:
        return bool(self._token)

    @property
    def current_user(self) -> Optional[str]:
        return self._state.get("user")
