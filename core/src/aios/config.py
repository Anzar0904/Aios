import tomllib
from dataclasses import dataclass
from pathlib import Path


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
class LLMConfig:
    provider: str = "mock"
    default_model: str = "mock-model"
    openrouter: OpenRouterConfig = OpenRouterConfig()


@dataclass(frozen=True)
class OSConfig:
    runtime: RuntimeConfig
    llm: LLMConfig = LLMConfig()


def load_config(config_path: Path) -> OSConfig:
    """Loads and parses the TOML configuration file."""
    if not config_path.exists():
        return OSConfig(
            runtime=RuntimeConfig(name="Personal AI OS", version="0.1.0", debug=False),
            llm=LLMConfig(),
        )

    with open(config_path, "rb") as f:
        data = tomllib.load(f)

    runtime_data = data.get("runtime", {})
    llm_data = data.get("llm", {})
    openrouter_data = llm_data.get("openrouter", {})

    return OSConfig(
        runtime=RuntimeConfig(
            name=runtime_data.get("name", "Personal AI OS"),
            version=runtime_data.get("version", "0.1.0"),
            debug=runtime_data.get("debug", False),
        ),
        llm=LLMConfig(
            provider=llm_data.get("provider", "mock"),
            default_model=llm_data.get("default_model", "mock-model"),
            openrouter=OpenRouterConfig(
                base_url=openrouter_data.get("base_url", "https://openrouter.ai/api/v1"),
                timeout=openrouter_data.get("timeout", 30),
            ),
        ),
    )
