from dataclasses import dataclass, field
from typing import List


@dataclass
class ProviderCapabilities:
    streaming: bool = True
    vision: bool = False
    function_calling: bool = False


@dataclass
class ProviderInfo:
    name: str
    supported_models: List[str] = field(default_factory=list)
    context_window: int = 4096
    capabilities: ProviderCapabilities = field(default_factory=ProviderCapabilities)
    availability: float = 1.0  # 0.0 to 1.0
    latency: float = 0.5  # average response time in seconds
    cost_per_million_input: float = 0.0
    cost_per_million_output: float = 0.0
    is_local: bool = False
