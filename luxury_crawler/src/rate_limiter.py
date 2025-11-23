"""Simple per-domain rate limiter to enforce polite crawling.

Security: Prevents excessive requests that might be interpreted as abusive
behavior and helps avoid denial-of-service scenarios.
Maintainability: Encapsulated logic keeps timing concerns out of crawler core.
Extensibility: Can be replaced with token-bucket or async strategies later.
"""
from __future__ import annotations

import time
from collections import defaultdict
from typing import Dict


class RateLimiter:
    """Tracks last-request timestamps per domain and enforces crawl delays."""

    def __init__(self, delay_seconds: float) -> None:
        self.delay_seconds = delay_seconds
        self._last_request: Dict[str, float] = defaultdict(float)

    def wait(self, domain: str) -> None:
        """Sleep if necessary to respect the configured delay for a domain."""
        now = time.monotonic()
        elapsed = now - self._last_request[domain]
        if elapsed < self.delay_seconds:
            time.sleep(self.delay_seconds - elapsed)
        self._last_request[domain] = time.monotonic()
