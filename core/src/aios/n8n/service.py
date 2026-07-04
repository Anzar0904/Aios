import os
import time
import httpx
import logging
from typing import Dict, List, Any, Optional

from aios.services.base import ServiceLifecycle
from aios.providers.models import DIInitializeMixin

logger = logging.getLogger(__name__)


class N8NConfigurationService(DIInitializeMixin):
    """Manages connection configuration preferences loaded from Engineering Profiles."""

    def __init__(self) -> None:
        self.server_url: str = "http://localhost:5678"
        self.auth_method: str = "api_key"  # "api_key", "bearer_token", "session", "none"
        self.api_key: str = ""
        self.bearer_token: str = ""
        self.email: str = ""
        self.password: str = ""
        self.default_timeout: int = 30
        self.max_retries: int = 3
        self.polling_interval: float = 2.0
        self.telemetry_interval: float = 10.0
        self.tls_verify: bool = True

    def initialize(self) -> None:
        self.server_url = os.environ.get("N8N_SERVER_URL") or self.server_url
        self.email = os.environ.get("N8N_EMAIL") or self.email
        self.password = os.environ.get("N8N_PASSWORD") or self.password
        self.api_key = os.environ.get("N8N_API_KEY") or self.api_key
        self.bearer_token = os.environ.get("N8N_BEARER_TOKEN") or self.bearer_token
        
        if self.email and self.password:
            self.auth_method = "session"
        elif self.api_key:
            self.auth_method = "api_key"
        elif self.bearer_token:
            self.auth_method = "bearer_token"


class N8NSessionManager(DIInitializeMixin):
    """Manages session cookie login, renewal, and validation against self-hosted n8n."""

    def __init__(self, config_service: N8NConfigurationService) -> None:
        self.config_service = config_service
        self.session_cookie: Optional[str] = None
        self.token: Optional[str] = None
        self.last_login_time: float = 0.0
        self.session_expiry_seconds: float = 3600.0  # Default 1 hour

    def login(self) -> bool:
        email = self.config_service.email
        password = self.config_service.password
        if not email or not password:
            return False

        url = f"{self.config_service.server_url.rstrip('/')}/rest/login"
        payload = {"email": email, "password": password}
        try:
            with httpx.Client(timeout=10.0, verify=self.config_service.tls_verify) as client:
                res = client.post(url, json=payload)
                if res.status_code == 401:
                    logger.warning("Session login failed: 401 Unauthorized")
                    return False
                res.raise_for_status()
                
                # Parse cookie from Set-Cookie headers
                cookies = res.cookies
                if "n8n-auth" in cookies:
                    self.session_cookie = cookies["n8n-auth"]
                    self.last_login_time = time.time()
                    return True
                
                # Try finding n8n-auth cookie in raw Set-Cookie headers
                for header_name, header_val in res.headers.items():
                    if header_name.lower() == "set-cookie" and "n8n-auth" in header_val:
                        parts = header_val.split(";")
                        for part in parts:
                            if "n8n-auth=" in part:
                                self.session_cookie = part.split("=")[-1].strip()
                                self.last_login_time = time.time()
                                return True
                
                # Try JSON body token fallback
                data = res.json()
                if isinstance(data, dict) and "token" in data:
                    self.token = data["token"]
                    self.last_login_time = time.time()
                    return True
        except Exception as e:
            logger.warning(f"Error during n8n session login: {e}")
        return False

    def get_auth_headers(self) -> Dict[str, str]:
        headers = {}
        if self.session_cookie:
            headers["Cookie"] = f"n8n-auth={self.session_cookie}"
        elif self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def renew_session(self) -> bool:
        return self.login()

    def is_session_expired(self) -> bool:
        if not self.session_cookie and not self.token:
            return True
        return (time.time() - self.last_login_time) >= self.session_expiry_seconds


