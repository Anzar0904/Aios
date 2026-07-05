import base64
import json
import os
from typing import Dict, List, Optional

import httpx

from skills.github.models import (
    GitHubBranch,
    GitHubCommit,
    GitHubIssue,
    GitHubPR,
    GitHubRelease,
    GitHubRepo,
    GitHubTag,
    GitHubWorkflow,
)


class EncryptedConfig:
    def __init__(self, filepath: Optional[str] = None) -> None:
        if filepath is None:
            self.filepath = os.path.expanduser("~/.aios_github_config.json")
        else:
            self.filepath = filepath
        self.key = b"ai_os_secret_key_12345"

    def _xor_crypt(self, data: bytes) -> bytes:
        key_len = len(self.key)
        return bytes(data[i] ^ self.key[i % key_len] for i in range(len(data)))

    def save_token(self, token: str) -> None:
        encrypted_bytes = self._xor_crypt(token.encode("utf-8"))
        encoded_str = base64.b64encode(encrypted_bytes).decode("utf-8")
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump({"token": encoded_str}, f)

    def load_token(self) -> Optional[str]:
        if not os.path.exists(self.filepath):
            return None
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            encoded_str = data.get("token")
            if not encoded_str:
                return None
            encrypted_bytes = base64.b64decode(encoded_str)
            decrypted_bytes = self._xor_crypt(encrypted_bytes)
            return decrypted_bytes.decode("utf-8")
        except Exception:
            return None


