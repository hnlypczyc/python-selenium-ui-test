from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from utils.paths import CONFIG_DIR


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")

    with path.open("r", encoding="utf-8") as stream:
        data = yaml.safe_load(stream) or {}

    if not isinstance(data, dict):
        raise ValueError(f"Configuration file must contain a mapping: {path}")

    return data


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_settings(env_name: str = "demo") -> dict[str, Any]:
    settings = _load_yaml(CONFIG_DIR / "settings.yaml")
    env_settings = _load_yaml(CONFIG_DIR / "environments" / f"{env_name}.yaml")
    merged = _deep_merge(settings, env_settings)
    merged.setdefault("app", {})
    merged["app"]["environment"] = env_name
    return merged


def get_default_credentials(settings: dict[str, Any], profile: str = "default_admin") -> dict[str, str]:
    users = settings.get("users", {})
    credentials = users.get(profile)
    if not credentials:
        raise KeyError(f"Credential profile not found: {profile}")
    return credentials

