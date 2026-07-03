import tomllib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class RuntimeConfig:
    name: str
    version: str
    debug: bool


@dataclass(frozen=True)
class OSConfig:
    runtime: RuntimeConfig


def load_config(config_path: Path) -> OSConfig:
    """Loads and parses the TOML configuration file."""
    if not config_path.exists():
        return OSConfig(runtime=RuntimeConfig(name="Personal AI OS", version="0.1.0", debug=False))

    with open(config_path, "rb") as f:
        data = tomllib.load(f)

    runtime_data = data.get("runtime", {})
    return OSConfig(
        runtime=RuntimeConfig(
            name=runtime_data.get("name", "Personal AI OS"),
            version=runtime_data.get("version", "0.1.0"),
            debug=runtime_data.get("debug", False),
        )
    )
