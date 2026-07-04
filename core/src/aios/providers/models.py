from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum


class ProviderStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    RATE_LIMITED = "rate_limited"
    QUOTA_EXHAUSTED = "quota_exhausted"
    AUTH_FAILURE = "auth_failure"
    UNAVAILABLE = "unavailable"
    MAINTENANCE = "maintenance"
    UNKNOWN = "unknown"


@dataclass
class ProviderCapabilities:
    streaming: bool = True
    vision: bool = False
    function_calling: bool = False
    tools: bool = False
    images: bool = False
    reasoning: bool = False
    code_generation: bool = False
    editing: bool = False
    long_context: bool = False
    structured_output: bool = False


@dataclass
class ProviderStatistics:
    total_requests: int = 0
    total_successes: int = 0
    total_failures: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    total_cost_usd: float = 0.0
    latency_history: List[float] = field(default_factory=list)
    last_success_timestamp: float = 0.0
    last_failure_timestamp: float = 0.0


@dataclass
class ProviderMetadata:
    name: str
    version: str = "1.0.0"
    capabilities: ProviderCapabilities = field(default_factory=ProviderCapabilities)
    priority: int = 1
    status: ProviderStatus = ProviderStatus.UNKNOWN
    context_window: int = 4096
    cost_per_million_input: float = 0.0
    cost_per_million_output: float = 0.0
    auth_type: str = "api_key"  # api_key, bearer_token, none
    configuration: Dict[str, Any] = field(default_factory=dict)
    is_local: bool = False
    supported_models: List[str] = field(default_factory=list)
    availability: float = 1.0
    latency: float = 0.5


ProviderInfo = ProviderMetadata


from aios.services.base import ServiceLifecycle


class DIInitializeMixin(ServiceLifecycle):
    def initialize(self) -> None:
        pass
    def on_ready(self) -> None:
        pass
    def teardown(self) -> None:
        pass


@dataclass
class ExecutionContext:
    task_id: str
    history: List[Dict[str, Any]] = field(default_factory=list)
    step_info: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionSession:
    session_id: str
    task_id: str
    active_provider: str
    active_model: str
    start_time: float
    context: ExecutionContext
    checkpoint_id: Optional[str] = None


@dataclass
class ProviderDiagnostics:
    selected_provider: str
    selected_model: str
    fallback_used: str  # "Yes" or "No"
    fallback_reason: str
    latency: float
    routing_policy: str
    retry_count: int
    tokens_used: int = 0
    cost: float = 0.0
