"""HTTP fetching utilities for the crawler.

Security: Enforces TLS verification, timeouts, max content size, and allows for
per-domain rate limiting to prevent abuse.
Maintainability: Isolating HTTP concerns makes it easy to swap libraries or add
features like retry/backoff.
Extensibility: Hooks for headers, proxies, and authentication can be added
without rewriting crawler core.
"""
from __future__ import annotations

import logging
from typing import Optional

import requests

from .rate_limiter import RateLimiter

MAX_CONTENT_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB guardrail against large responses
DEFAULT_TIMEOUT = 10  # seconds


class Fetcher:
    """Fetches web pages with polite defaults and safety checks."""

    def __init__(self, user_agent: str, rate_limiter: RateLimiter) -> None:
        self.user_agent = user_agent
        self.rate_limiter = rate_limiter
        self.logger = logging.getLogger(__name__)

    def get(self, url: str, timeout: int | float = DEFAULT_TIMEOUT) -> Optional[str]:
        """Retrieve a URL as text, respecting rate limits and size caps."""
        domain = self._domain_from_url(url)
        self.rate_limiter.wait(domain)

        headers = {"User-Agent": self.user_agent}
        try:
            resp = requests.get(url, headers=headers, timeout=timeout, stream=True)
            resp.raise_for_status()
        except requests.RequestException as exc:
            self.logger.warning("Request failed for %s: %s", url, exc)
            return None

        content = self._read_with_size_limit(resp)
        if content is None:
            return None
        return content

    def _read_with_size_limit(self, response: requests.Response) -> Optional[str]:
        """Read response stream while enforcing a maximum size."""
        total = 0
        chunks = []
        for chunk in response.iter_content(chunk_size=8192, decode_unicode=True):
            if chunk:
                total += len(chunk.encode(response.encoding or "utf-8"))
                if total > MAX_CONTENT_SIZE_BYTES:
                    self.logger.warning(
                        "Response too large (>%s bytes) from %s", MAX_CONTENT_SIZE_BYTES, response.url
                    )
                    return None
                chunks.append(chunk)
        return "".join(chunks)

    @staticmethod
    def _domain_from_url(url: str) -> str:
        parts = url.split("//", 1)
        if len(parts) == 2:
            scheme_host, *_ = parts[1].split("/", 1)
            return f"{parts[0]}//{scheme_host}"
        return url