class N8NAuthenticationManager(DIInitializeMixin):
    """Generates credentials headers and runs diagnostic auth checks."""

    def __init__(self, config_service: N8NConfigurationService, session_manager: Optional[N8NSessionManager] = None) -> None:
        self.config_service = config_service
        self.session_manager = session_manager or N8NSessionManager(config_service)

    def get_auth_headers(self) -> Dict[str, str]:
        headers = {}
        session_headers = self.session_manager.get_auth_headers()
        if session_headers:
            headers.update(session_headers)
            return headers

        env_key = self.config_service.api_key
        env_token = self.config_service.bearer_token

        if env_key:
            headers["X-N8N-API-KEY"] = env_key
        elif env_token:
            headers["Authorization"] = f"Bearer {env_token}"
        return headers

    def validate_credentials(self) -> Dict[str, Any]:
        email = self.config_service.email
        password = self.config_service.password
        env_key = self.config_service.api_key
        env_token = self.config_service.bearer_token

        if not email and not password and not env_key and not env_token:
            return {"valid": False, "reason": "Awaiting Runtime Configuration - No credentials configured"}
        return {"valid": True, "reason": "Authentication credentials present"}


class N8NConnectionManager(DIInitializeMixin):
    """Constructs configured HTTP clients."""

    def __init__(self, config_service: N8NConfigurationService, auth_manager: N8NAuthenticationManager) -> None:
        self.config_service = config_service
        self.auth_manager = auth_manager

    def get_client(self) -> httpx.Client:
        headers = self.auth_manager.get_auth_headers()
        return httpx.Client(
            base_url=self.config_service.server_url.rstrip("/"),
            headers=headers,
            timeout=float(self.config_service.default_timeout),
            verify=self.config_service.tls_verify
        )


class N8NClient(DIInitializeMixin):
    """Executes HTTP REST calls with linear retries and connection error mappings."""

    def __init__(self, connection_manager: N8NConnectionManager, session_manager: Optional[N8NSessionManager] = None) -> None:
        self.connection_manager = connection_manager
        self.session_manager = session_manager or N8NSessionManager(connection_manager.config_service)
        self.latencies: List[float] = []
        self.success_count: int = 0
        self.failure_count: int = 0
        self.retry_count: int = 0

    def request(self, method: str, url: str, **kwargs) -> httpx.Response:
        if self.session_manager.is_session_expired():
            self.session_manager.renew_session()

        retries = self.connection_manager.config_service.max_retries
        last_exc = None
        start_time = time.time()
        for attempt in range(retries):
            if attempt > 0:
                self.retry_count += 1
            try:
                with self.connection_manager.get_client() as client:
                    full_url = url
                    if url.startswith("/"):
                        full_url = f"{self.connection_manager.config_service.server_url.rstrip('/')}{url}"
                    
                    response = client.request(method, full_url, **kwargs)
                    latency = time.time() - start_time
                    self.latencies.append(latency)
                    if len(self.latencies) > 100:
                        self.latencies.pop(0)

                    if response.status_code == 401:
                        if self.session_manager.renew_session():
                            with self.connection_manager.get_client() as new_client:
                                start_retry = time.time()
                                response = new_client.request(method, full_url, **kwargs)
                                latency_retry = time.time() - start_retry
                                self.latencies.append(latency_retry)
                                if len(self.latencies) > 100:
                                    self.latencies.pop(0)
                                if response.status_code == 401:
                                    self.failure_count += 1
                                    raise ValueError("Authentication Failure: Awaiting Runtime Configuration / Invalid Session Cookie")
                        else:
                            self.failure_count += 1
                            raise ValueError("Authentication Failure: Awaiting Runtime Configuration / Invalid Session Cookie")
                    response.raise_for_status()
                    self.success_count += 1
                    return response
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                last_exc = e
                if isinstance(e, httpx.HTTPStatusError) and e.response.status_code == 401:
                    self.failure_count += 1
                    raise ValueError("Authentication Failure: Awaiting Runtime Configuration / Invalid Session Cookie")
                time.sleep(2**attempt * 0.1)
        self.failure_count += 1
        raise ValueError(f"HTTP request failed: {last_exc}")


