"""
Unit tests for ``InvestorTenProvider``.

This provider issues one ``GET`` per month via the ``requests`` library and
parses the response with BeautifulSoup. We mock all HTTP calls with
``responses`` and assert against the CSV that the provider writes to disk.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import List

import pytest
import responses

from financial_scraper.providers.investor_ten import InvestorTenProvider


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _month_url(year: str, month: str) -> str:
    return InvestorTenProvider._URL.replace(":year:", year).replace(":month:", month)


def _table_html(tickers: List[str]) -> str:
    """Minimal HTML that matches the CSS selector used by InvestorTenProvider.

    Selector (from the source):
        table.min-w-full.bg-white.md\\:shadow.border-collapse.border-spacing-0
    """
    rows = []
    for ticker in tickers:
        rows.append(
            "<tr>"
            f"<td><span class=\"ticker-name\">{ticker}</span>rest</td>"
            "<td>Data Com 01/12/2023</td>"
            "<td>Pgto 02/12/2023</td>"
            "<td>Rendimento</td>"
            "<td>R$ 1,23</td>"
            "</tr>"
        )
    return (
        "<html><body>"
        "<table class=\"min-w-full bg-white md:shadow border-collapse border-spacing-0\">"
        "<tbody>" + "".join(rows) + "</tbody>"
        "</table>"
        "</body></html>"
    )


# ---------------------------------------------------------------------------
# _make_request
# ---------------------------------------------------------------------------


@responses.activate
def test_make_request_stores_response_text(download_path: str) -> None:
    body = _table_html(["HGLG11"])
    responses.add(
        responses.GET,
        _month_url("2023", "janeiro"),
        body=body,
        status=200,
    )

    provider = InvestorTenProvider(download_path=download_path)
    provider.year = "2023"
    provider.month = "janeiro"
    provider._make_request()

    assert provider.response == body
    assert provider.table is not None


@responses.activate
def test_make_request_returns_early_when_table_missing(download_path: str) -> None:
    # Valid HTML, but missing the table the provider expects.
    responses.add(
        responses.GET,
        _month_url("2023", "janeiro"),
        body="<html><body>no table</body></html>",
        status=200,
    )

    provider = InvestorTenProvider(download_path=download_path)
    provider.year = "2023"
    provider.month = "janeiro"
    provider._make_request()

    assert provider.table is None


@responses.activate
def test_make_request_sends_browser_headers(download_path: str) -> None:
    responses.add(
        responses.GET,
        _month_url("2023", "janeiro"),
        body=_table_html(["HGLG11"]),
        status=200,
    )

    provider = InvestorTenProvider(download_path=download_path)
    provider.year = "2023"
    provider.month = "janeiro"
    provider._make_request()

    assert len(responses.calls) == 1
    headers = responses.calls[0].request.headers
    assert "Mozilla" in headers.get("User-Agent", "")
    assert headers.get("Accept-Language", "").startswith("pt-BR")


@responses.activate
def test_make_request_raises_on_http_error(download_path: str) -> None:
    responses.add(responses.GET, _month_url("2023", "janeiro"), status=500)

    provider = InvestorTenProvider(download_path=download_path)
    provider.year = "2023"
    provider.month = "janeiro"
    with pytest.raises(Exception):
        provider._make_request()


# ---------------------------------------------------------------------------
# _read_page_and_get_data
# ---------------------------------------------------------------------------


def test_read_page_and_get_data_appends_one_row_per_ticker(
    download_path: str,
) -> None:
    provider = InvestorTenProvider(download_path=download_path)
    provider.year = "2023"
    provider.month = "janeiro"

    html = _table_html(["HGLG11", "MXRF11"])
    import bs4

    provider.response = html
    provider.table = bs4.BeautifulSoup(html, "html.parser").select_one(
        "table.min-w-full.bg-white.md\\:shadow.border-collapse.border-spacing-0"
    )
    provider.result = []
    provider._read_page_and_get_data()

    assert len(provider.result) == 2


# ---------------------------------------------------------------------------
# _clean_data
# ---------------------------------------------------------------------------


def test_clean_data_normalizes_basic_row(download_path: str) -> None:
    provider = InvestorTenProvider(download_path=download_path)
    row = [
        "HGLG11\nSome suffix to drop",
        "01/12/2023 Data Com",
        "02/12/2023 Pgto",
        "Rendimento",
        "R$ 1,23",
    ]
    cleaned = provider._clean_data(row)

    # FII column drops the suffix
    assert cleaned[0] == "HGLG11"
    # Slashes replaced, "Data Com" stripped
    assert cleaned[1] == "01-12-2023"
    # Slashes replaced, "Pgto" stripped
    assert cleaned[2] == "02-12-2023"
    # Value column: "R$" stripped, comma replaced with dot
    assert cleaned[4] == "1.23"


def test_clean_data_handles_value_without_currency_symbol(download_path: str) -> None:
    provider = InvestorTenProvider(download_path=download_path)
    row = ["HGLG11", "01-12-2023", "02-12-2023", "Rendimento", "1,23"]
    cleaned = provider._clean_data(row)
    assert cleaned[4] == "1.23"


# ---------------------------------------------------------------------------
# _transform_data_into_csv
# ---------------------------------------------------------------------------


def test_transform_data_into_csv_writes_header_and_rows(download_path: str) -> None:
    provider = InvestorTenProvider(download_path=download_path)
    provider.year = "2023"
    provider.result = [
        ["HGLG11", "01-12-2023", "02-12-2023", "Rendimento", "1,23"],
    ]
    provider._transform_data_into_csv()

    out = Path(download_path) / "funds-2023.csv"
    assert out.exists()
    rows = list(csv.reader(out.read_text(encoding="utf-8").splitlines(), delimiter=";"))
    assert rows[0] == ["FII", "Data Com", "Data Pagamento", "Tipo", "Valor"]
    assert rows[1] == ["HGLG11", "01-12-2023", "02-12-2023", "Rendimento", "1,23"]


def test_transform_data_into_csv_uses_custom_filename(download_path: str) -> None:
    provider = InvestorTenProvider(download_path=download_path, filename="fiis.csv")
    provider.year = "2023"
    provider.result = [["HGLG11", "01-12-2023", "02-12-2023", "Rendimento", "1,23"]]
    provider._transform_data_into_csv()

    assert (Path(download_path) / "fiis.csv").exists()
    assert not (Path(download_path) / "funds-2023.csv").exists()


def test_transform_data_into_csv_overwrites_on_rerun(download_path: str) -> None:
    """Regression: running the provider twice for the same year must NOT
    duplicate data. The file must be opened in write mode (truncate), not
    append mode.
    """
    out = Path(download_path) / "funds-2023.csv"

    provider = InvestorTenProvider(download_path=download_path)
    provider.year = "2023"
    provider.result = [
        ["HGLG11", "01-12-2023", "02-12-2023", "Rendimento", "1,23"],
        ["MXRF11", "03-12-2023", "04-12-2023", "Rendimento", "0,10"],
    ]
    provider._transform_data_into_csv()

    provider.result = [["HGLG11", "01-12-2023", "02-12-2023", "Rendimento", "1,23"]]
    provider._transform_data_into_csv()

    rows = list(csv.reader(out.read_text(encoding="utf-8").splitlines(), delimiter=";"))
    # header + 1 data row, NOT 1 + 2 + 1 from a duplicated file
    assert len(rows) == 1 + 1, rows


# ---------------------------------------------------------------------------
# run (full pipeline)
# ---------------------------------------------------------------------------


@responses.activate
def test_run_aggregates_rows_across_all_months(download_path: str) -> None:
    # Mock every month with two tickers per month.
    for month in InvestorTenProvider._MONTHS:
        responses.add(
            responses.GET,
            _month_url("2023", month),
            body=_table_html(["HGLG11", "MXRF11"]),
            status=200,
        )

    provider = InvestorTenProvider(download_path=download_path)
    provider.run("2023")

    out = Path(download_path) / "funds-2023.csv"
    rows = list(csv.reader(out.read_text(encoding="utf-8").splitlines(), delimiter=";"))
    # header + 12 months * 2 tickers
    assert len(rows) == 1 + 12 * 2


@responses.activate
def test_run_swallows_failed_months_but_continues(download_path: str) -> None:
    # First month fails, the rest succeed. The provider has a bare ``except:`` in
    # run() that intentionally keeps the loop alive.
    responses.add(responses.GET, _month_url("2023", "janeiro"), status=500)
    for month in InvestorTenProvider._MONTHS[1:]:
        responses.add(
            responses.GET,
            _month_url("2023", month),
            body=_table_html(["HGLG11"]),
            status=200,
        )

    provider = InvestorTenProvider(download_path=download_path)
    provider.run("2023")

    # The pipeline must still produce an output file with 11 months of data.
    out = Path(download_path) / "funds-2023.csv"
    rows = list(csv.reader(out.read_text(encoding="utf-8").splitlines(), delimiter=";"))
    assert len(rows) == 1 + 11  # header + 11 successful months


# ---------------------------------------------------------------------------
# Tests against the captured real-site fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def captured_investor_ten_janeiro_html(fixtures_dir):
    """The live jan/2024 page captured by ``capture_fixtures.py``."""
    path = fixtures_dir / "html" / "investor_ten_2024_janeiro.html"
    if not path.exists():
        pytest.skip(f"fixture {path} not present")
    return path.read_text(encoding="utf-8")


def test_provider_parses_captured_real_page(
    download_path: str, captured_investor_ten_janeiro_html: str
) -> None:
    """End-to-end: the real (captured) page must drive the provider to a CSV."""
    provider = InvestorTenProvider(
        download_path=download_path, filename="real.csv"
    )
    provider.year = "2024"
    provider.month = "janeiro"

    # Replicate what _make_request does: parse the response and populate
    # ``self.table``. We don't go through _make_request itself so we don't
    # hit the network.
    provider.response = captured_investor_ten_janeiro_html
    provider.table = _select_dividend_table(provider.response)
    provider.result = []
    provider._read_page_and_get_data()

    # The captured page contains ~377 FIIs; require at least 100 so we are
    # genuinely parsing the page, not a stub.
    assert len(provider.result) >= 100

    provider._transform_data_into_csv()
    assert (Path(download_path) / "real.csv").exists()


def _select_dividend_table(html: str):
    """Small helper so both fixture tests share the same selector logic."""
    from bs4 import BeautifulSoup

    return BeautifulSoup(html, "html.parser").select_one(
        "table.min-w-full.bg-white.md\\:shadow.border-collapse.border-spacing-0"
    )


def test_captured_csv_matches_provider_output(
    download_path: str, captured_investor_ten_janeiro_html: str
) -> None:
    """Reference snapshot: replay the captured january page through the
    provider and compare its jan/2024 row count to the committed CSV.

    The captured CSV is grouped by year+month (column ``Data Com`` ends with
    the YY suffix), so we can pull out exactly the jan/2024 bucket from the
    reference to compare against ``provider.result``.
    """
    from collections import Counter
    import csv as csvlib

    reference = Path(__file__).resolve().parents[1] / "fixtures" / "csv" / "investor_ten.csv"
    if not reference.exists():
        pytest.skip("reference csv not present")

    provider = InvestorTenProvider(download_path=download_path, filename="x.csv")
    provider.year = "2024"
    provider.month = "janeiro"
    provider.response = captured_investor_ten_janeiro_html
    provider.table = _select_dividend_table(provider.response)
    provider.result = []
    provider._read_page_and_get_data()

    # Count rows in the reference CSV grouped by (MM, YY) on the "Data Com"
    # column. The reference's jan/2024 bucket is the comparison target.
    rows = list(csvlib.reader(reference.open(encoding="utf-8"), delimiter=";"))
    bucket = Counter()
    for r in rows[1:]:
        if len(r) > 1 and r[1].count("-") == 2:
            _, mm, yy = r[1].split("-")
            bucket[(mm, yy)] += 1
    ref_jan_24 = bucket[("01", "24")]
    parsed = len(provider.result)

    assert parsed == ref_jan_24, (
        f"Parsed {parsed} FIIs for jan/2024, but the reference snapshot "
        f"contains {ref_jan_24} rows for jan/2024. This usually means the "
        f"site CSS changed or the parser dropped some <tr> tags."
    )
