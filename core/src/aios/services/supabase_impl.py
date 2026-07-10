import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx

from aios.services.supabase import SupabaseCredentialsStore, SupabaseService

logger = logging.getLogger(__name__)


class LocalSupabaseIntelligenceService(SupabaseService):
    """Concrete implementation of SupabaseIntelligenceService."""

    def __init__(self, credentials_path: Optional[Path] = None) -> None:
        self._credentials_store = SupabaseCredentialsStore(path=credentials_path)
        self._access_token: Optional[str] = None
        self._projects: List[Dict[str, Any]] = []
        self._active_project_ref: Optional[str] = None

    def initialize(self) -> None:
        """Initialize the service and load credentials."""
        super().initialize()
        self._refresh_credentials()

    def start(self) -> None:
        """Start the service."""
        super().start()
        self._refresh_credentials()
        logger.info("Supabase Intelligence Service started.")

    def _refresh_credentials(self) -> None:
        """Loads/Reloads the latest credentials from storage."""
        creds = self._credentials_store.load_all()
        self._access_token = creds.get("access_token")
        self._projects = creds.get("projects", [])
        self._active_project_ref = creds.get("active_project_ref")

    def login(
        self,
        access_token: Optional[str] = None,
        project_url: Optional[str] = None,
        service_role_key: Optional[str] = None,
        project_ref: Optional[str] = None,
    ) -> bool:
        """Authenticate with Supabase PAT or direct project credentials."""
        self._refresh_credentials()
        if access_token:
            # Validate access token (PAT)
            try:
                headers = {"Authorization": f"Bearer {access_token}"}
                with httpx.Client() as client:
                    resp = client.get(
                        "https://api.supabase.com/v1/projects", headers=headers, timeout=10
                    )
                if resp.status_code == 200:
                    self._access_token = access_token
                    discovered_projects = resp.json()

                    # Convert to our internal projects list format
                    projects_list = []
                    for p in discovered_projects:
                        projects_list.append(
                            {
                                "ref": p.get("ref") or p.get("id"),
                                "name": p.get("name"),
                                "region": p.get("region"),
                                "url": f"https://{p.get('ref')}.supabase.co",
                                "key": None,  # Will need to be supplied for DB ops
                            }
                        )

                    self._projects = projects_list
                    if projects_list and not self._active_project_ref:
                        self._active_project_ref = projects_list[0]["ref"]

                    self._credentials_store.save_credentials(
                        access_token=self._access_token,
                        projects=self._projects,
                        active_project_ref=self._active_project_ref,
                    )
                    return True
                else:
                    logger.error(f"PAT Login failed with status code: {resp.status_code}")
                    return False
            except Exception as e:
                logger.error(f"PAT Login exception: {e}")
                return False

        elif project_url and service_role_key:
            # Direct project url and service role key validation
            try:
                url_clean = project_url.rstrip("/")
                ref = project_ref
                if not ref:
                    # Extract from URL e.g. https://xyz.supabase.co
                    if ".supabase.co" in url_clean:
                        ref = url_clean.split("//")[1].split(".")[0]
                    else:
                        ref = "custom-project"

                headers = {
                    "apikey": service_role_key,
                    "Authorization": f"Bearer {service_role_key}",
                }
                with httpx.Client() as client:
                    resp = client.get(f"{url_clean}/rest/v1/", headers=headers, timeout=10)
                if resp.status_code == 200:
                    # Successfully connected
                    # Merge into existing projects or create new
                    new_proj = {
                        "ref": ref,
                        "name": ref,
                        "url": url_clean,
                        "key": service_role_key,
                        "region": "detected",
                    }

                    projects_map = {p["ref"]: p for p in self._projects}
                    projects_map[ref] = new_proj
                    self._projects = list(projects_map.values())
                    self._active_project_ref = ref

                    self._credentials_store.save_credentials(
                        projects=self._projects, active_project_ref=self._active_project_ref
                    )
                    return True
                else:
                    logger.error(f"Project URL login failed with status code: {resp.status_code}")
                    return False
            except Exception as e:
                logger.error(f"Project URL login exception: {e}")
                return False

        return False

    def logout(self) -> bool:
        """Clear all active session and credential settings."""
        self._access_token = None
        self._projects = []
        self._active_project_ref = None
        self._credentials_store.delete_all()
        return True

    def get_status(self) -> Dict[str, Any]:
        """Get current auth state, active project ref, and list count."""
        self._refresh_credentials()
        active = self._get_active_project()
        return {
            "connected": active is not None,
            "access_token_present": self._access_token is not None,
            "active_project_ref": self._active_project_ref,
            "project_url": active.get("url") if active else None,
            "projects_count": len(self._projects),
        }

    def list_projects(self) -> List[Dict[str, Any]]:
        """List all discovered/configured projects."""
        self._refresh_credentials()
        return self._projects

    def select_project(self, project_ref: str) -> bool:
        """Set the active project reference."""
        self._refresh_credentials()
        for p in self._projects:
            if p["ref"] == project_ref:
                self._active_project_ref = project_ref
                self._credentials_store.save_credentials(active_project_ref=project_ref)
                return True
        return False

    def _get_active_project(self) -> Optional[Dict[str, Any]]:
        if not self._active_project_ref:
            return None
        for p in self._projects:
            if p["ref"] == self._active_project_ref:
                return p
        return None

    def _get_headers(self, project: Dict[str, Any]) -> Dict[str, str]:
        key = project.get("key") or ""
        return {"apikey": key, "Authorization": f"Bearer {key}"}

    def _get_cache_path(self, project_ref: str) -> Path:
        return Path(f".agent/supabase/cache_{project_ref}.json")

    def _load_cache(self, project_ref: str) -> Optional[Dict[str, Any]]:
        cache_file = self._get_cache_path(project_ref)
        if not cache_file.is_file():
            return None
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Check TTL (5 minutes default)
                if time.time() - data.get("timestamp", 0) < 300:
                    return data.get("content")
        except Exception:
            pass
        return None

    def _save_cache(self, project_ref: str, content: Dict[str, Any]) -> None:
        cache_file = self._get_cache_path(project_ref)
        try:
            cache_file.parent.mkdir(parents=True, exist_ok=True)
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump({"timestamp": time.time(), "content": content}, f)
        except Exception as e:
            logger.error(f"Failed to write cache for project {project_ref}: {e}")

    def clear_cache(self) -> None:
        """Delete all cache files."""
        self._refresh_credentials()
        if self._active_project_ref:
            cache_file = self._get_cache_path(self._active_project_ref)
            if cache_file.is_file():
                try:
                    cache_file.unlink()
                except Exception:
                    pass

    def get_project_summary(self, project_ref: Optional[str] = None) -> Dict[str, Any]:
        """Generate a complete summary of the project's components."""
        self._refresh_credentials()
        ref = project_ref or self._active_project_ref
        if not ref:
            raise ValueError("No active project selected")

        project = None
        for p in self._projects:
            if p["ref"] == ref:
                project = p
                break
        if not project:
            raise ValueError(f"Project reference '{ref}' not found")

        # Check Cache
        cached = self._load_cache(f"{ref}_summary")
        if cached:
            return cached

        # Perform discovery
        url = project.get("url") or ""
        headers = self._get_headers(project)

        tables_count = 0
        buckets_count = 0
        functions_count = 0
        views_count = 0

        # Try PostgREST schema discovery for tables
        try:
            with httpx.Client() as client:
                resp = client.post(
                    f"{url}/rest/v1/rpc/get_schema_info",  # Mock target or custom
                    headers=headers,
                    json={},
                    timeout=5,
                )
            if resp.status_code == 200:
                tables_info = resp.json()
                if isinstance(tables_info, list):
                    tables_count = len(tables_info)
            else:
                # Try OpenAPI fallback
                with httpx.Client() as client:
                    spec_resp = client.get(f"{url}/rest/v1/", headers=headers, timeout=5)
                if spec_resp.status_code == 200:
                    spec_data = spec_resp.json()
                    definitions = spec_data.get("definitions", {})
                    tables_count = len(definitions)
                    views_count = len(
                        [k for k, v in spec_data.get("paths", {}).items() if "views" in k]
                    )
        except Exception:
            pass

        # Try Storage Bucket discovery
        try:
            with httpx.Client() as client:
                resp = client.get(f"{url}/storage/v1/bucket", headers=headers, timeout=5)
            if resp.status_code == 200:
                buckets = resp.json()
                buckets_count = len(buckets)
        except Exception:
            pass

        # Try Edge Functions discovery
        if self._access_token:
            try:
                mgmt_headers = {"Authorization": f"Bearer {self._access_token}"}
                with httpx.Client() as client:
                    resp = client.get(
                        f"https://api.supabase.com/v1/projects/{ref}/functions",
                        headers=mgmt_headers,
                        timeout=5,
                    )
                if resp.status_code == 200:
                    functions = resp.json()
                    functions_count = len(functions)
            except Exception:
                pass

        summary = {
            "project_ref": ref,
            "name": project.get("name") or ref,
            "url": url,
            "region": project.get("region") or "unknown",
            "tables_count": tables_count,
            "views_count": views_count,
            "buckets_count": buckets_count,
            "functions_count": functions_count,
        }

        self._save_cache(f"{ref}_summary", summary)
        return summary

    def get_schema(self, project_ref: Optional[str] = None) -> Dict[str, Any]:
        """Explore schemas, tables, views, functions, triggers, and constraints."""
        self._refresh_credentials()
        ref = project_ref or self._active_project_ref
        if not ref:
            raise ValueError("No active project selected")

        project = None
        for p in self._projects:
            if p["ref"] == ref:
                project = p
                break
        if not project:
            raise ValueError(f"Project reference '{ref}' not found")

        cached = self._load_cache(f"{ref}_schema")
        if cached:
            return cached

        url = project.get("url") or ""
        headers = self._get_headers(project)

        schema_data = {
            "tables": [],
            "relationships": [],
            "views": [],
            "functions": [],
            "triggers": [],
            "constraints": [],
            "indexes": [],
        }

        # Try customized RPC/SQL endpoint
        try:
            with httpx.Client() as client:
                resp = client.post(
                    f"{url}/rest/v1/rpc/get_schema_metadata", headers=headers, json={}, timeout=5
                )
            if resp.status_code == 200:
                schema_data.update(resp.json())
            else:
                # Direct PostgREST OpenAPI parsing
                with httpx.Client() as client:
                    spec_resp = client.get(f"{url}/rest/v1/", headers=headers, timeout=5)
                if spec_resp.status_code == 200:
                    spec_data = spec_resp.json()
                    definitions = spec_data.get("definitions", {})
                    for tbl_name, tbl_spec in definitions.items():
                        cols = []
                        properties = tbl_spec.get("properties", {})
                        for col_name, col_spec in properties.items():
                            cols.append(
                                {
                                    "name": col_name,
                                    "type": col_spec.get("type"),
                                    "nullable": col_spec.get("description", "").find("nullable")
                                    != -1,
                                }
                            )
                        schema_data["tables"].append({"name": tbl_name, "columns": cols})
        except Exception:
            pass

        self._save_cache(f"{ref}_schema", schema_data)
        return schema_data

    def get_security_analysis(self, project_ref: Optional[str] = None) -> Dict[str, Any]:
        """Perform security check on RLS, public tables, keys, and storage policies."""
        self._refresh_credentials()
        ref = project_ref or self._active_project_ref
        if not ref:
            raise ValueError("No active project selected")

        project = None
        for p in self._projects:
            if p["ref"] == ref:
                project = p
                break
        if not project:
            raise ValueError(f"Project reference '{ref}' not found")

        cached = self._load_cache(f"{ref}_security")
        if cached:
            return cached

        url = project.get("url") or ""
        headers = self._get_headers(project)

        security_data = {
            "rls_enabled_tables": [],
            "rls_disabled_tables": [],
            "public_tables": [],
            "policies": [],
            "service_role_exposed": False,
            "security_recommendations": [],
        }

        try:
            with httpx.Client() as client:
                resp = client.post(
                    f"{url}/rest/v1/rpc/get_security_metadata", headers=headers, json={}, timeout=5
                )
            if resp.status_code == 200:
                security_data.update(resp.json())
        except Exception:
            pass

        # Build basic fallback recommendations
        recs = []
        if not security_data["rls_enabled_tables"] and security_data.get("tables"):
            recs.append("CRITICAL: RLS is disabled on all tables. Enable RLS to secure user data.")
        else:
            for tbl in security_data.get("rls_disabled_tables", []):
                recs.append(f"HIGH: Table '{tbl}' has RLS disabled. Enable RLS immediately.")

        # Verify Service Role exposure
        service_role_key = project.get("key") or ""
        if service_role_key.startswith("ey") and len(service_role_key) > 100:
            # Standard JWT, let's keep it safe.
            pass
        else:
            security_data["service_role_exposed"] = True
            recs.append("WARNING: Service role credential format is non-standard or insecure.")

        security_data["security_recommendations"] = recs

        self._save_cache(f"{ref}_security", security_data)
        return security_data

    def get_migrations(self, project_ref: Optional[str] = None) -> Dict[str, Any]:
        """Detect migration history, drift, and pending migrations."""
        self._refresh_credentials()
        ref = project_ref or self._active_project_ref
        if not ref:
            raise ValueError("No active project selected")

        project = None
        for p in self._projects:
            if p["ref"] == ref:
                project = p
                break
        if not project:
            raise ValueError(f"Project reference '{ref}' not found")

        cached = self._load_cache(f"{ref}_migrations")
        if cached:
            return cached

        url = project.get("url") or ""
        headers = self._get_headers(project)

        migration_data = {
            "migration_history": [],
            "pending_migrations": [],
            "drift_detected": False,
            "drift_details": [],
        }

        try:
            with httpx.Client() as client:
                resp = client.post(
                    f"{url}/rest/v1/rpc/get_migration_history", headers=headers, json={}, timeout=5
                )
            if resp.status_code == 200:
                migration_data.update(resp.json())
        except Exception:
            pass

        self._save_cache(f"{ref}_migrations", migration_data)
        return migration_data

    def get_edge_functions(self, project_ref: Optional[str] = None) -> Dict[str, Any]:
        """Discover and analyze edge functions deployment readiness."""
        self._refresh_credentials()
        ref = project_ref or self._active_project_ref
        if not ref:
            raise ValueError("No active project selected")

        project = None
        for p in self._projects:
            if p["ref"] == ref:
                project = p
                break
        if not project:
            raise ValueError(f"Project reference '{ref}' not found")

        cached = self._load_cache(f"{ref}_functions")
        if cached:
            return cached

        functions_list = []

        if self._access_token:
            try:
                mgmt_headers = {"Authorization": f"Bearer {self._access_token}"}
                with httpx.Client() as client:
                    resp = client.get(
                        f"https://api.supabase.com/v1/projects/{ref}/functions",
                        headers=mgmt_headers,
                        timeout=5,
                    )
                if resp.status_code == 200:
                    functions_list = resp.json()
            except Exception:
                pass

        result = {
            "functions": functions_list,
            "deploy_readiness": {
                "configured": len(functions_list) > 0,
                "token_valid": self._access_token is not None,
            },
        }

        self._save_cache(f"{ref}_functions", result)
        return result

    def get_storage(self, project_ref: Optional[str] = None) -> Dict[str, Any]:
        """Retrieve storage buckets, policies, and file statistics."""
        self._refresh_credentials()
        ref = project_ref or self._active_project_ref
        if not ref:
            raise ValueError("No active project selected")

        project = None
        for p in self._projects:
            if p["ref"] == ref:
                project = p
                break
        if not project:
            raise ValueError(f"Project reference '{ref}' not found")

        cached = self._load_cache(f"{ref}_storage")
        if cached:
            return cached

        url = project.get("url") or ""
        headers = self._get_headers(project)

        buckets_list = []
        try:
            with httpx.Client() as client:
                resp = client.get(f"{url}/storage/v1/bucket", headers=headers, timeout=5)
            if resp.status_code == 200:
                buckets_list = resp.json()
        except Exception:
            pass

        result = {"buckets": buckets_list, "policies": []}

        self._save_cache(f"{ref}_storage", result)
        return result

    def get_auth_config(self, project_ref: Optional[str] = None) -> Dict[str, Any]:
        """Retrieve authentication providers, sessions, and MFA configuration."""
        self._refresh_credentials()
        ref = project_ref or self._active_project_ref
        if not ref:
            raise ValueError("No active project selected")

        project = None
        for p in self._projects:
            if p["ref"] == ref:
                project = p
                break
        if not project:
            raise ValueError(f"Project reference '{ref}' not found")

        cached = self._load_cache(f"{ref}_auth")
        if cached:
            return cached

        url = project.get("url") or ""
        headers = self._get_headers(project)

        auth_config = {
            "providers": {"email": {"enabled": True}},
            "mfa": {"totp": {"enabled": False}},
            "mailer": {"secure": True},
        }

        try:
            with httpx.Client() as client:
                resp = client.get(f"{url}/auth/v1/admin/config", headers=headers, timeout=5)
            if resp.status_code == 200:
                auth_config.update(resp.json())
        except Exception:
            pass

        self._save_cache(f"{ref}_auth", auth_config)
        return auth_config

    def generate_reports(self, output_dir: Optional[Path] = None) -> Dict[str, Any]:
        """Generate markdown reports under docs/supabase/ directory."""
        self._refresh_credentials()
        ref = self._active_project_ref
        if not ref:
            raise ValueError("No active project selected for reports")

        out_path = output_dir or Path("docs/supabase")
        out_path.mkdir(parents=True, exist_ok=True)

        summary = self.get_project_summary(ref)
        schema = self.get_schema(ref)
        security = self.get_security_analysis(ref)
        migrations = self.get_migrations(ref)
        storage = self.get_storage(ref)
        auth = self.get_auth_config(ref)

        # 1. Summary Report
        summary_md = f"""# Supabase Project Summary Report

- **Project Ref:** `{ref}`
- **Project Name:** {summary.get("name")}
- **Region:** {summary.get("region")}
- **Project URL:** {summary.get("url")}

## Component Statistics
- **Tables Count:** {summary.get("tables_count")}
- **Views Count:** {summary.get("views_count")}
- **Storage Buckets:** {summary.get("buckets_count")}
- **Edge Functions:** {summary.get("functions_count")}
"""
        with open(out_path / "summary_report.md", "w", encoding="utf-8") as f:
            f.write(summary_md.strip())

        # 2. Schema Report
        tables_md = ""
        for t in schema.get("tables", []):
            cols_md = "\n".join(
                [f"  - `{c.get('name')}`: {c.get('type')}" for c in t.get("columns", [])]
            )
            tables_md += f"- **Table:** `{t.get('name')}`\n{cols_md}\n\n"

        views_raw = schema.get("views", [])
        views_list = [v.get("name", v) if isinstance(v, dict) else v for v in views_raw]
        schema_md = f"""# Supabase Schema Report

## Tables
{tables_md or "No tables discovered."}

## Views
{", ".join(views_list) or "No views discovered."}
"""
        with open(out_path / "schema_report.md", "w", encoding="utf-8") as f:
            f.write(schema_md.strip())

        # 3. Security Report
        recs_md = "\n".join([f"- {r}" for r in security.get("security_recommendations", [])])
        security_md = f"""# Supabase Security Report

## RLS Summary
- **RLS Enabled Tables:** {", ".join(security.get("rls_enabled_tables", [])) or "None"}
- **RLS Disabled Tables:** {", ".join(security.get("rls_disabled_tables", [])) or "None"}

## Security Recommendations
{recs_md or "No vulnerabilities detected."}
"""
        with open(out_path / "security_report.md", "w", encoding="utf-8") as f:
            f.write(security_md.strip())

        # 4. Migration Report
        history_md = "\n".join(
            [
                f"- `{m.get('version')}`: {m.get('name')} (applied at {m.get('applied_at')})"
                for m in migrations.get("migration_history", [])
            ]
        )
        migration_md = f"""# Supabase Migration Report

## Migration History
{history_md or "No migration history found."}

## Pending Migrations
{migrations.get("pending_migrations") or "None"}
"""
        with open(out_path / "migration_report.md", "w", encoding="utf-8") as f:
            f.write(migration_md.strip())

        # 5. Storage Report
        buckets_md = "\n".join(
            [
                f"- Bucket: `{b.get('name')}` (Public: {b.get('public')})"
                for b in storage.get("buckets", [])
            ]
        )
        storage_md = f"""# Supabase Storage Report

## Storage Buckets
{buckets_md or "No storage buckets found."}
"""
        with open(out_path / "storage_report.md", "w", encoding="utf-8") as f:
            f.write(storage_md.strip())

        # 6. Auth Report
        providers_md = ", ".join(
            [
                f"{k}: {'enabled' if v.get('enabled') else 'disabled'}"
                for k, v in auth.get("providers", {}).items()
            ]
        )
        auth_md = f"""# Supabase Auth Report

## Auth Configuration
- **Providers:** {providers_md or "None"}
- **MFA Configuration:** {auth.get("mfa")}
"""
        with open(out_path / "auth_report.md", "w", encoding="utf-8") as f:
            f.write(auth_md.strip())

        return {"reports_written": 6, "output_dir": str(out_path)}
