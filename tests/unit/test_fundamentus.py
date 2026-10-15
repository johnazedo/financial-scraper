"""
Unit tests for ``FundamentusProvider``.

Approach
--------
- Mock ``requests.get`` with the ``responses`` library.
- Pin ``datetime.now()`` with ``freezegun`` so the default filename is deterministic.
- All filesystem writes go to pytest's ``tmp_path`` (via the ``download_path`` fixture).

These tests intentionally avoid hitting the real Fundamentus website.
"""

from __future__ import annotations

import pandas as pd
import pytest
import responses
from freezegun import freeze_time

from financial_scraper.providers.fundamentus import FundamentusProvider


# ---------------------------------------------------------------------------
# Inline HTML fixture
# ---------------------------------------------------------------------------

FUNDAMENTUS_HTML = """
<html>
  <body>
    <table>
      <tr>
        <th>Ticker</th>
        <th>P/L</th>
        <th>DY</th>
      </tr>
      <tr>
        <td>PETR4</td><td>5,2</td><td>12,3%</td>
      </tr>
      <tr>
        <td>VALE3</td><td>3,1</td><td>9,8%</td>
      </tr>
      <tr>
        <td>ITUB4</td><td>7,8</td><td>6,1%</td>
      </tr>
    </table>
  </body>
</html>
"""


# ---------------------------------------------------------------------------
# _make_request
# ---------------------------------------------------------------------------


@responses.activate
def test_make_request_stores_html_content_on_success() -> None:
    responses.add(
        responses.GET,
        FundamentusProvider._URL,
        body=FUNDAMENTUS_HTML,
        status=200,
    )

    provider = FundamentusProvider(download_path="/tmp")
    provider._make_request()

    assert provider.html_content == FUNDAMENTUS_HTML.encode("utf-8")


@responses.activate
def test_make_request_sends_user_agent_header() -> None:
    responses.add(
        responses.GET,
        FundamentusProvider._URL,
        body=FUNDAMENTUS_HTML,
        status=200,
    )

    provider = FundamentusProvider(download_path="/tmp")
    provider._make_request()

    assert len(responses.calls) == 1
    # Browser-like UA is required by Fundamentus to avoid a 403.
    ua = responses.calls[0].request.headers.get("User-Agent", "")
    assert "Mozilla" in ua


@responses.activate
def test_make_request_raises_on_http_error() -> None:
    responses.add(responses.GET, FundamentusProvider._URL, status=500)

    provider = FundamentusProvider(download_path="/tmp")
    with pytest.raises(Exception):
        provider._make_request()


# ---------------------------------------------------------------------------
# _read_page_and_get_data
# ---------------------------------------------------------------------------


def test_read_page_and_get_data_builds_dataframe() -> None:
    provider = FundamentusProvider(download_path="/tmp")
    provider.html_content = FUNDAMENTUS_HTML.encode("utf-8")
    provider._read_page_and_get_data()

    assert isinstance(provider.df, pd.DataFrame)
    assert list(provider.df.columns) == ["Ticker", "P/L", "DY"]
    assert provider.df.iloc[0]["Ticker"] == "PETR4"
    # Header row excluded
    assert len(provider.df) == 3


def test_read_page_and_get_data_raises_when_table_missing() -> None:
    provider = FundamentusProvider(download_path="/tmp")
    provider.html_content = b"<html><body><p>no table here</p></body></html>"
    with pytest.raises(Exception):
        provider._read_page_and_get_data()


# ---------------------------------------------------------------------------
# _transform_data_into_csv
# ---------------------------------------------------------------------------


@freeze_time("2026-01-15")
def test_transform_data_into_csv_uses_default_date_based_name(download_path: str) -> None:
    provider = FundamentusProvider(download_path=download_path)
    provider.df = pd.DataFrame({"Ticker": ["PETR4"], "P/L": ["5,2"], "DY": ["12,3%"]})
    provider._transform_data_into_csv()

    assert (  # noqa: WPS421 — Path doesn't have a direct ``in tmp_path`` check
        __import__("pathlib").Path(download_path) / "fundamentus-15-01-2026.csv"
    ).exists()


