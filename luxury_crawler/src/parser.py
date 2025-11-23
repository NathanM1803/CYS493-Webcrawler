"""HTML parsing for inventory pages.

Security: Relies on BeautifulSoup instead of heavy regex to reduce ReDoS risk
and includes TODOs for site-specific selectors to avoid brittle scraping.
Maintainability: Keeps parsing logic separate from network code for clarity.
Extensibility: New site-specific parsers or selectors can be added with minimal
changes to caller code.
"""
from __future__ import annotations

from typing import List, Tuple
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .models import Car


def parse_inventory_page(html: str, base_url: str, source: str) -> Tuple[List[Car], List[str]]:
    """Parse an inventory page for car listings and discover new links.

    Args:
        html: Raw HTML of the page.
        base_url: The URL the HTML was retrieved from, used for resolving links.
        source: Human-readable source name (e.g., domain).

    Returns:
        Tuple of (cars, new_urls).
    """
    soup = BeautifulSoup(html, "lxml")

    cars: List[Car] = []
    new_urls: List[str] = []

    # TODO: Replace the below placeholder selectors with site-specific CSS selectors
    # for luxury car inventory pages. Example patterns are provided to guide future
    # contributors. Keep selectors narrow to avoid accidental scraping of unrelated
    # content.
    for listing in soup.select("div.listing"):
        brand = listing.select_one(".brand")
        model = listing.select_one(".model")
        year = listing.select_one(".year")
        price = listing.select_one(".price")

        car = Car(
            brand=brand.get_text(strip=True) if brand else "",
            model=model.get_text(strip=True) if model else "",
            year=int(year.get_text(strip=True)) if year and year.get_text(strip=True).isdigit() else None,
            price=price.get_text(strip=True) if price else None,
            url=base_url,
            source=source,
        )
        cars.append(car)

    # Discover new URLs limited to same domain via simple heuristic.
    for link in soup.find_all("a", href=True):
        href = link["href"]
        absolute = urljoin(base_url, href)
        if absolute.startswith(base_url.split("/", 3)[0]):
            new_urls.append(absolute)

    return cars, new_urls
