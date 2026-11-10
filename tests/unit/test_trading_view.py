"""
Unit tests for ``TradingViewProvider``.

This provider issues one ``GET`` per ticker and parses the response with
BeautifulSoup. We mock the HTTP layer with ``responses``.

``run_quotes`` is covered separately: it POSTs to the TradingView scanner
endpoint once per market and returns the parsed rows in memory.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import requests
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


# ---------------------------------------------------------------------------
# run_quotes (TradingView scanner endpoint)
# ---------------------------------------------------------------------------


def _scanner_url(market: str) -> str:
    return TradingViewProvider._SCANNER_URL.format(market=market)


def _scanner_body(symbol: str, ticker: str, price: float, currency: str = "BRL",
                  exchange: str = "BMFBOVESPA") -> dict:
    """Build a scanner response body with one row."""
    row = {
        "name": ticker,
        "description": f"{ticker} description",
        "close": price,
        "change": 1.5,
        "change_abs": 0.75,
        "volume": 1000,
        "average_volume_10d_calc": 2000,
        "market_cap_basic": 5000,
        "currency": currency,
        "exchange": exchange,
        "sector": "Energy Minerals",
        "industry": "Integrated Oil",
        "price_earnings_ttm": 7.5,
        "dividends_yield": 0,
        "Perf.Y": 12.5,
        "Perf.1M": -3.5,
        "Volatility.D": 25.0,
    }
    columns = [column for column, _ in TradingViewProvider._QUOTE_FIELDS]
    return {
        "totalCount": 1,
        "data": [{"s": symbol, "d": [row[column] for column in columns]}],
    }


def _register(market: str, body: dict) -> None:
    responses.add(
        responses.POST,
        _scanner_url(market),
        json=body,
        status=200,
    )


def _requested_symbols() -> dict[str, list[str]]:
    """Map scanner URL -> list of tickers sent in the request body."""
    sent: dict[str, list[str]] = {}
    for call in responses.calls:
        market = call.request.url.rstrip("/").split("/")[-2]
        payload = json.loads(call.request.body)
        sent.setdefault(market, []).extend(payload["symbols"]["tickers"])
    return sent


@responses.activate
def test_run_quotes_returns_price_for_br_ticker(download_path: str) -> None:
    # Given a B3 ticker
    _register("brazil", _scanner_body("BMFBOVESPA:PETR4", "PETR4", 45.19))
    _register("america", {"totalCount": 0, "data": []})

    provider = TradingViewProvider(download_path=download_path)

    # When the quotes are fetched
    quotes = provider.run_quotes(stocks=["PETR4"])

    # Then the price is returned in memory
    assert len(quotes) == 1
    assert quotes[0]["ticker"] == "PETR4"
    assert quotes[0]["price"] == 45.19
    assert quotes[0]["currency"] == "BRL"
    assert quotes[0]["symbol"] == "BMFBOVESPA:PETR4"
    assert quotes[0]["market"] == "brazil"


@responses.activate
def test_run_quotes_returns_price_for_us_ticker(download_path: str) -> None:
    # Given a US ticker that resolves on NASDAQ
    _register("brazil", {"totalCount": 0, "data": []})
    _register("america", _scanner_body("NASDAQ:AAPL", "AAPL", 350.69,
                                       currency="USD", exchange="NASDAQ"))

    provider = TradingViewProvider(download_path=download_path)

    # When the quotes are fetched
    quotes = provider.run_quotes(stocks=["AAPL"])

    # Then the US price is returned
    assert len(quotes) == 1
    assert quotes[0]["ticker"] == "AAPL"
    assert quotes[0]["price"] == 350.69
    assert quotes[0]["currency"] == "USD"
    assert quotes[0]["exchange"] == "NASDAQ"
    assert quotes[0]["market"] == "america"


@responses.activate
def test_run_quotes_handles_br_and_us_in_a_single_call(download_path: str) -> None:
    # Given one Brazilian and one US ticker
    _register("brazil", _scanner_body("BMFBOVESPA:PETR4", "PETR4", 45.19))
    _register("america", _scanner_body("NASDAQ:AAPL", "AAPL", 350.69,
                                       currency="USD", exchange="NASDAQ"))

    provider = TradingViewProvider(download_path=download_path)

    # When the quotes are fetched
    quotes = provider.run_quotes(stocks=["PETR4", "AAPL"])

    # Then both markets are answered
    assert {q["ticker"] for q in quotes} == {"PETR4", "AAPL"}
    assert len(responses.calls) == 2


@responses.activate
def test_run_quotes_probes_every_exchange_for_plain_tickers(download_path: str) -> None:
    # Given a plain US ticker
    _register("brazil", {"totalCount": 0, "data": []})
    _register("america", {"totalCount": 0, "data": []})

    provider = TradingViewProvider(download_path=download_path)
    provider.run_quotes(stocks=["AAPL"])

    # Then every known exchange is probed so the right one resolves
    sent = _requested_symbols()
    assert "BMFBOVESPA:AAPL" in sent["brazil"]
    for exchange in TradingViewProvider._US_EXCHANGES:
        assert f"{exchange}:AAPL" in sent["america"]


@responses.activate
def test_run_quotes_keeps_qualified_tickers_untouched(download_path: str) -> None:
    # Given an already qualified US ticker
    _register("america", _scanner_body("NASDAQ:AAPL", "AAPL", 350.69,
                                       currency="USD", exchange="NASDAQ"))

    provider = TradingViewProvider(download_path=download_path)
    provider.run_quotes(stocks=["NASDAQ:AAPL"])

    # Then only the US market is queried, without probing other exchanges
    sent = _requested_symbols()
    assert list(sent.keys()) == ["america"]
    assert sent["america"] == ["NASDAQ:AAPL"]


@responses.activate
def test_run_quotes_brazil_mode_skips_us_market(download_path: str) -> None:
    # Given the explicit brazil exchange hint
    _register("brazil", _scanner_body("BMFBOVESPA:PETR4", "PETR4", 45.19))

    provider = TradingViewProvider(download_path=download_path)
    provider.run_quotes(stocks=["PETR4"], exchange="brazil")

    # Then only B3 is queried
    sent = _requested_symbols()
    assert list(sent.keys()) == ["brazil"]
    assert sent["brazil"] == ["BMFBOVESPA:PETR4"]


@responses.activate
def test_run_quotes_america_mode_skips_brazil_market(download_path: str) -> None:
    # Given the explicit america exchange hint
    _register("america", {"totalCount": 0, "data": []})

    provider = TradingViewProvider(download_path=download_path)
    provider.run_quotes(stocks=["AAPL"], exchange="america")

    # Then only the US market is queried
    sent = _requested_symbols()
    assert list(sent.keys()) == ["america"]
    assert "NASDAQ:AAPL" in sent["america"]
    assert "BMFBOVESPA:AAPL" not in sent["america"]


@responses.activate
def test_run_quotes_writes_csv(download_path: str) -> None:
    # Given a resolved ticker
    _register("brazil", _scanner_body("BMFBOVESPA:PETR4", "PETR4", 45.19))
    _register("america", {"totalCount": 0, "data": []})

    provider = TradingViewProvider(download_path=download_path)
    provider.run_quotes(stocks=["PETR4"])

    # Then the CSV holds the header and the row
    text = (Path(download_path) / "trading_view_quotes.csv").read_text(encoding="utf-8")
    lines = text.splitlines()
    assert lines[0].startswith("TICKER;COMPANY;PRICE;")
    assert "PETR4" in lines[1]
    assert "45.19" in lines[1]


@responses.activate
def test_run_quotes_uses_custom_filename(download_path: str) -> None:
    # Given a custom filename
    _register("brazil", _scanner_body("BMFBOVESPA:PETR4", "PETR4", 45.19))
    _register("america", {"totalCount": 0, "data": []})

    provider = TradingViewProvider(download_path=download_path, quotes_filename="mine.csv")
    provider.run_quotes(stocks=["PETR4"])

    # Then the custom name is used
    assert (Path(download_path) / "mine.csv").exists()
    assert not (Path(download_path) / "trading_view_quotes.csv").exists()


@responses.activate
def test_run_quotes_skips_unresolved_tickers(download_path: str) -> None:
    # Given a ticker the scanner does not know
    _register("brazil", {"totalCount": 0, "data": []})
    _register("america", {"totalCount": 0, "data": []})

    provider = TradingViewProvider(download_path=download_path)
    quotes = provider.run_quotes(stocks=["ZZZZ"])

    # Then no row is produced and no CSV is written
    assert quotes == []
    assert not (Path(download_path) / "trading_view_quotes.csv").exists()


@responses.activate
def test_run_quotes_survives_a_network_error(download_path: str) -> None:
    # Given a failing scanner
    responses.add(
        responses.POST,
        _scanner_url("brazil"),
        body=requests.ConnectionError("boom"),
    )
    responses.add(
        responses.POST,
        _scanner_url("america"),
        body=requests.ConnectionError("boom"),
    )

    provider = TradingViewProvider(download_path=download_path)

    # When the quotes are fetched
    quotes = provider.run_quotes(stocks=["PETR4"])

    # Then the provider swallows the error and returns nothing
    assert quotes == []


@responses.activate
def test_run_quotes_normalizes_class_share_tickers(download_path: str) -> None:
    # Given a class share ticker written the Yahoo way
    _register("brazil", {"totalCount": 0, "data": []})
    _register("america", _scanner_body("NYSE:BRK.B", "BRK.B", 575.25,
                                       currency="USD", exchange="NYSE"))

    provider = TradingViewProvider(download_path=download_path)
    quotes = provider.run_quotes(stocks=["BRK_B"])

    # Then it is sent in TradingView's dotted form and resolves
    sent = _requested_symbols()
    assert "NYSE:BRK.B" in sent["america"]
    assert len(quotes) == 1
    assert quotes[0]["ticker"] == "BRK.B"
    assert quotes[0]["price"] == 575.25


@responses.activate
def test_run_quotes_keeps_the_best_row_when_a_ticker_matches_twice(download_path: str) -> None:
    # Given a ticker that resolves on both markets
    _register("brazil", _scanner_body("BMFBOVESPA:VALE3", "VALE3", 66.11))
    _register("america", _scanner_body("NASDAQ:VALE3", "VALE3", 12.0,
                                       currency="USD", exchange="NASDAQ"))

    provider = TradingViewProvider(download_path=download_path)
    quotes = provider.run_quotes(stocks=["VALE3"])

    # Then the B3 row wins because the ticker looks like a B3 ticker
    assert len(quotes) == 1
    assert quotes[0]["market"] == "brazil"
    assert quotes[0]["price"] == 66.11
