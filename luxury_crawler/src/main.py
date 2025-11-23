"""Entry point wiring configuration, crawler components, and execution.

Security: Ensures all components (rate limiting, robots enforcement, TLS) are
initialized consistently.
Maintainability: Centralizes application bootstrap logic for clarity.
Extensibility: New CLI options or configuration formats can be added without
changing component internals.
"""
from __future__ import annotations

import argparse
import logging
from pathlib import Path

from .config import load_config
from .fetcher import Fetcher
from .rate_limiter import RateLimiter
from .robots_handler import RobotsHandler
from .scheduler import Scheduler
from .storage import CarStorage


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(Path(__file__).resolve().parent.parent / "logs" / "crawler.log"),
    ],
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Benign luxury car web crawler for CYS-493")
    parser.add_argument(
        "--config",
        default=Path(__file__).resolve().parent.parent / "configs" / "config.json",
        help="Path to crawler configuration JSON",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(args.config)

    rate_limiter = RateLimiter(delay_seconds=config.crawl_delay_seconds)
    fetcher = Fetcher(user_agent=config.user_agent, rate_limiter=rate_limiter)
    robots = RobotsHandler(user_agent=config.user_agent)
    storage = CarStorage(Path(__file__).resolve().parent.parent / "data" / "cars.csv")

    scheduler = Scheduler(config=config, fetcher=fetcher, robots=robots, storage=storage)
    scheduler.run()


if __name__ == "__main__":
    main()
