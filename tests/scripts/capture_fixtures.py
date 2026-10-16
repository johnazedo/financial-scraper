"""
One-shot helper to refresh ``tests/fixtures/`` from the live sites.

What this script does
---------------------
For each requests-based provider it:

  1. Performs the same HTTP GET the provider would do.
  2. Saves the **raw response body** to ``tests/fixtures/html/<name>.html``.
  3. Replays that body through the provider's parser so the matching
     ``tests/fixtures/csv/<name>.csv`` is also written for reference.

For Selenium-based providers (``StatusInvestProvider``, ``FundsExplorerProvider``,
``MarketDataProvider``) the HTML lives inside ``driver.page_source`` after the
browser has navigated to the page. Reproducing it here would require a fake
Selenium driver that writes its page_source to disk — that's left for a
follow-up that pairs with the ``driver_factory`` refactor.

Usage
-----
This script hits real websites. Do not run it in CI.

    /tmp/opencode/venv/bin/python tests/scripts/capture_fixtures.py

Each capture writes to a deterministic filename in tests/fixtures/{html,csv}.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from freezegun import freeze_time

# Make the package importable when run as ``python tests/scripts/capture_fixtures.py``.
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from financial_scraper import (  # noqa: E402
    FundamentusProvider,
    InvestorTenProvider,
    TradingViewProvider,
)


CSV_DIR = ROOT / "tests" / "fixtures" / "csv"
HTML_DIR = ROOT / "tests" / "fixtures" / "html"

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0 Safari/537.36"
)
COMMON_HEADERS = {
    "User-Agent": UA,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
}


def _write_html(name: str, body: bytes | str) -> Path:
    """Persist HTML payload to disk; ``name`` is e.g. 'fundamentus'."""
    target = HTML_DIR / f"{name}.html"
    if isinstance(body, str):
        body = body.encode("utf-8")
    target.write_bytes(body)
    return target


def _print(label: str, path: Path | None, *, err: str | None = None) -> None:
    if err:
        print(f"   FAILED {label}: {err}")
    elif path is not None:
        print(f"   wrote {path.relative_to(ROOT)}")


# ---------------------------------------------------------------------------
# Fundamentus
# ---------------------------------------------------------------------------


def _capture_fundamentus() -> None:
    name = "fundamentus"
    print(f"== {name} ==")
    resp = requests.get(
        FundamentusProvider._URL,
        headers={
            **COMMON_HEADERS,
            "User-Agent": FundamentusProvider._HEADERS["User-Agent"],
        },
        timeout=30,
    )
    resp.raise_for_status()
    html_path = _write_html(name, resp.content)

    # Replay through the provider's parser against the captured bytes.
    with freeze_time("2026-01-15"):
        provider = FundamentusProvider(
            download_path=str(CSV_DIR),
            filename=f"{name}.csv",
        )
        provider.html_content = resp.content
        provider._read_page_and_get_data()
        provider._transform_data_into_csv()

    _print(name, html_path)


# ---------------------------------------------------------------------------
# TradingView
# ---------------------------------------------------------------------------


def _capture_trading_view(symbols: list[str] | None = None) -> None:
    name = "trading_view"
    print(f"== {name} ==")
    symbols = symbols or ["PETR4", "VALE3"]

    # Capture each symbol's HTML page separately, and also build a single
    # combined fixture that contains all of them so a test can stub several
    # responses at once.
    combined_html_parts: list[str] = []
    for symbol in symbols:
        url = TradingViewProvider._URL.replace(TradingViewProvider._SYMBOL, symbol)
        resp = requests.get(url, headers=COMMON_HEADERS, timeout=30)
        resp.raise_for_status()
        _write_html(f"{name}_{symbol}", resp.content)
        combined_html_parts.append(
            f"<!-- BEGIN {symbol} -->\n{resp.text}\n<!-- END {symbol} -->"
        )

    combined_html = (
        "<!doctype html>\n"
        "<html><head><meta charset='utf-8'>"
        "<title>TradingView combined fixture</title>"
        "</head><body>\n"
        + "\n\n".join(combined_html_parts)
        + "\n</body></html>\n"
    )
    combined_path = HTML_DIR / f"{name}_combined.html"
    combined_path.write_text(combined_html, encoding="utf-8")

    # Build the CSV by replaying the parser for each captured symbol.
    provider = TradingViewProvider(
        download_path=str(CSV_DIR), filename=f"{name}.csv"
    )
    provider._config_step()
    for symbol in symbols:
        url = TradingViewProvider._URL.replace(TradingViewProvider._SYMBOL, symbol)
        resp = requests.get(url, headers=COMMON_HEADERS, timeout=30)
        resp.raise_for_status()
        provider.stock = symbol
        provider.execute_next_step = True
        provider.page = BeautifulSoup(resp.text, "html.parser")
        provider._read_page_and_get_data()
    provider._transform_data_into_csv()

    _print(name, combined_path)


# ---------------------------------------------------------------------------
# InvestorTen
# ---------------------------------------------------------------------------


def _capture_investor_ten(months: list[str] | None = None, year: str = "2024") -> None:
    name = "investor_ten"
    print(f"== {name} ==")
    # Default to all 12 months so the fixtures match what `provider.run(year=...)`
    # actually iterates over.
    months = months or list(InvestorTenProvider._MONTHS)
    written: list[Path] = []
    for month in months:
        url = InvestorTenProvider._URL.replace(":year:", year).replace(
            ":month:", month
        )
        resp = requests.get(url, headers=InvestorTenProvider._HEADERS, timeout=30)
        resp.raise_for_status()
        written.append(_write_html(f"{name}_{year}_{month}", resp.content))

    # Generate the CSV via the real provider so the column layout is authoritative.
    provider = InvestorTenProvider(
        download_path=str(CSV_DIR), filename=f"{name}.csv"
    )
    provider.run(year=year)

    # Print the first written HTML path as a "representative" output line.
    _print(name, written[0] if written else None)


# ---------------------------------------------------------------------------
# Selenium-based providers — intentionally skipped.
# ---------------------------------------------------------------------------


def _capture_status_invest() -> None:  # pragma: no cover - placeholder
    name = "status_invest"
    print(f"== {name} ==")
    print(
        "   SKIPPED: requires a fake selenium.webdriver.Chrome that writes its "
        "page_source to disk. Add after the driver_factory refactor."
    )


def _capture_funds_explorer() -> None:  # pragma: no cover - placeholder
    name = "funds_explorer"
    print(f"== {name} ==")
    print(
        "   SKIPPED: requires a fake selenium.webdriver.Chrome that writes its "
        "page_source to disk. Add after the driver_factory refactor."
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    os.makedirs(CSV_DIR, exist_ok=True)
    os.makedirs(HTML_DIR, exist_ok=True)

    captures = (
        _capture_fundamentus,
        _capture_trading_view,
        _capture_investor_ten,
        _capture_status_invest,
        _capture_funds_explorer,
    )

    for fn in captures:
        try:
            fn()
        except Exception as exc:
            print(f"== {fn.__name__} == FAILED: {type(exc).__name__}: {exc}")


if __name__ == "__main__":
    main()
