"""
Shared pytest fixtures for the financial_scraper test suite.

Conventions
-----------
- All tests run hermetically: file I/O goes to pytest's `tmp_path` fixture, never
  to the user's working directory.
- HTML / CSV fixtures live under ``tests/fixtures/`` and are committed alongside the
  code so the suite is reproducible offline.
- The ``html`` and ``csv_text`` fixtures are tiny helpers for reading those files.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable

import pytest


FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def fixtures_dir() -> Path:
    """Root directory of the bundled fixture files."""
    return FIXTURES_DIR


@pytest.fixture
def download_path(tmp_path: Path) -> str:
    """
    A per-test, hermetic download directory.

    Returns the path as a string because the providers under test expect
    ``download_path: str``. The directory is created inside ``tmp_path`` so the
    suite never touches the user's filesystem.
    """
    p = tmp_path / "downloads"
    p.mkdir()
    return str(p)


@pytest.fixture
def html(fixtures_dir: Path) -> Callable[[str], str]:
    """Factory: read a stored HTML fixture by filename from ``fixtures/html/``."""

    def _read(name: str) -> str:
        path = fixtures_dir / "html" / name
        return path.read_text(encoding="utf-8")

    return _read


@pytest.fixture
def csv_text(fixtures_dir: Path) -> Callable[[str], str]:
    """Factory: read a stored CSV fixture by filename from ``fixtures/csv/``."""

    def _read(name: str) -> str:
        path = fixtures_dir / "csv" / name
        return path.read_text(encoding="utf-8")

    return _read
