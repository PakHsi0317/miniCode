from pathlib import Path
from typing import Any

import yaml

DEFAULTS: dict[str, Any] = {
    "scan": {
        "extensions": [".py", ".md", ".txt"],
        "ignore_dirs": [
            ".git", "__pycache__", ".venv", "venv",
            "node_modules", ".pytest_cache", ".devnotes",
            ".ruff_cache", "dist", "build",
        ],
    },
    "keywords": {
        "max_per_file": 200,
    },
    "storage": {
        "db_path": ".devnotes/index.db",
    },
    "logging": {
        "level": "INFO",
    },
}

CONFIG_FILENAME = "config.yaml"


def load_config(config_path: Path | None = None) -> dict[str, Any]:
    """Load YAML config and deep-merge over built-in defaults.

    Search order (when path not given):
      1. ./config.yaml in current working dir
      2. Fall back to DEFAULTS only (no error if missing).
    """
    if config_path is None:
        config_path = Path.cwd() / CONFIG_FILENAME

    config = _deep_copy(DEFAULTS)

    if config_path.exists():
        with config_path.open(encoding="utf-8") as f:
            user_config = yaml.safe_load(f) or {}
        if not isinstance(user_config, dict):
            raise ValueError(f"{config_path} must contain a YAML mapping at top level")
        config = _deep_merge(config, user_config)

    return config


def _deep_copy(d: dict) -> dict:
    return {k: _deep_copy(v) if isinstance(v, dict) else v for k, v in d.items()}


def _deep_merge(base: dict, overrides: dict) -> dict:
    """Recursively merge `overrides` into `base`. Lists are replaced, not merged."""
    result = _deep_copy(base)
    for key, value in overrides.items():
        if (
            key in result
            and isinstance(result[key], dict)
            and isinstance(value, dict)
        ):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result