class GitHubClient:
    def __init__(self, token: Optional[str] = None) -> None:
        self.base_url = "https://api.github.com"

        # Priority:
        # 1. Explicit token passed
        # 2. Environment variable GITHUB_TOKEN or GITHUB_PAT
        # 3. Encrypted config token
        self.token = token
        if not self.token:
            self.token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GITHUB_PAT")
        if not self.token:
            self.token = EncryptedConfig().load_token()

    def _get_headers(self) -> Dict[str, str]:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def list_repositories(self) -> List[GitHubRepo]:
        if not self.token:
            return [
                GitHubRepo(
                    name="aios",
                    owner="Anzar0904",
                    description="Personal AI OS core.",
                    url="https://github.com/Anzar0904/aios",
                ),
                GitHubRepo(
                    name="atlas",
                    owner="Anzar0904",
                    description="CLI engine for AI OS.",
                    url="https://github.com/Anzar0904/atlas",
                ),
            ]
        try:
            with httpx.Client() as client:
                res = client.get(f"{self.base_url}/user/repos", headers=self._get_headers())
                if res.status_code != 200:
                    raise Exception(f"GitHub returned status {res.status_code}")
                data = res.json()
                return [
                    GitHubRepo(
                        name=item["name"],
                        owner=item["owner"]["login"],
                        description=item.get("description"),
                        url=item["html_url"],
                        is_private=item["private"],
                    )
                    for item in data
                ]
        except Exception:
            return [
                GitHubRepo(
                    name="aios",
                    owner="Anzar0904",
                    description="Personal AI OS core.",
                    url="https://github.com/Anzar0904/aios",
                )
            ]

    def list_branches(self, owner: str, repo: str) -> List[GitHubBranch]:
        if not self.token:
            return [
                GitHubBranch(name="main", commit_sha="abc1234"),
                GitHubBranch(name="dev", commit_sha="def5678"),
            ]
        try:
            with httpx.Client() as client:
                res = client.get(
                    f"{self.base_url}/repos/{owner}/{repo}/branches", headers=self._get_headers()
                )
                if res.status_code != 200:
                    return []
                data = res.json()
                return [
                    GitHubBranch(name=item["name"], commit_sha=item["commit"]["sha"])
                    for item in data
                ]
        except Exception:
            return []

    def get_pr(self, owner: str, repo: str, number: int) -> Optional[GitHubPR]:
        if not self.token:
            return GitHubPR(
                number=number,
                title=f"Mock PR #{number}: Refactor core commands",
                state="open",
                body="This pull request moves commands to skills.",
                html_url=f"https://github.com/{owner}/{repo}/pull/{number}",
                diff_url=f"https://github.com/{owner}/{repo}/pull/{number}.diff",
            )
        try:
            with httpx.Client() as client:
                res = client.get(
                    f"{self.base_url}/repos/{owner}/{repo}/pulls/{number}",
                    headers=self._get_headers(),
                )
                if res.status_code != 200:
                    return None
                item = res.json()
                return GitHubPR(
                    number=item["number"],
                    title=item["title"],
                    state=item["state"],
                    body=item.get("body"),
                    html_url=item["html_url"],
                    diff_url=item.get("diff_url", ""),
                )
        except Exception:
            return None

    def get_pr_diff(self, owner: str, repo: str, number: int) -> str:
        if not self.token:
            return f"Mock diff content for PR #{number}\n- old_line\n+ new_line"
        try:
            headers = self._get_headers()
            headers["Accept"] = "application/vnd.github.diff"
            with httpx.Client() as client:
                res = client.get(
                    f"{self.base_url}/repos/{owner}/{repo}/pulls/{number}",
                    headers=headers,
                )
                if res.status_code == 200:
                    return res.text
                return f"Failed to fetch PR diff: status code {res.status_code}"
        except Exception as e:
            return f"Error fetching PR diff: {e}"

    def get_issue(self, owner: str, repo: str, number: int) -> Optional[GitHubIssue]:
        if not self.token:
            return GitHubIssue(
                number=number,
                title=f"Mock Issue #{number}: Bug in task scheduler",
                state="open",
                body="The scheduler occasionally crashes on startup.",
                html_url=f"https://github.com/{owner}/{repo}/issues/{number}",
            )
        try:
            with httpx.Client() as client:
                res = client.get(
                    f"{self.base_url}/repos/{owner}/{repo}/issues/{number}",
                    headers=self._get_headers(),
                )
                if res.status_code != 200:
                    return None
                item = res.json()
                return GitHubIssue(
                    number=item["number"],
                    title=item["title"],
                    state=item["state"],
                    body=item.get("body"),
                    html_url=item["html_url"],
                )
        except Exception:
            return None

    def list_workflows(self, owner: str, repo: str) -> List[GitHubWorkflow]:
        if not self.token:
            return [
                GitHubWorkflow(
                    id=101,
                    name="CI Build",
                    state="active",
                    path=".github/workflows/ci.yml",
                ),
                GitHubWorkflow(
                    id=102,
                    name="Deploy",
                    state="active",
                    path=".github/workflows/deploy.yml",
                ),
            ]
        try:
            with httpx.Client() as client:
                res = client.get(
                    f"{self.base_url}/repos/{owner}/{repo}/actions/workflows",
                    headers=self._get_headers(),
                )
                if res.status_code != 200:
                    return []
                data = res.json()
                return [
                    GitHubWorkflow(
                        id=w["id"],
                        name=w["name"],
                        state=w["state"],
                        path=w["path"],
                    )
                    for w in data.get("workflows", [])
                ]
        except Exception:
            return []

    def get_workflow_runs(self, owner: str, repo: str) -> List[dict]:
        if not self.token:
            return [
                {
                    "id": 123456,
                    "name": "CI Build",
                    "status": "completed",
                    "conclusion": "failure",
                    "html_url": f"https://github.com/{owner}/{repo}/actions/runs/123456",
                }
            ]
        try:
            with httpx.Client() as client:
                res = client.get(
                    f"{self.base_url}/repos/{owner}/{repo}/actions/runs",
                    headers=self._get_headers(),
                )
                if res.status_code == 200:
                    return res.json().get("workflow_runs", [])
                return []
        except Exception:
            return []

    def get_latest_failed_job_log(
        self, owner: str, repo: str
    ) -> tuple[Optional[str], Optional[str], Optional[str]]:
        if not self.token:
            return (
                "CI Build",
                "failure",
                "Mock error log: AssertionError: Test failed in test_kernel.py:45",
            )
        try:
            runs = self.get_workflow_runs(owner, repo)
            if not runs:
                return None, None, None
            # Find the latest run
            latest_run = runs[0]
            name = latest_run.get("name")
            conclusion = latest_run.get("conclusion")
            status = latest_run.get("status")

            if conclusion == "failure":
                run_id = latest_run["id"]
                with httpx.Client() as client:
                    res = client.get(
                        f"{self.base_url}/repos/{owner}/{repo}/actions/runs/{run_id}/jobs",
                        headers=self._get_headers(),
                    )
                    if res.status_code == 200:
                        jobs = res.json().get("jobs", [])
                        failed_jobs = [j for j in jobs if j.get("conclusion") == "failure"]
                        if failed_jobs:
                            job_id = failed_jobs[0]["id"]
                            log_res = client.get(
                                f"{self.base_url}/repos/{owner}/{repo}/actions/jobs/{job_id}/logs",
                                headers=self._get_headers(),
                            )
                            if log_res.status_code == 200:
                                return name, conclusion, log_res.text[-2000:]
            return name, conclusion or status, None
        except Exception:
            return None, None, None

    def get_latest_release(self, owner: str, repo: str) -> Optional[GitHubRelease]:
        if not self.token:
            return GitHubRelease(
                tag_name="v1.0.0",
                name="v1.0.0 Stable release",
                body="Initial stable release of AI OS.",
                published_at="2026-07-01T12:00:00Z",
            )
        try:
            with httpx.Client() as client:
                res = client.get(
                    f"{self.base_url}/repos/{owner}/{repo}/releases/latest",
                    headers=self._get_headers(),
                )
                if res.status_code != 200:
                    return None
                item = res.json()
                return GitHubRelease(
                    tag_name=item["tag_name"],
                    name=item["name"],
                    body=item.get("body"),
                    published_at=item["published_at"],
                )
        except Exception:
            return None

    def create_issue(self, owner: str, repo: str, title: str, body: str) -> Optional[GitHubIssue]:
        if not self.token:
            return GitHubIssue(
                number=999,
                title=title,
                state="open",
                body=body,
                html_url=f"https://github.com/{owner}/{repo}/issues/999",
            )
        try:
            payload = {"title": title, "body": body}
            with httpx.Client() as client:
                res = client.post(
                    f"{self.base_url}/repos/{owner}/{repo}/issues",
                    json=payload,
                    headers=self._get_headers(),
                )
                if res.status_code != 201:
                    return None
                item = res.json()
                return GitHubIssue(
                    number=item["number"],
                    title=item["title"],
                    state=item["state"],
                    body=item.get("body"),
                    html_url=item["html_url"],
                )
        except Exception:
            return None

    def create_pr(
        self, owner: str, repo: str, title: str, head: str, base: str, body: str
    ) -> Optional[GitHubPR]:
        if not self.token:
            return GitHubPR(
                number=888,
                title=title,
                state="open",
                body=body,
                html_url=f"https://github.com/{owner}/{repo}/pull/888",
                diff_url="",
            )
        try:
            payload = {"title": title, "head": head, "base": base, "body": body}
            with httpx.Client() as client:
                res = client.post(
                    f"{self.base_url}/repos/{owner}/{repo}/pulls",
                    json=payload,
                    headers=self._get_headers(),
                )
                if res.status_code != 201:
                    return None
                item = res.json()
                return GitHubPR(
                    number=item["number"],
                    title=item["title"],
                    state=item["state"],
                    body=item.get("body"),
                    html_url=item["html_url"],
                    diff_url=item.get("diff_url", ""),
                )
        except Exception:
            return None

    def compare_branches(self, owner: str, repo: str, base: str, head: str) -> str:
        if not self.token:
            return f"Mock diff content between {base} and {head}:\n- old_logic()\n+ new_logic()"
        try:
            headers = self._get_headers()
            headers["Accept"] = "application/vnd.github.diff"
            with httpx.Client() as client:
                res = client.get(
                    f"{self.base_url}/repos/{owner}/{repo}/compare/{base}...{head}",
                    headers=headers,
                )
                if res.status_code == 200:
                    return res.text
                return f"Failed to compare branches: status code {res.status_code}"
        except Exception as e:
            return f"Error comparing branches: {e}"

    def list_commits(self, owner: str, repo: str, sha: Optional[str] = None) -> List[GitHubCommit]:
        if not self.token:
            return [
                GitHubCommit(
                    sha="abc1234",
                    message="feat: implement github skill",
                    author="Dev",
                    date="2026-07-04",
                ),
                GitHubCommit(
                    sha="def5678",
                    message="fix: handle rate limit errors",
                    author="Dev",
                    date="2026-07-04",
                ),
            ]
        try:
            params = {}
            if sha:
                params["sha"] = sha
            with httpx.Client() as client:
                res = client.get(
                    f"{self.base_url}/repos/{owner}/{repo}/commits",
                    headers=self._get_headers(),
                    params=params,
                )
                if res.status_code != 200:
                    return []
                data = res.json()
                return [
                    GitHubCommit(
                        sha=item["sha"],
                        message=item["commit"]["message"],
                        author=item["commit"]["author"]["name"],
                        date=item["commit"]["author"]["date"],
                    )
                    for item in data
                ]
        except Exception:
            return []

    def list_tags(self, owner: str, repo: str) -> List[GitHubTag]:
        if not self.token:
            return [
                GitHubTag(name="v1.0.0", commit_sha="abc1234"),
                GitHubTag(name="v0.9.0", commit_sha="def5678"),
            ]
        try:
            with httpx.Client() as client:
                res = client.get(
                    f"{self.base_url}/repos/{owner}/{repo}/tags",
                    headers=self._get_headers(),
                )
                if res.status_code != 200:
                    return []
                data = res.json()
                return [
                    GitHubTag(
                        name=item["name"],
                        commit_sha=item["commit"]["sha"],
                    )
                    for item in data
                ]
        except Exception:
            return []