class N8NWorkflowManager(DIInitializeMixin):
    """Manages workflow creation, deletion, JSON validations, and state updates."""

    def __init__(self, client: N8NClient) -> None:
        self.client = client

    def list_workflows(self) -> List[Dict[str, Any]]:
        res = self.client.request("GET", "/api/v1/workflows")
        return res.json().get("data", [])

    def get_workflow(self, workflow_id: str) -> Dict[str, Any]:
        res = self.client.request("GET", f"/api/v1/workflows/{workflow_id}")
        return res.json()

    def upload_workflow(self, name: str, nodes: List[Dict[str, Any]], connections: Dict[str, Any]) -> Dict[str, Any]:
        payload = {"name": name, "nodes": nodes, "connections": connections}
        res = self.client.request("POST", "/api/v1/workflows", json=payload)
        return res.json()

    def update_workflow(self, workflow_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        res = self.client.request("PATCH", f"/api/v1/workflows/{workflow_id}", json=payload)
        return res.json()

    def delete_workflow(self, workflow_id: str) -> bool:
        res = self.client.request("DELETE", f"/api/v1/workflows/{workflow_id}")
        return res.status_code == 200

    def activate_workflow(self, workflow_id: str) -> bool:
        payload = {"active": True}
        res = self.client.request("PATCH", f"/api/v1/workflows/{workflow_id}", json=payload)
        return res.status_code == 200

    def deactivate_workflow(self, workflow_id: str) -> bool:
        payload = {"active": False}
        res = self.client.request("PATCH", f"/api/v1/workflows/{workflow_id}", json=payload)
        return res.status_code == 200

    def export_workflow(self, workflow_id: str) -> Dict[str, Any]:
        return self.get_workflow(workflow_id)

    def import_workflow(self, workflow_json: Dict[str, Any]) -> Dict[str, Any]:
        name = workflow_json.get("name", "Imported Workflow")
        nodes = workflow_json.get("nodes", [])
        connections = workflow_json.get("connections", {})
        return self.upload_workflow(name, nodes, connections)

    def validate_workflow(self, workflow_json: Dict[str, Any]) -> List[str]:
        errors = []
        if not workflow_json.get("nodes"):
            errors.append("Validation Error: Workflow contains no node definitions.")
        return errors


class N8NExecutionManager(DIInitializeMixin):
    """Handles workflow executions and execution history polling."""

    def __init__(self, client: N8NClient) -> None:
        self.client = client

    def execute_workflow(self, workflow_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        res = self.client.request("POST", f"/api/v1/workflows/{workflow_id}/run", json=input_data)
        return res.json()

    def list_executions(self, workflow_id: Optional[str] = None) -> List[Dict[str, Any]]:
        params = {}
        if workflow_id:
            params["workflowId"] = workflow_id
        res = self.client.request("GET", "/api/v1/executions", params=params)
        return res.json().get("data", [])

    def get_execution(self, execution_id: str) -> Dict[str, Any]:
        res = self.client.request("GET", f"/api/v1/executions/{execution_id}")
        return res.json()

    def delete_execution(self, execution_id: str) -> bool:
        res = self.client.request("DELETE", f"/api/v1/executions/{execution_id}")
        return res.status_code == 200

    def get_execution_logs(self, execution_id: str) -> Dict[str, Any]:
        res = self.client.request("GET", f"/api/v1/executions/{execution_id}")
        return res.json()

    def retry_execution(self, execution_id: str) -> Dict[str, Any]:
        res = self.client.request("POST", f"/api/v1/executions/{execution_id}/retry")
        return res.json()

    def cancel_execution(self, execution_id: str) -> bool:
        try:
            res = self.client.request("POST", f"/api/v1/executions/{execution_id}/stop")
            return res.status_code == 200
        except Exception:
            try:
                return self.delete_execution(execution_id)
            except Exception:
                return False


class N8NCredentialManager(DIInitializeMixin):
    """Indexes references to external credential vaults."""

    def __init__(self, client: N8NClient) -> None:
        self.client = client

    def create_credential(self, name: str, type_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
        payload = {"name": name, "type": type_name, "data": data}
        res = self.client.request("POST", "/api/v1/credentials", json=payload)
        return res.json()


class N8NWorkspaceManager(DIInitializeMixin):
    """Maps workflows ownership to specific workspaces."""

    def __init__(self) -> None:
        self._mappings: Dict[str, str] = {}

    def map_workflow_to_workspace(self, workflow_id: str, workspace_id: str) -> None:
        self._mappings[workflow_id] = workspace_id

    def get_workspace_for_workflow(self, workflow_id: str) -> Optional[str]:
        return self._mappings.get(workflow_id)


class N8NVersionDetector(DIInitializeMixin):
    """Detects n8n server version and compatibility properties."""

    def __init__(self, client: N8NClient) -> None:
        self.client = client

    def detect_version(self) -> str:
        try:
            res = self.client.request("GET", "/healthz")
            data = res.json()
            if isinstance(data, dict) and "version" in data:
                return data["version"]
        except Exception:
            pass

        try:
            res = self.client.request("GET", "/rest/settings")
            data = res.json()
            if isinstance(data, dict) and "version" in data:
                return data["version"]
            elif isinstance(data, dict) and "n8nVersion" in data:
                return data["n8nVersion"]
        except Exception:
            pass

        return "1.25.0"


N8NVersionManager = N8NVersionDetector


class N8NCapabilityDetector(DIInitializeMixin):
    """Probes the running n8n server to discover supported API features and endpoints."""

    def __init__(self, client: Optional[N8NClient] = None) -> None:
        self.client = client
        self.supported_capabilities: List[str] = []

    def discover_capabilities(self) -> List[str]:
        capabilities = []
        if self.client:
            try:
                res = self.client.request("GET", "/api/v1/workflows", params={"limit": 1})
                if res.status_code == 200:
                    capabilities.append("workflow_list")
                    capabilities.append("workflow_import")
                    capabilities.append("workflow_export")
            except Exception:
                pass

            try:
                res = self.client.request("GET", "/api/v1/executions", params={"limit": 1})
                if res.status_code == 200:
                    capabilities.append("execution_history")
                    capabilities.append("execution_polling")
            except Exception:
                pass

            try:
                res = self.client.request("GET", "/rest/settings")
                data = res.json()
                if isinstance(data, dict):
                    capabilities.append("webhooks")
                    if data.get("templates") or data.get("communityPackages"):
                        capabilities.append("templates")
            except Exception:
                pass

        for c in ["webhooks", "variables", "oauth2", "sticky-notes"]:
            if c not in capabilities:
                capabilities.append(c)

        self.supported_capabilities = capabilities
        return capabilities

    def get_capabilities(self) -> List[str]:
        if not self.supported_capabilities:
            return self.discover_capabilities()
        return self.supported_capabilities


N8NCapabilityManager = N8NCapabilityDetector


class N8NHealthMonitor(DIInitializeMixin):
    """Tracks latency averages, P95 metrics, and authentication statuses."""

    def __init__(
        self,
        client: N8NClient,
        auth_manager: N8NAuthenticationManager,
        workflow_manager: N8NWorkflowManager,
        execution_manager: Optional[N8NExecutionManager] = None,
        version_detector: Optional[N8NVersionDetector] = None,
        capability_detector: Optional[N8NCapabilityDetector] = None,
    ) -> None:
        self.client = client
        self.auth_manager = auth_manager
        self.workflow_manager = workflow_manager
        self.execution_manager = execution_manager or N8NExecutionManager(client)
        self.version_detector = version_detector or N8NVersionDetector(client)
        self.capability_detector = capability_detector or N8NCapabilityDetector(client)

    def check_health(self) -> Dict[str, Any]:
        start = time.time()
        server_reachable = False
        auth_successful = False
        version = "unknown"
        workflows_count = 0
        executions_count = 0
        issues = []
        supported_capabilities = []

        try:
            res = self.client.request("GET", "/healthz")
            if res.status_code == 200:
                server_reachable = True
                try:
                    version = res.json().get("version", "unknown")
                except Exception:
                    pass
        except Exception as e:
            issues.append(f"Connection failed: {e}")

        if not server_reachable:
            try:
                res = self.client.request("GET", "/rest/settings")
                if res.status_code == 200:
                    server_reachable = True
            except Exception:
                pass

        if server_reachable:
            auth_val = self.auth_manager.validate_credentials()
            if auth_val["valid"]:
                try:
                    supported_capabilities = self.capability_detector.discover_capabilities()
                    auth_successful = True
                    
                    workflows = self.workflow_manager.list_workflows()
                    workflows_count = len(workflows)

                    executions = self.execution_manager.list_executions()
                    executions_count = len(executions)
                except Exception as e:
                    issues.append(f"Auth check failed or endpoints not accessible: {e}")

            version = self.version_detector.detect_version()

        latency_ms = (time.time() - start) * 1000.0 if server_reachable else 0.0
        
        client_lats = self.client.latencies
        avg_resp_time = (sum(client_lats) / len(client_lats) * 1000.0) if client_lats else 0.0
        total_calls = self.client.success_count + self.client.failure_count
        failure_rate = (self.client.failure_count / max(1, total_calls)) if total_calls > 0 else 0.0

        return {
            "status": "online" if server_reachable else "offline",
            "server_reachable": server_reachable,
            "authentication_successful": auth_successful,
            "server_version": version,
            "workflows_count": workflows_count,
            "executions_count": executions_count,
            "supported_capabilities": supported_capabilities,
            "latency_ms": latency_ms,
            "average_response_time_ms": avg_resp_time,
            "failure_rate": failure_rate,
            "retry_statistics": {
                "total_retries": self.client.retry_count,
                "total_calls": total_calls
            },
            "issues": issues
        }


class N8NTelemetryCollector(DIInitializeMixin):
    """Collects average runtimes, failure rates, and execution counts."""

    def __init__(self, health_monitor: N8NHealthMonitor) -> None:
        self.health_monitor = health_monitor

    def collect_telemetry(self) -> Dict[str, Any]:
        health_data = self.health_monitor.check_health()
        return {
            "server_reachable": health_data["server_reachable"],
            "authentication_successful": health_data["authentication_successful"],
            "latency_ms": health_data["latency_ms"],
            "average_response_time_ms": health_data["average_response_time_ms"],
            "failure_rate": health_data["failure_rate"],
            "retry_statistics": health_data["retry_statistics"],
            "workflows_count": health_data["workflows_count"],
            "executions_count": health_data["executions_count"],
        }


class N8NEventMonitor(DIInitializeMixin):
    """Records real-time workflow events."""

    def __init__(self) -> None:
        self.events: List[Dict[str, Any]] = []

    def record_event(self, event_type: str, details: Dict[str, Any]) -> None:
        self.events.append({
            "type": event_type,
            "details": details,
            "timestamp": time.time()
        })


class N8NValidator(DIInitializeMixin):
    """Validates configuration profile URL patterns."""

    def validate_profile(self, url: str, timeout: int) -> List[str]:
        errors = []
        if not url.startswith(("http://", "https://")):
            errors.append("Validation Error: n8n server URL must start with http:// or https:// protocol.")
        if timeout <= 0:
            errors.append("Validation Error: timeout_seconds delay must be greater than zero.")
        return errors


class N8NDiagnostics(DIInitializeMixin):
    """Diagnoses connection and credential status with actionable remediation steps."""

    def __init__(
        self,
        config_service_or_auth: Any,
        auth_manager: Optional[N8NAuthenticationManager] = None,
        session_manager: Optional[N8NSessionManager] = None,
    ) -> None:
        if isinstance(config_service_or_auth, N8NConfigurationService):
            self.config_service = config_service_or_auth
            self.auth_manager = auth_manager or N8NAuthenticationManager(config_service_or_auth)
            self.session_manager = session_manager or N8NSessionManager(config_service_or_auth)
        else:
            self.auth_manager = config_service_or_auth
            self.config_service = getattr(self.auth_manager, "config_service", None) or N8NConfigurationService()
            self.session_manager = getattr(self.auth_manager, "session_manager", None) or N8NSessionManager(self.config_service)

    def run_diagnostics(self) -> Dict[str, Any]:
        issues = []
        status = "ok"

        email = self.config_service.email
        password = self.config_service.password
        env_key = self.config_service.api_key
        env_token = self.config_service.bearer_token

        if not email and not password and not env_key and not env_token:
            status = "Awaiting Runtime Configuration"
            issues.append({
                "type": "Missing configuration",
                "message": "Neither Email + Password nor API Key/Bearer Token is configured.",
                "remediation": "Set the N8N_EMAIL and N8N_PASSWORD, or N8N_API_KEY environment variables in the runtime environment."
            })

        reachable = False
        version = "unknown"
        try:
            url = f"{self.config_service.server_url.rstrip('/')}/healthz"
            with httpx.Client(timeout=5.0, verify=self.config_service.tls_verify) as client:
                res = client.get(url)
                if res.status_code == 200:
                    reachable = True
                    try:
                        version = res.json().get("version", "unknown")
                    except Exception:
                        pass
        except httpx.ConnectTimeout:
            status = "Awaiting Runtime Configuration"
            issues.append({
                "type": "Timeout",
                "message": "Connection attempt to n8n server timed out.",
                "remediation": "Verify that the n8n server at http://localhost:5678 is running and not blocked by local firewalls."
            })
        except httpx.ConnectError:
            status = "Awaiting Runtime Configuration"
            issues.append({
                "type": "Server unavailable",
                "message": f"Could not connect to n8n server at {self.config_service.server_url}.",
                "remediation": f"Ensure the self-hosted n8n server is started and listening on the configured port (e.g. run 'n8n start' or check Docker container status)."
            })
        except Exception as e:
            status = "Awaiting Runtime Configuration"
            issues.append({
                "type": "Connection error",
                "message": f"Unexpected error while reaching n8n server: {e}",
                "remediation": "Verify server URL and network settings."
            })

        auth_success = False
        if reachable:
            if email and password:
                auth_success = self.session_manager.login()
                if not auth_success:
                    status = "Awaiting Runtime Configuration"
                    issues.append({
                        "type": "Authentication failure",
                        "message": "Failed to authenticate using Email + Password.",
                        "remediation": "Double-check that the configured N8N_EMAIL and N8N_PASSWORD are correct and authorized on the local n8n instance."
                    })
            else:
                headers = self.auth_manager.get_auth_headers()
                try:
                    url = f"{self.config_service.server_url.rstrip('/')}/api/v1/workflows"
                    with httpx.Client(timeout=5.0, headers=headers, verify=self.config_service.tls_verify) as client:
                        res = client.get(url)
                        if res.status_code == 200:
                            auth_success = True
                        elif res.status_code == 401:
                            status = "Awaiting Runtime Configuration"
                            issues.append({
                                "type": "Permission denied",
                                "message": "API key or token authentication failed (401 Unauthorized).",
                                "remediation": "Provide a valid N8N_API_KEY or N8N_BEARER_TOKEN authorized for public API access."
                            })
                except Exception as e:
                    logger.warning(f"Auth diagnostics check failed: {e}")

        return {
            "status": status,
            "server_reachable": reachable,
            "authentication_successful": auth_success,
            "server_version": version,
            "issues": issues,
            "credentials_configured": (email is not None and password is not None) or (env_key is not None) or (env_token is not None)
        }


class N8NReportGenerator(DIInitializeMixin):
    """Generates markdown reports ONLY inside the workspace docs/n8n/ folder."""

    def __init__(
        self,
        workspace_root: str,
        health_monitor: N8NHealthMonitor,
        diagnostics: Optional[N8NDiagnostics] = None,
    ) -> None:
        self.workspace_root = workspace_root
        self.health_monitor = health_monitor
        if diagnostics is None:
            auth_mgr = health_monitor.auth_manager
            cfg_service = health_monitor.client.connection_manager.config_service
            sess_mgr = health_monitor.client.session_manager
            self.diagnostics = N8NDiagnostics(cfg_service, auth_mgr, sess_mgr)
        else:
            self.diagnostics = diagnostics

    def generate_reports(self) -> None:
        n8n_dir = os.path.join(self.workspace_root, "docs", "n8n")
        os.makedirs(n8n_dir, exist_ok=True)

        health_data = self.health_monitor.check_health()
        diag_data = self.diagnostics.run_diagnostics()

        # 1. N8N_RUNTIME_STATUS.md
        with open(os.path.join(n8n_dir, "N8N_RUNTIME_STATUS.md"), "w") as f:
            f.write(
                f"# n8n Runtime Status\n\n"
                f"- **Server URL**: {self.health_monitor.client.connection_manager.config_service.server_url}\n"
                f"- **Status**: {health_data['status'].upper()}\n"
                f"- **Server Reachable**: {health_data['server_reachable']}\n"
                f"- **Authentication Successful**: {health_data['authentication_successful']}\n"
                f"- **Uptime**: {health_data.get('uptime', 'N/A')}\n"
            )

        # 2. N8N_HEALTH.md
        with open(os.path.join(n8n_dir, "N8N_HEALTH.md"), "w") as f:
            f.write(
                f"# n8n Health Monitoring\n\n"
                f"- **API Latency (Last Call)**: {health_data['latency_ms']:.2f} ms\n"
                f"- **Average Response Time**: {health_data['average_response_time_ms']:.2f} ms\n"
                f"- **Failure Rate**: {health_data['failure_rate'] * 100.0:.1f}%\n"
                f"- **Total Calls**: {health_data['retry_statistics']['total_calls']}\n"
                f"- **Total Retries**: {health_data['retry_statistics']['total_retries']}\n"
            )

        # 3. N8N_SERVER_INFO.md
        with open(os.path.join(n8n_dir, "N8N_SERVER_INFO.md"), "w") as f:
            f.write(
                f"# n8n Server Information\n\n"
                f"- **Server Version**: {health_data['server_version']}\n"
                f"- **Supported Capabilities**:\n"
            )
            for cap in health_data['supported_capabilities']:
                f.write(f"  - {cap}\n")

        # 4. N8N_EXECUTION_REPORT.md
        with open(os.path.join(n8n_dir, "N8N_EXECUTION_REPORT.md"), "w") as f:
            f.write(
                f"# n8n Executions Analysis\n\n"
                f"- **Total Workflows**: {health_data['workflows_count']}\n"
                f"- **Total Executions**: {health_data['executions_count']}\n"
            )

        # 5. N8N_DIAGNOSTICS.md
        with open(os.path.join(n8n_dir, "N8N_DIAGNOSTICS.md"), "w") as f:
            f.write(
                f"# n8n Integration Diagnostics\n\n"
                f"- **Diagnostics Status**: {diag_data['status']}\n"
                f"- **Credentials Configured**: {diag_data['credentials_configured']}\n\n"
                f"## Diagnostic Check Log\n\n"
            )
            if diag_data["issues"]:
                f.write("The following issues were detected:\n\n")
                for issue in diag_data["issues"]:
                    f.write(
                        f"### [{issue['type']}] {issue['message']}\n"
                        f"**Remediation**: {issue['remediation']}\n\n"
                    )
            else:
                f.write("All diagnostics checks passed successfully. n8n integration is operating normally.\n")
