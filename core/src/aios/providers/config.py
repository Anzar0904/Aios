from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ProviderConfig:
    preferred_provider: Optional[str] = None
    fallback_chain: List[str] = field(
        default_factory=lambda: [
            "omniroute",
            "openrouter",
            "openai",
            "gemini",
            "anthropic",
            "ollama",
            "lmstudio",
        ]
    )
    offline_mode: bool = False
    preferred_local_model: str = "llama3"
    preferred_remote_model: str = "gpt-4o"
    # OmniRoute Settings
    omniroute_base_url: str = "http://localhost:20128/v1"
    omniroute_api_key: Optional[str] = None
    omniroute_routing_policy: str = "FREE_ONLY"
    omniroute_timeout: int = 30
    omniroute_retry_count: int = 3
    omniroute_streaming_enabled: bool = True

