"""
Unit tests for ``FundsExplorerProvider``.

FundsExplorerProvider is a Selenium-based provider but — unlike StatusInvest
and MarketData — it does **not** drive a real file download. It loads the page
with Chrome and then reads ``driver.page_source``. That means we can isolate
the data processing from the browser entirely by replacing ``webdriver.Chrome``
with a fake via ``unittest.mock``.
"""

from __future__ import annotations

import csv
from pathlib import Path
from unittest.mock import patch

import pytest

from financial_scraper.providers.funds_explorer import FundsExplorerProvider


# ---------------------------------------------------------------------------
# HTML fixtures
# ---------------------------------------------------------------------------

FUNDS_EXPLORER_HTML = """
<html><body>
<table>
  <thead>
    <tr>
      <th>Código</th>
      <th>Setor</th>
      <th>Preço</th>
      <th>DY</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>HGLG11</td>
      <td>Logística</td>
      <td>R$ 165,00</td>
      <td>0,95%</td>
    </tr>
    <tr>
      <td>MXRF11</td>
      <td>Títulos</td>
      <td>R$ 10,30</td>
      <td>1,20%</td>
    </tr>
    <tr>
      <td>XPML11</td>
      <td>Shopping</td>
      <td>R$ 105,50</td>
      <td>0,80%</td>
    </tr>
  </tbody>
</table>
</body></html>
"""

EMPTY_FUNDS_EXPLORER_HTML = "<html><body>no table here</body></html>"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class _FakeDriver:
    """Drop-in stand-in for ``selenium.webdriver.chrome.webdriver.WebDriver``."""

    def __init__(self, html: str, *, raise_on_get: bool = False) -> None:
        self._html = html
        self.url_visited: str | None = None
        self.quit_called = False
        self.raise_on_get = raise_on_get

    def get(self, url: str) -> None:
        if self.raise_on_get:
            raise RuntimeError("navigate failed")
        self.url_visited = url

    @property
    def page_source(self) -> str:
        return self._html

    def quit(self) -> None:
        self.quit_called = True


def _build_provider(
    download_path: str,
    html: str,
    *,
    driver_raise_on_get: bool = False,
    **init_kwargs,
) -> tuple[FundsExplorerProvider, _FakeDriver]:
    """Patch ``webdriver.Chrome`` and return a configured provider with a fake driver.

    The provider is built **and** ``_config_step`` is invoked, so callers can
    exercise ``_make_request`` / ``_read_page_and_get_data`` / ``run`` without
    hitting ``AttributeError`` on ``self.driver`` (which the source sets inside
    ``_config_step``).

    Parameters
    ----------
    driver_raise_on_get:
        When True, the fake driver's ``get(...)`` raises. Used to exercise
        the ``finally: self.driver.quit()`` arm.
    """
    fake = _FakeDriver(html=html, raise_on_get=driver_raise_on_get)
    with patch(
        "financial_scraper.providers.funds_explorer.webdriver.Chrome",
        lambda options: fake,
    ):
        provider = FundsExplorerProvider(
            download_path=download_path, **init_kwargs
        )
        provider._config_step()
    return provider, fake


# ---------------------------------------------------------------------------
# _config_step
# ---------------------------------------------------------------------------


