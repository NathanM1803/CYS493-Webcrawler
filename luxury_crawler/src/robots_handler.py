"""Robots.txt handling and enforcement for the crawler.

Security: Strictly obeys robots.txt rules and fails closed on parsing errors,
reducing legal/ethical risk and avoiding hostile endpoints.
Maintainability: Encapsulates robots logic away from crawler core, simplifying
future changes.
Extensibility: Supports swapping in more advanced robots evaluators later.
"""
from __future__ import annotations

import logging
from typing import Dict, Optional

import requests
import urllib.robotparser


class RobotsHandler:
    """Caches robots.txt rules and checks URL eligibility."""

    def __init__(self, user_agent: str, timeout: int | float = 10) -> None:
        self.user_agent = user_agent
        self.timeout = timeout
        self._parsers: Dict[str, urllib.robotparser.RobotFileParser] = {}
        self.logger = logging.getLogger(__name__)

    def can_fetch(self, url: str) -> bool:
        """Return True if the URL is allowed per robots.txt, False otherwise.

        On parsing failure the method returns False (fail-closed) to prioritize
        ethical behavior.
        """
        domain = self._domain_from_url(url)
        parser = self._parsers.get(domain)
        if parser is None:
            parser = self._fetch_parser(domain)
            self._parsers[domain] = parser

        try:
            return parser.can_fetch(self.user_agent, url)
        except Exception as exc:  # pragma: no cover - defensive safety
            self.logger.warning("Robots parsing failed for %s: %s", url, exc)
            return False

    def _fetch_parser(self, domain: str) -> urllib.robotparser.RobotFileParser:
        """Retrieve and parse robots.txt, failing closed on errors."""
        parser = urllib.robotparser.RobotFileParser()
        robots_url = self._robots_url(domain)
        parser.set_url(robots_url)

        content = self._download_robots(robots_url)
        if content is None:
            # Fail closed: disallow everything when robots cannot be read.
            parser.parse(["User-agent: *", "Disallow: /"])
            return parser

        try:
            lines = content.splitlines()
            parser.parse(lines)
        except Exception as exc:  # pragma: no cover - defensive safety
            self.logger.warning("Failed to parse robots.txt from %s: %s", robots_url, exc)
            parser.parse(["User-agent: *", "Disallow: /"])
        return parser

    def _download_robots(self, robots_url: str) -> Optional[str]:
        """Download robots.txt with explicit timeout and user-agent.

        Returns the text content or None if retrieval fails.
        """
        headers = {"User-Agent": self.user_agent}
        try:
            response = requests.get(robots_url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.text
        except requests.RequestException as exc:
            self.logger.warning("Failed to read robots.txt from %s: %s", robots_url, exc)
            return None

    @staticmethod
    def _domain_from_url(url: str) -> str:
        # Minimal parsing to group rate limiting/robots by scheme and host.
        # Using simple split avoids needing external dependencies at this stage.
        parts = url.split("//", 1)
        if len(parts) == 2:
            scheme_host, *_ = parts[1].split("/", 1)
            return f"{parts[0]}//{scheme_host}"
        return url

    @staticmethod
    def _robots_url(domain: str) -> str:
        return f"{domain}/robots.txt" if domain.startswith("http") else f"https://{domain}/robots.txt"
