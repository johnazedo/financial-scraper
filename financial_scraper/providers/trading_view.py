import csv
import os
import re
from typing import Any, List
import requests
from requests import Response
from bs4 import BeautifulSoup
from financial_scraper.config.utils import Log


class TradingViewProvider():
    """
    A provider for scraping stock information from TradingView website.
    
    This class retrieves basic information about stocks from the Brazilian stock market
    (B3/BMFBOVESPA) including stock name, department/sector, and logo image URL.
    The data is collected from the TradingView website and saved into a CSV file.
    
    It also exposes :meth:`run_quotes`, a bulk quote lookup that accepts a list of
    tickers from **Brazil (B3) and/or the United States** and returns the price,
    change, volume and fundamentals of every ticker in a single pass.

    Attributes:
        download_path (str): Directory path where the CSV file will be saved.
        filename (str, optional): Custom filename for the output CSV file.
                                 If not provided, defaults to 'trading_view.csv'.
        quotes_filename (str, optional): Custom filename for the quotes CSV file.
                                 If not provided, defaults to 'trading_view_quotes.csv'.
    """

    _SYMBOL = ":stock:"
    _URL = f"https://br.tradingview.com/symbols/BMFBOVESPA-{_SYMBOL}/"
    # _URL_STATISTICS = f"https://br.tradingview.com/symbols/BMFBOVESPA-{_SYMBOL}/financials-statistics-and-ratios/"
    # _URL_DEMOSTRATIONS = f"https://br.tradingview.com/symbols/BMFBOVESPA-{_SYMBOL}/financials-income-statement/"
    _DEFAULT_FILENAME = "trading_view.csv"
    # - SEARCH_STRING - HEADER

    # ------------------------------------------------------------------
    # Quotes: TradingView scanner endpoint (free, no API key required)
    # ------------------------------------------------------------------
    _SCANNER_URL = "https://scanner.tradingview.com/{market}/scan"
    _BR_EXCHANGE = "BMFBOVESPA"
    _BR_MARKET = "brazil"
    _US_MARKET = "america"
    _US_EXCHANGES = ("NASDAQ", "NYSE", "AMEX", "OTC")
    _DEFAULT_QUOTES_FILENAME = "trading_view_quotes.csv"
    _REQUEST_TIMEOUT = 30
    _SCANNER_HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36' +
                      ' (KHTML, like Gecko) Chrome/120.0 Safari/537.36',
        'Content-Type': 'application/json',
        'Referer': 'https://www.tradingview.com/',
    }
    # Accepted values for the ``exchange`` argument of :meth:`run_quotes`.
    _AUTO = "auto"
    _EXCHANGE_MODES = {
        'AUTO': _AUTO,
        'BR': _BR_MARKET,
        'BRAZIL': _BR_MARKET,
        'B3': _BR_MARKET,
        'BMFBOVESPA': _BR_MARKET,
        'US': _US_MARKET,
        'USA': _US_MARKET,
        'AMERICA': _US_MARKET,
        'NASDAQ': 'NASDAQ',
        'NYSE': 'NYSE',
        'AMEX': 'AMEX',
        'OTC': 'OTC',
    }
    # B3 tickers are four letters plus one or two digits, optionally followed by
    # a class letter (``PETR4``, ``HGLG11``, ``CSAN3F``). Used only to break ties
    # when a ticker could resolve on more than one exchange.
    _B3_TICKER_PATTERN = re.compile(r"^[A-Z]{4}\d{1,2}[A-Z]?$")
    # Scanner column -> friendly key used in the returned dicts and in the CSV.
    _QUOTE_FIELDS = (
        ("name", "ticker"),
        ("description", "company"),
        ("close", "price"),
        ("change", "change_percent"),
        ("change_abs", "change_abs"),
        ("volume", "volume"),
        ("average_volume_10d_calc", "avg_volume_10d"),
        ("market_cap_basic", "market_cap"),
        ("currency", "currency"),
        ("exchange", "exchange"),
        ("sector", "sector"),
        ("industry", "industry"),
        ("price_earnings_ttm", "pe_ttm"),
        ("dividends_yield", "dividend_yield"),
        ("Perf.Y", "perf_1y"),
        ("Perf.1M", "perf_1m"),
        ("Volatility.D", "volatility_d"),
    )

    def __init__(self, download_path: str, filename: str = None, quotes_filename: str | None = None):
        """
        Initialize the TradingViewProvider with a download path and optional filename.
        
        Args:
            download_path (str): Directory path where the CSV file will be saved.
            filename (str, optional): Custom filename for the output CSV file.
                                      If not provided, defaults to 'trading_view.csv'.
            quotes_filename (str, optional): Custom filename for the quotes CSV file.
                                      If not provided, defaults to 'trading_view_quotes.csv'.
        """
        self.download_path = download_path
        self.filename = filename if filename else self._DEFAULT_FILENAME
        self.quotes_filename = quotes_filename if quotes_filename else self._DEFAULT_QUOTES_FILENAME

    def _config_step(self):
        Log.log("Start")
        self.HEADER = "STOCK;NAME;DEPARTMENT;IMAGE\n"
        self.lines = []

    def _make_request(self):
        url = self._URL.replace(self._SYMBOL, self.stock)
        response: Response = requests.get(url)
        Log.log(f"Making request for {self.stock}")

        if response.status_code == 200:
            html = response.text
            self.page = BeautifulSoup(html, 'html.parser')
            self.execute_next_step = True
        else:
            Log.log(f"Failed request with status code {response.status_code} when call for {self.stock}")
            self.execute_next_step = False

    def _read_page_and_get_data(self):
        if not self.execute_next_step:
            Log.log("Skip step")
            return

        Log.log(f"Reading page and getting data for {self.stock}")

        img_tag = self.page.select_one('img[class*="logo-"]')
        image = ""
        if img_tag is not None:
            image = img_tag["src"]

        name_tag = self.page.find("h1", class_="apply-overflow-tooltip title-HDE_EEoW")
        name = ""
        if name_tag is not None:
            name = name_tag.get_text(strip=True)

        prefix = "/markets/stocks-brazil/sectorandindustry-sector/"
        department_tag = self.page.select_one(f'a[href^="{prefix}"]')

        if department_tag is None:
            department = ""
        else:
            department = department_tag.get_text(strip=True)

        self.lines.append(f"{self.stock};{name};{department};{image}\n")

    def _transform_data_into_csv(self):
        if not self.lines:
            Log.log("No data to write")
            return

        file_path = f"{self.download_path}/{self.filename}"
        Log.log(f"Writing data to CSV at {file_path}")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(self.HEADER)
            f.writelines(self.lines)

    def run(self, stocks: List[str]):
        """
        Run the scraping process for a list of stock tickers.
        
        This is the main method to execute the scraping process. It iterates through
        the provided list of stock tickers, collects information for each stock,
        and saves the results to a CSV file.
        
        Args:
            stocks (List[str]): A list of stock ticker symbols to collect data for.
                               These should be valid B3/BMFBOVESPA stock symbols.
                                
        Example:
            >>> provider = TradingViewProvider(download_path="./data")
            >>> provider.run(stocks=["PETR4", "VALE3", "ITUB4"])
        """
        self._config_step()
        for stock in stocks:
            self.stock = stock
            self._make_request()
            self._read_page_and_get_data()
        self._transform_data_into_csv()

    # ------------------------------------------------------------------
    # Bulk quotes (TradingView scanner endpoint)
    # ------------------------------------------------------------------

    def _normalize_exchange(self, exchange: str) -> str:
        """
        Map a user supplied exchange hint onto a known mode.

        Args:
            exchange (str): One of ``auto``, ``brazil``/``br``/``b3``,
                ``america``/``us``/``usa``, or an explicit exchange name
                (``BMFBOVESPA``, ``NASDAQ``, ``NYSE``, ``AMEX``, ``OTC``).

        Returns:
            str: The normalized mode. Unknown values fall back to ``auto``.
        """
        mode = (exchange or self._AUTO).strip().upper()
        if mode in self._EXCHANGE_MODES:
            return self._EXCHANGE_MODES[mode]

        Log.log(f"Unknown exchange '{exchange}'. Falling back to '{self._AUTO}'.")
        return self._AUTO

    def _market_for_exchange(self, exchange: str) -> str:
        """Return the scanner market that serves the given exchange."""
        if exchange.upper() == self._BR_EXCHANGE:
            return self._BR_MARKET
        return self._US_MARKET

    def _normalize_ticker(self, ticker: str) -> str:
        """
        Normalize a ticker to the symbol format TradingView expects.

        TradingView writes class shares with a dot (``BRK.B``) while other
        platforms use ``BRK_B`` or ``BRK-B``. B3 tickers never contain those
        characters, so the substitution is safe for both markets.

        Args:
            ticker (str): Raw ticker.

        Returns:
            str: The normalized ticker.
        """
        return ticker.replace("_", ".").replace("-", ".")

    def _quote_candidates(self, ticker: str, mode: str) -> list[tuple[str, str]]:
        """
        Build the (market, symbol) pairs probed for a plain ticker.

        In ``auto`` mode both markets are probed with every known exchange, so
        the ticker's own market decides the match instead of a local guess.

        Args:
            ticker (str): Uppercase ticker without an exchange prefix.
            mode (str): Normalized exchange mode.

        Returns:
            list[tuple[str, str]]: Pairs of (market, qualified symbol).
        """
        if mode == self._BR_MARKET:
            return [(self._BR_MARKET, f"{self._BR_EXCHANGE}:{ticker}")]

        if mode == self._US_MARKET:
            return [(self._US_MARKET, f"{exchange}:{ticker}") for exchange in self._US_EXCHANGES]

        if mode in self._US_EXCHANGES:
            return [(self._US_MARKET, f"{mode}:{ticker}")]

        candidates = [(self._BR_MARKET, f"{self._BR_EXCHANGE}:{ticker}")]
        candidates += [(self._US_MARKET, f"{exchange}:{ticker}") for exchange in self._US_EXCHANGES]
        return candidates

    def _preferred_market(self, ticker: str, mode: str) -> str:
        """Guess the market a ticker belongs to, used only to break ties."""
        if mode == self._BR_MARKET:
            return self._BR_MARKET
        if mode == self._US_MARKET or mode in self._US_EXCHANGES:
            return self._US_MARKET
        if self._B3_TICKER_PATTERN.match(ticker):
            return self._BR_MARKET
        return self._US_MARKET

    def _quote_config_step(self, stocks: list[str], exchange: str = "auto") -> None:
        """
        Prepare the scanner requests for a list of tickers.

        Args:
            stocks (list[str]): Tickers to look up. Both plain tickers
                (``PETR4``, ``AAPL``) and qualified ones (``BMFBOVESPA:PETR4``,
                ``NASDAQ:AAPL``) are accepted.
            exchange (str): Exchange hint, see :meth:`_normalize_exchange`.
        """
        Log.log("Start")
        os.makedirs(self.download_path, exist_ok=True)

        self.quotes: list[dict[str, Any]] = []
        self._quote_payloads: dict[str, Any] = {}
        self._quote_requests: dict[str, list[str]] = {}
        self._quote_preferred_market: dict[str, str] = {}

        mode = self._normalize_exchange(exchange)
        Log.log(f"Exchange mode: {mode}")

        for raw_stock in stocks or []:
            ticker = self._normalize_ticker(str(raw_stock).strip().upper())
            if not ticker:
                continue

            if ":" in ticker:
                exchange_name, _, symbol = ticker.partition(":")
                exchange_name = exchange_name.upper()
                market = self._market_for_exchange(exchange_name)
                candidates = [(market, f"{exchange_name}:{symbol}")]
                bare_ticker = symbol
                preferred_market = market
            else:
                candidates = self._quote_candidates(ticker, mode)
                bare_ticker = ticker
                preferred_market = self._preferred_market(ticker, mode)

            for market, symbol in candidates:
                self._quote_requests.setdefault(market, []).append(symbol)
            self._quote_preferred_market[bare_ticker] = preferred_market

    def _quote_make_request(self) -> None:
        """Fetch the quotes, one request per market."""
        for market, symbols in self._quote_requests.items():
            if not symbols:
                continue

            payload = {
                "symbols": {"tickers": symbols, "query": {"types": []}},
                "columns": [column for column, _ in self._QUOTE_FIELDS],
            }
            url = self._SCANNER_URL.format(market=market)
            Log.log(f"Making request for {len(symbols)} symbols on market '{market}'")

            try:
                response: Response = requests.post(
                    url,
                    json=payload,
                    headers=self._SCANNER_HEADERS,
                    timeout=self._REQUEST_TIMEOUT,
                )
                response.raise_for_status()
                self._quote_payloads[market] = response.json()
            except (requests.RequestException, ValueError) as e:
                Log.log_error(f"Error when fetching quotes for market '{market}'", e)

    def _quote_read_page_and_get_data(self) -> None:
        """Turn the scanner payloads into one dict per ticker."""
        rows: dict[str, dict[str, Any]] = {}

        for market, payload in self._quote_payloads.items():
            for item in payload.get("data") or []:
                symbol = item.get("s")
                if not symbol:
                    continue

                values = item.get("d") or []
                row = {key: value for (_, key), value in zip(self._QUOTE_FIELDS, values)}
                row["symbol"] = symbol
                row["market"] = market

                ticker = row.get("ticker") or symbol.split(":", 1)[-1]
                current = rows.get(ticker)
                if current is not None and not self._prefer_row(row, current):
                    continue
                rows[ticker] = row

        self.quotes = list(rows.values())
        Log.log(f"Loaded {len(self.quotes)} quotes")
        self._log_missing_tickers(rows.keys())

    def _prefer_row(self, candidate: dict[str, Any], current: dict[str, Any]) -> bool:
        """Decide which row wins when a ticker resolves on several exchanges."""
        preferred = self._quote_preferred_market.get(candidate.get("ticker", ""))
        if preferred is None:
            return True
        if candidate.get("market") == preferred:
            return True
        return current.get("market") != preferred

    def _log_missing_tickers(self, resolved) -> None:
        """Warn about tickers that could not be resolved by the scanner."""
        missing = sorted(ticker for ticker in self._quote_preferred_market if ticker not in resolved)
        if missing:
            Log.log(f"Could not resolve {len(missing)} ticker(s): {', '.join(missing)}")
    def _quote_transform_data_into_csv(self, filename: str | None = None) -> None:
        """Write the collected quotes to a CSV file."""
        if not self.quotes:
            Log.log("No data to write")
            return

        target = filename if filename else self.quotes_filename
        file_path = f"{self.download_path}/{target}"
        Log.log(f"Writing data to CSV at {file_path}")

        header = [key for _, key in self._QUOTE_FIELDS] + ["symbol", "market"]
        with open(file_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow([key.upper() for key in header])
            for row in self.quotes:
                writer.writerow([row.get(key, "") for key in header])

    def run_quotes(self, stocks: list[str], exchange: str = "auto", filename: str | None = None) -> list[dict[str, Any]]:
        """
        Fetch quotes for a list of tickers from Brazil (B3) and/or the United States.

        Unlike :meth:`run`, this uses the TradingView scanner endpoint, which
        answers the whole list in a single request per market instead of one
        request per ticker. No API key or account is required.

        Tickers may be plain (``PETR4``, ``AAPL``) or qualified
        (``BMFBOVESPA:PETR4``, ``NASDAQ:AAPL``). Plain tickers are resolved
        against the Brazilian and the US exchanges, so a single call can mix
        both markets.

        Args:
            stocks (List[str]): Tickers to look up.
            exchange (str, optional): Exchange hint. ``auto`` (default) probes
                B3 and the US exchanges, ``brazil``/``br``/``b3`` restricts the
                lookup to B3, ``america``/``us``/``usa`` to the US exchanges, and
                ``BMFBOVESPA``/``NASDAQ``/``NYSE``/``AMEX``/``OTC`` to a single
                exchange.
            filename (str, optional): Custom filename for the output CSV file.
                Defaults to the provider's ``quotes_filename``.

        Returns:
            List[dict]: One dict per resolved ticker, with the keys ``ticker``,
            ``company``, ``price``, ``change_percent``, ``change_abs``,
            ``volume``, ``avg_volume_10d``, ``market_cap``, ``currency``,
            ``exchange``, ``sector``, ``industry``, ``pe_ttm``,
            ``dividend_yield``, ``perf_1y``, ``perf_1m``, ``volatility_d``,
            ``symbol`` and ``market``.

        Example:
            >>> provider = TradingViewProvider(download_path="./data")
            >>> provider.run_quotes(stocks=["PETR4", "VALE3", "AAPL", "JPM"])
            [{'ticker': 'PETR4', 'price': 45.19, ...}, ...]
        """
        self._quote_config_step(stocks, exchange)
        self._quote_make_request()
        self._quote_read_page_and_get_data()
        self._quote_transform_data_into_csv(filename)
        return self.quotes
