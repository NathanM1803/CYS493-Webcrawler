"""Configuration loading and validation for the crawler.

Security: Centralized configuration prevents hard-coded secrets or URLs and
ensures SSL verification, robots compliance, and rate limits are enforced.
Maintainability: Separating config parsing keeps core logic clean and easier
for collaborators to read.
Extensibility: New configuration options (e.g., proxies, authentication) can
be added without touching crawler internals.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class Config:
    """Typed configuration for the crawler runtime."""

    seed_urls: List[str]
    max_pages_per_domain: int
    crawl_delay_seconds: float
    user_agent: str


def load_config(path: str | Path) -> Config:
    """Load and validate configuration from a JSON file.

    Args:
        path: Path to the JSON configuration file.

    Returns:
        A populated :class:`Config` instance.

    Raises:
        FileNotFoundError: If the configuration file does not exist.
        ValueError: If required fields are missing or malformed.
    """

    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as f:
        raw = json.load(f)

    try:
        seed_urls = raw["seed_urls"]
        max_pages_per_domain = int(raw["max_pages_per_domain"])
        crawl_delay_seconds = float(raw["crawl_delay_seconds"])
        user_agent = raw["user_agent"]
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("Invalid configuration file; missing or malformed fields") from exc

    if not seed_urls:
        raise ValueError("Configuration must include at least one seed URL")

    return Config(
        seed_urls=seed_urls,
        max_pages_per_domain=max_pages_per_domain,
        crawl_delay_seconds=crawl_delay_seconds,
        user_agent=user_agent,
    )
