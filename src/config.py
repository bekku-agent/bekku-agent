"""Load agent configuration from config.yaml."""

from __future__ import annotations

from pathlib import Path
from functools import lru_cache

import yaml


CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"


@lru_cache
def load_config() -> dict:
    """Load and cache the agent configuration."""
    return yaml.safe_load(CONFIG_PATH.read_text())


def get_company_name() -> str:
    return load_config()["company"]["name"]


def get_docs_url() -> str:
    return load_config()["company"]["docs_url"]


def get_agent_name() -> str:
    return load_config()["agent"]["name"]
