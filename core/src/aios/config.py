import tomllib
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class RuntimeConfig:
    name: str
    version: str
    debug: bool


@dataclass(frozen=True)
class OpenRouterConfig:
    base_url: str = "https://openrouter.ai/api/v1"
    timeout: int = 30


@dataclass(frozen=True)
class OmniRouteConfig:
    base_url: str = "http://localhost:20128/v1"
    api_key: Optional[str] = None
    routing_policy: str = "FREE_ONLY"
    timeout: int = 30
    retry_count: int = 3
    streaming_enabled: bool = True
    offline_mode: bool = False


@dataclass(frozen=True)
class LLMConfig:
    provider: str = "mock"
    default_model: str = "mock-model"
    openrouter: OpenRouterConfig = OpenRouterConfig()
    omniroute: OmniRouteConfig = OmniRouteConfig()


@dataclass(frozen=True)
class GitHubConfig:
    token: Optional[str] = None
    base_url: str = "https://api.github.com"
    rate_limit_per_min: int = 60
    cache_enabled: bool = True
    timeout: int = 30
    max_retries: int = 3
    offline_mode: bool = False


@dataclass(frozen=True)
class NotionConfig:
    token: Optional[str] = None
    workspace_id: Optional[str] = None
    default_parent_page: Optional[str] = None
    default_databases: Optional[dict] = None
    read_only_mode: bool = False
    sync_mode: str = "periodic"
    offline_mode: bool = False
    retry_count: int = 3
    timeout: int = 30
    logging_enabled: bool = True


@dataclass(frozen=True)
class OSConfig:
    runtime: RuntimeConfig
    llm: LLMConfig = LLMConfig()
    github: GitHubConfig = GitHubConfig()
    notion: NotionConfig = NotionConfig()


def load_config(config_path: Path) -> OSConfig:
    """Loads and parses the TOML configuration file."""
    if not config_path.exists():
        return OSConfig(
            runtime=RuntimeConfig(name="Personal AI OS", version="0.5.0", debug=False),
            llm=LLMConfig(),
            github=GitHubConfig(),
            notion=NotionConfig(),
        )

    with open(config_path, "rb") as f:
        data = tomllib.load(f)

    runtime_data = data.get("runtime", {})
    llm_data = data.get("llm", {})
    openrouter_data = llm_data.get("openrouter", {})
    omniroute_data = llm_data.get("omniroute", {})
    github_data = data.get("github", {})
    notion_data = data.get("notion", {})

    # Load api_key from environment variables if not present in config
    api_key = omniroute_data.get("api_key") or os.environ.get("OMNIROUTE_API_KEY")

    # Load github token from environment variables if not present in config
    github_token = github_data.get("token") or os.environ.get("GITHUB_TOKEN") or os.environ.get("GITHUB_PAT")

    # Load notion token from environment variables if not present in config
    notion_token = notion_data.get("token") or os.environ.get("NOTION_TOKEN")

    return OSConfig(
        runtime=RuntimeConfig(
            name=runtime_data.get("name", "Personal AI OS"),
            version=runtime_data.get("version", "0.5.0"),
            debug=runtime_data.get("debug", False),
        ),
        llm=LLMConfig(
            provider=llm_data.get("provider", "mock"),
            default_model=llm_data.get("default_model", "mock-model"),
            openrouter=OpenRouterConfig(
                base_url=openrouter_data.get("base_url", "https://openrouter.ai/api/v1"),
                timeout=openrouter_data.get("timeout", 30),
            ),
            omniroute=OmniRouteConfig(
                base_url=omniroute_data.get("base_url", "http://localhost:20128/v1"),
                api_key=api_key,
                routing_policy=omniroute_data.get("routing_policy", "FREE_ONLY"),
                timeout=omniroute_data.get("timeout", 30),
                retry_count=omniroute_data.get("retry_count", 3),
                streaming_enabled=omniroute_data.get("streaming_enabled", True),
                offline_mode=omniroute_data.get("offline_mode", False),
            ),
        ),
        github=GitHubConfig(
            token=github_token,
            base_url=github_data.get("base_url", "https://api.github.com"),
            rate_limit_per_min=github_data.get("rate_limit_per_min", 60),
            cache_enabled=github_data.get("cache_enabled", True),
            timeout=github_data.get("timeout", 30),
            max_retries=github_data.get("max_retries", 3),
            offline_mode=github_data.get("offline_mode", False),
        ),
        notion=NotionConfig(
            token=notion_token,
            workspace_id=notion_data.get("workspace_id"),
            default_parent_page=notion_data.get("default_parent_page"),
            default_databases=notion_data.get("default_databases", {}),
            read_only_mode=notion_data.get("read_only_mode", False),
            sync_mode=notion_data.get("sync_mode", "periodic"),
            offline_mode=notion_data.get("offline_mode", False),
            retry_count=notion_data.get("retry_count", 3),
            timeout=notion_data.get("timeout", 30),
            logging_enabled=notion_data.get("logging_enabled", True),
        ),
    )
