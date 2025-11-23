"""Data storage utilities for the crawler.

Security: Writes only structured CSV output, avoiding arbitrary code execution
risks from dynamic formats.
Maintainability: Encapsulates file handling to keep crawler core focused on
logic rather than IO concerns.
Extensibility: Can be expanded to support SQLite or cloud storage backends
without changing crawler orchestration.
"""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable

from .models import Car


class CarStorage:
    """CSV-backed storage for car listings."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_header()

    def _ensure_header(self) -> None:
        if not self.path.exists():
            with self.path.open("w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["brand", "model", "year", "price", "url", "source"])

    def write_car(self, car: Car) -> None:
        with self.path.open("a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([car.brand, car.model, car.year or "", car.price or "", car.url, car.source])

    def write_cars(self, cars: Iterable[Car]) -> None:
        for car in cars:
            self.write_car(car)
