"""Domain models for the luxury car crawler.

Security: Using dataclasses ensures predictable attributes and avoids
arbitrary attribute mutation, reducing accidental data leaks.
Maintainability: Centralized models make it easy to update fields used across
modules without breaking callers.
Extensibility: New fields can be added as the project evolves (e.g., VIN,
color, mileage) without changing overall architecture.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Car:
    """Structured representation of a car listing discovered by the crawler."""

    brand: str
    model: str
    year: Optional[int]
    price: Optional[str]
    url: str
    source: str
