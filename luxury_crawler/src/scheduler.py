"""URL scheduling and crawl loop controller.

Security: Tracks visited URLs to avoid loops and repeated requests that could
stress target sites.
Maintainability: Encapsulates crawl orchestration, making core logic easier to
reason about and extend.
Extensibility: Can be enhanced with depth limits, priority queues, or domain
sharding without altering other modules.
"""
from __future__ import annotations

import logging
from collections import deque
from typing import Deque, Set

from .config import Config
from .fetcher import Fetcher
from .parser import parse_inventory_page
from .robots_handler import RobotsHandler
from .storage import CarStorage


class Scheduler:
    """Minimal breadth-first scheduler for crawling approved domains."""

    def __init__(self, config: Config, fetcher: Fetcher, robots: RobotsHandler, storage: CarStorage) -> None:
        self.config = config
        self.fetcher = fetcher
        self.robots = robots
        self.storage = storage
        self.queue: Deque[str] = deque(config.seed_urls)
        self.visited: Set[str] = set()
        self.logger = logging.getLogger(__name__)

    def run(self) -> None:
        """Execute the crawl loop respecting limits and robots policies."""
        pages_fetched = 0
        while self.queue and pages_fetched < self.config.max_pages_per_domain:
            url = self.queue.popleft()
            if url in self.visited:
                continue

            if not self.robots.can_fetch(url):
                self.logger.info("Skipping disallowed URL per robots.txt: %s", url)
                continue

            html = self.fetcher.get(url)
            if html is None:
                continue

            cars, new_urls = parse_inventory_page(html, base_url=url, source=url)
            for car in cars:
                self.storage.write_car(car)

            for new_url in new_urls:
                if new_url in self.visited:
                    continue

                if not self.robots.can_fetch(new_url):
                    self.logger.info("Skipping disallowed discovered URL per robots.txt: %s", new_url)
                    continue

                self.queue.append(new_url)

            self.visited.add(url)
            pages_fetched += 1