def test_transform_data_into_csv_respects_custom_filename(download_path: str) -> None:
    provider = FundamentusProvider(
        download_path=download_path, filename="mine.csv"
    )
    provider.df = pd.DataFrame({"Ticker": ["VALE3"]})
    provider._transform_data_into_csv()

    from pathlib import Path

    assert (Path(download_path) / "mine.csv").exists()


def test_transform_data_into_csv_uses_semicolon_separator(download_path: str) -> None:
    provider = FundamentusProvider(
        download_path=download_path, filename="semi.csv"
    )
    provider.df = pd.DataFrame({"A": [1], "B": [2]})
    provider._transform_data_into_csv()

    from pathlib import Path

    text = (Path(download_path) / "semi.csv").read_text(encoding="utf-8")
    # Header must use ';' as separator
    assert text.splitlines()[0] == "A;B"


# ---------------------------------------------------------------------------
# run (full pipeline)
# ---------------------------------------------------------------------------


@responses.activate
@freeze_time("2026-01-15")
def test_run_writes_expected_csv(download_path: str) -> None:
    responses.add(
        responses.GET,
        FundamentusProvider._URL,
        body=FUNDAMENTUS_HTML,
        status=200,
    )

    provider = FundamentusProvider(download_path=download_path)
    provider.run()

    from pathlib import Path

    out = Path(download_path) / "fundamentus-15-01-2026.csv"
    assert out.exists()

    df = pd.read_csv(out, sep=";")
    assert list(df.columns) == ["Ticker", "P/L", "DY"]
    assert set(df["Ticker"]) == {"PETR4", "VALE3", "ITUB4"}


@responses.activate
def test_run_uses_custom_filename(download_path: str) -> None:
    responses.add(
        responses.GET,
        FundamentusProvider._URL,
        body=FUNDAMENTUS_HTML,
        status=200,
    )

    provider = FundamentusProvider(
        download_path=download_path, filename="custom.csv"
    )
    provider.run()

    from pathlib import Path

    assert (Path(download_path) / "custom.csv").exists()
    # No date-suffixed file should have been written
    assert not any(
        p.name.startswith("fundamentus-") for p in Path(download_path).iterdir()
    )


# ---------------------------------------------------------------------------
# Tests against the captured real-site fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def captured_fundamentus_html(fixtures_dir):
    """The live Fundamentus page captured by ``tests/scripts/capture_fixtures.py``.

    Skips when the fixture isn't committed yet — that lets the test file be
    checked in before the (large) HTML snapshot itself.
    """
    path = fixtures_dir / "html" / "fundamentus.html"
    if not path.exists():
        pytest.skip(f"fixture {path.name} not present")
    return path.read_bytes()


def test_provider_parses_captured_real_page(
    download_path: str, captured_fundamentus_html: bytes
) -> None:
    """End-to-end: the real (captured) page must drive the provider to a CSV."""
    provider = FundamentusProvider(download_path=download_path)
    provider.html_content = captured_fundamentus_html
    provider._read_page_and_get_data()
    provider._transform_data_into_csv()

    from pathlib import Path

    csvs = list(Path(download_path).glob("fundamentus-*.csv"))
    assert len(csvs) == 1
    df = pd.read_csv(csvs[0], sep=";")
    # The captured page contains the real Brazilian stock market tickers; assert a
    # handful of well-known symbols are present so the fixture is exercising the
    # right page.
    assert {"PETR4", "VALE3", "ITUB4"} <= set(df["Papel"].astype(str))

    # The captured CSV should roughly match the size of the committed reference.
    reference = (Path(__file__).resolve().parents[1] / "fixtures" / "csv" / "fundamentus.csv")
    if reference.exists():
        rows = sum(1 for _ in reference.open(encoding="utf-8")) - 1  # minus header
        # The live page should have roughly as many stocks as the reference
        # capture (allow some slack since the universe changes over time).
        assert abs(len(df) - rows) <= 50, (
            f"Captured page row count {len(df)} drifted too far from "
            f"reference {rows}"
        )
