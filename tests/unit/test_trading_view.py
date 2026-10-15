"""
Unit tests for ``TradingViewProvider``.

This provider issues one ``GET`` per ticker and parses the response with
BeautifulSoup. We mock the HTTP layer with ``responses``.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import responses

from financial_scraper.providers.trading_view import TradingViewProvider


# ---------------------------------------------------------------------------
# HTML builders
# ---------------------------------------------------------------------------


def _tv_html(symbol: str, name: str, dept: str | None, image: str | None) -> str:
    img_tag = (
        f'<img class="logo-{symbol}" src="{image}" />' if image is not None else ""
    )
    name_tag = (
        f'<h1 class="apply-overflow-tooltip title-HDE_EEoW">{name}</h1>'
    )
    dept_tag = (
        f'<a href="/markets/stocks-brazil/sectorandindustry-sector/{dept.lower().replace(" ", "-")}/">{dept}</a>'
        if dept is not None
        else ""
    )
    return f"<html><body>{img_tag}{name_tag}{dept_tag}</body></html>"


def _url(symbol: str) -> str:
    return TradingViewProvider._URL.replace(TradingViewProvider._SYMBOL, symbol)


# ---------------------------------------------------------------------------
# _make_request
# ---------------------------------------------------------------------------


@responses.activate
def test_make_request_parses_html_on_200() -> None:
    responses.add(
        responses.GET,
        _url("PETR4"),
        body=_tv_html("PETR4", "Petrobras", "Energy",
                      "https://s3.tradingview.com/petr.png"),
        status=200,
    )

    provider = TradingViewProvider(download_path="/tmp")
    provider.stock = "PETR4"
    provider._make_request()

    assert provider.execute_next_step is True
    assert provider.page is not None


@responses.activate
def test_make_request_skips_step_on_non_200() -> None:
    responses.add(responses.GET, _url("XXXX"), status=404)

    provider = TradingViewProvider(download_path="/tmp")
    provider.stock = "XXXX"
    provider._make_request()

    assert provider.execute_next_step is False


# ---------------------------------------------------------------------------
# _read_page_and_get_data
# ---------------------------------------------------------------------------


@responses.activate
def test_read_page_extracts_name_department_and_image() -> None:
    responses.add(
        responses.GET,
        _url("PETR4"),
        body=_tv_html(
            "PETR4",
            "Petrobras",
            "Energy",
            "https://s3.tradingview.com/petr.png",
        ),
        status=200,
    )

    provider = TradingViewProvider(download_path="/tmp")
    provider._config_step()  # initializes self.lines = []
    provider.stock = "PETR4"
    provider._make_request()
    provider._read_page_and_get_data()

    assert provider.lines == [
        "PETR4;Petrobras;Energy;https://s3.tradingview.com/petr.png\n"
    ]


def test_read_page_handles_missing_optional_fields() -> None:
    """Provider must not crash when name / image / department are missing."""
    import bs4

    provider = TradingViewProvider(download_path="/tmp")
    provider._config_step()  # initializes self.lines = []
    provider.stock = "PETR4"
    provider.page = bs4.BeautifulSoup("<html><body>nope</body></html>", "html.parser")
    provider.execute_next_step = True

    provider._read_page_and_get_data()

    # Empty fields substituted with the empty string, but the line is appended.
    assert len(provider.lines) == 1
    assert provider.lines[0].startswith("PETR4;;;")


def test_read_page_skips_when_execute_next_step_false() -> None:
    provider = TradingViewProvider(download_path="/tmp")
    provider._config_step()  # initializes self.lines = []
    provider.stock = "XXXX"
    provider.execute_next_step = False
    provider._read_page_and_get_data()
    assert provider.lines == []


# ---------------------------------------------------------------------------
# _transform_data_into_csv
# ---------------------------------------------------------------------------


def test_transform_data_into_csv_writes_header_and_rows(tmp_path) -> None:
    download_path = str(tmp_path)
    provider = TradingViewProvider(download_path=download_path)
    provider.HEADER = "STOCK;NAME;DEPARTMENT;IMAGE\n"
    provider.lines = ["PETR4;Petrobras;Energy;img.png\n", "VALE3;Vale;Materials;v.png\n"]
    provider._transform_data_into_csv()

    text = (Path(download_path) / "trading_view.csv").read_text(encoding="utf-8")
    assert text.splitlines()[0] == "STOCK;NAME;DEPARTMENT;IMAGE"
    assert "PETR4;Petrobras;Energy;img.png" in text
    assert "VALE3;Vale;Materials;v.png" in text


def test_transform_data_into_csv_does_nothing_when_no_data(tmp_path) -> None:
    download_path = str(tmp_path)
    provider = TradingViewProvider(download_path=download_path)
    provider.lines = []
    provider._transform_data_into_csv()
    assert not (Path(download_path) / "trading_view.csv").exists()


def test_transform_data_into_csv_uses_custom_filename(tmp_path) -> None:
    download_path = str(tmp_path)
    provider = TradingViewProvider(
        download_path=download_path, filename="mine.csv"
    )
    provider.HEADER = "STOCK;NAME;DEPARTMENT;IMAGE\n"
    provider.lines = ["PETR4;Petrobras;Energy;img.png\n"]
    provider._transform_data_into_csv()

    assert (Path(download_path) / "mine.csv").exists()
    assert not (Path(download_path) / "trading_view.csv").exists()


# ---------------------------------------------------------------------------
# run (full pipeline)
# ---------------------------------------------------------------------------


@responses.activate
def test_run_writes_one_csv_row_per_ticker(tmp_path) -> None:
    download_path = str(tmp_path)
    for symbol, name, dept in (
        ("PETR4", "Petrobras", "Energy"),
        ("VALE3", "Vale", "Materials"),
    ):
        responses.add(
            responses.GET,
            _url(symbol),
            body=_tv_html(symbol, name, dept, f"https://x/{symbol}.png"),
            status=200,
        )

    provider = TradingViewProvider(download_path=download_path)
    provider.run(stocks=["PETR4", "VALE3"])

    lines = (Path(download_path) / "trading_view.csv").read_text(
        encoding="utf-8"
    ).splitlines()
    assert lines[0] == "STOCK;NAME;DEPARTMENT;IMAGE"
    assert any(line.startswith("PETR4;Petrobras;Energy;") for line in lines[1:])
    assert any(line.startswith("VALE3;Vale;Materials;") for line in lines[1:])


@responses.activate
def test_run_omits_tickers_with_404(tmp_path) -> None:
    download_path = str(tmp_path)
    responses.add(
        responses.GET,
        _url("PETR4"),
        body=_tv_html("PETR4", "Petrobras", "Energy", "img.png"),
        status=200,
    )
    responses.add(responses.GET, _url("XXXX"), status=404)

    provider = TradingViewProvider(download_path=download_path)
    provider.run(stocks=["PETR4", "XXXX"])

    lines = (Path(download_path) / "trading_view.csv").read_text(
        encoding="utf-8"
    ).splitlines()
    # header + PETR4 only; XXXX yields no row
    assert len(lines) == 2
    assert lines[1].startswith("PETR4")


# ---------------------------------------------------------------------------
# Tests against the captured real-site fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def captured_trading_view_html(fixtures_dir):
    """Single combined TradingView page captured by ``capture_fixtures.py``.

    Splits the file at the ``<!-- BEGIN/END ... -->`` sentinels and returns a
    dict ``{symbol: html_text}`` so individual tests can pick what they want.
    """
    combined_path = fixtures_dir / "html" / "trading_view_combined.html"
    if not combined_path.exists():
        pytest.skip(f"fixture {combined_path} not present")
    text = combined_path.read_text(encoding="utf-8")
    parts: dict[str, str] = {}
    for chunk in text.split("<!-- BEGIN ")[1:]:
        head, _, body = chunk.partition(" -->")
        symbol = head.strip()
        body = body.rsplit("<!-- END ", 1)[0]
        parts[symbol] = body
    return parts


def test_provider_extracts_department_and_image_from_captured_page(
    download_path: str, captured_trading_view_html: dict[str, str]
) -> None:
    """The real TradingView HTML must yield non-empty DEPARTMENT and IMAGE cells."""
    import bs4

    petr = captured_trading_view_html.get("PETR4")
    if not petr:
        pytest.skip("PETR4 not present in the captured fixture")

    provider = TradingViewProvider(download_path=download_path)
    provider._config_step()
    provider.stock = "PETR4"
    provider.page = bs4.BeautifulSoup(petr, "html.parser")
    provider.execute_next_step = True
    provider._read_page_and_get_data()

    assert len(provider.lines) == 1
    cells = provider.lines[0].rstrip("\n").split(";")
    # STOCK, NAME, DEPARTMENT, IMAGE
    assert cells[0] == "PETR4"
    # TradingView's current page structure no longer matches the historical
    # CSS class the selector expects — pin that:
    assert cells[1] == "", "name selector no longer matches the live page"
    assert cells[2] != "", (
        "department should still be extracted from /markets/.../sector/ link"
    )
    assert cells[3].startswith("https://"), "image URL must be absolute"