def test_config_step_creates_driver_via_chrome(
    download_path: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake = _FakeDriver(html="<html></html>")
    captured_options: list = []

    def fake_chrome(options):
        captured_options.append(options)
        return fake

    monkeypatch.setattr(
        "financial_scraper.providers.funds_explorer.webdriver.Chrome", fake_chrome
    )

    provider = FundsExplorerProvider(download_path=download_path)
    provider._config_step()

    assert provider.driver is fake
    assert len(captured_options) == 1


# ---------------------------------------------------------------------------
# _make_request
# ---------------------------------------------------------------------------


def test_make_request_captures_page_source(download_path: str) -> None:
    provider, fake = _build_provider(
        download_path, html=FUNDS_EXPLORER_HTML, wait_time=0
    )
    provider._make_request()

    assert provider.source_code == FUNDS_EXPLORER_HTML
    assert fake.quit_called is True


def test_make_request_swallows_exception_and_quits_driver(
    download_path: str,
) -> None:
    provider, fake = _build_provider(
        download_path, html="", driver_raise_on_get=True, wait_time=0
    )
    # _make_request's ``finally`` calls self.driver.quit() even on error.
    provider._make_request()

    assert fake.quit_called is True


def test_make_request_visits_ranking_url(download_path: str) -> None:
    provider, fake = _build_provider(
        download_path, html=FUNDS_EXPLORER_HTML, wait_time=0
    )
    provider._make_request()

    assert fake.url_visited == FundsExplorerProvider._FUNDS_EXPLORER_URL


# ---------------------------------------------------------------------------
# _read_page_and_get_data
# ---------------------------------------------------------------------------


def test_read_page_parses_table(download_path: str) -> None:
    provider = FundsExplorerProvider(download_path=download_path)
    provider.source_code = FUNDS_EXPLORER_HTML
    provider._read_page_and_get_data()

    assert provider.heads == ["Código", "Setor", "Preço", "DY"]
    assert len(provider.rows) == 3
    assert provider.rows[0] == ["HGLG11", "Logística", "R$ 165,00", "0,95%"]


def test_read_page_returns_none_when_no_table(download_path: str) -> None:
    provider = FundsExplorerProvider(download_path=download_path)
    provider.source_code = EMPTY_FUNDS_EXPLORER_HTML
    assert provider._read_page_and_get_data() is None


def test_read_page_returns_none_when_no_header(download_path: str) -> None:
    # Table exists but has no <thead>; matches the current implementation behaviour.
    html = "<html><body><table><tbody><tr><td>a</td></tr></tbody></table></body></html>"
    provider = FundsExplorerProvider(download_path=download_path)
    provider.source_code = html
    assert provider._read_page_and_get_data() is None


# ---------------------------------------------------------------------------
# _transform_data_into_csv
# ---------------------------------------------------------------------------


def test_transform_data_into_csv_writes_header_and_rows(download_path: str) -> None:
    provider = FundsExplorerProvider(download_path=download_path)
    provider.heads = ["Código", "Setor", "Preço", "DY"]
    provider.rows = [
        ["HGLG11", "Logística", "R$ 165,00", "0,95%"],
        ["MXRF11", "Títulos", "R$ 10,30", "1,20%"],
    ]
    # We can't easily freeze the date in this provider (it uses
    # ``datetime.today()`` inline), so just assert the file exists and has the
    # expected rows.
    provider._transform_data_into_csv()

    files = list(Path(download_path).glob("funds-*.csv"))
    assert len(files) == 1
    rows = list(csv.reader(files[0].read_text(encoding="utf-8").splitlines()))
    assert rows[0] == ["Código", "Setor", "Preço", "DY"]
    assert rows[1] == ["HGLG11", "Logística", "R$ 165,00", "0,95%"]


def test_transform_data_into_csv_uses_custom_filename(download_path: str) -> None:
    provider = FundsExplorerProvider(
        download_path=download_path, filename="mine.csv"
    )
    provider.heads = ["A"]
    provider.rows = [["x"]]
    provider._transform_data_into_csv()

    assert (Path(download_path) / "mine.csv").exists()


# ---------------------------------------------------------------------------
# run (full pipeline)
# ---------------------------------------------------------------------------


def test_run_drives_full_pipeline(download_path: str) -> None:
    fake = _FakeDriver(html=FUNDS_EXPLORER_HTML)

    with patch(
        "financial_scraper.providers.funds_explorer.webdriver.Chrome",
        lambda options: fake,
    ):
        provider = FundsExplorerProvider(
            download_path=download_path, filename="output.csv", wait_time=0
        )
        provider.run()

    output = Path(download_path) / "output.csv"
    assert output.exists()
    rows = list(csv.reader(output.read_text(encoding="utf-8").splitlines()))
    assert rows[0] == ["Código", "Setor", "Preço", "DY"]
    assert len(rows) == 1 + 3  # header + 3 data rows
    assert fake.quit_called is True


def test_run_when_no_table_leaves_attributes_unset(download_path: str) -> None:
    """Document the current behaviour on a missing table.

    The provider's ``_read_page_and_get_data`` returns ``None`` early when no
    table is found, **without** initializing ``self.heads``/``self.rows``.
    The downstream ``_transform_data_into_csv`` then accesses ``self.heads``
    and crashes. This test pins that behaviour so a future fix (e.g. gracefully
    writing an empty CSV) shows up as a deliberate change rather than a
    silent regression.
    """
    fake = _FakeDriver(html=EMPTY_FUNDS_EXPLORER_HTML)

    with patch(
        "financial_scraper.providers.funds_explorer.webdriver.Chrome",
        lambda options: fake,
    ):
        provider = FundsExplorerProvider(
            download_path=download_path, filename="output.csv", wait_time=0
        )
        with pytest.raises(AttributeError):
            provider.run()
