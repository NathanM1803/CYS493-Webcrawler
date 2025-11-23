"""Test configuration to ensure package imports resolve correctly."""
from __future__ import annotations

import sys
from pathlib import Path


def pytest_configure() -> None:
    # Add repository root to sys.path so ``import luxury_crawler`` works when
    # tests are executed from within the repository directory structure.
    project_root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(project_root))
