# TradingView Provider

The `TradingViewProvider` allows you to scrape basic stock information from the TradingView website for Brazilian stocks.

## Overview

This provider collects information about stocks from the Brazilian stock market (B3/BMFBOVESPA), including:

- Stock ticker symbol
- Full company name
- Department/sector
- Logo image URL

The data is collected from the TradingView website and saved to a CSV file for further analysis.

## Usage

### Basic Usage

```python
from financial_scraper import TradingViewProvider
import os

# Set the download path
download_path = os.path.dirname(os.path.abspath(__file__))

# Initialize the provider
provider = TradingViewProvider(
    download_path=download_path,
)

# Fetch data for specific stocks
provider.run(stocks=["PETR4", "VALE3", "ITUB4"])
```

### Custom Filename

You can specify a custom filename for the output CSV:

```python
from financial_scraper import TradingViewProvider
import os

download_path = os.path.dirname(os.path.abspath(__file__))

# Initialize with custom filename
provider = TradingViewProvider(
    download_path=download_path,
    filename="brazilian_stocks_info.csv"
)

provider.run(stocks=["PETR4", "VALE3", "ITUB4"])
```

## Output Format

The provider generates a CSV file with the following columns:

| STOCK | NAME | DEPARTMENT | IMAGE |
|-------|------|-----------|-------|
| PETR4 | Petrobras PN | Oil & Gas | https://s3-symbol-logo.tradingview.com/petrobras--big.svg |
| VALE3 | Vale | Basic Materials | https://s3-symbol-logo.tradingview.com/vale--big.svg |
| ITUB4 | Itaú Unibanco PN | Financial Services | https://s3-symbol-logo.tradingview.com/itau-unibanco--big.svg |

## How It Works

The TradingViewProvider uses the following process to collect data:

1. For each stock ticker in the provided list:
   - Constructs a URL to the stock's page on TradingView
   - Makes an HTTP request to retrieve the page content
   - Parses the HTML to extract the company name, department/sector, and logo image URL

2. After collecting data for all stocks:
   - Combines the data into a CSV file with semicolon (`;`) as the delimiter
   - Saves the file to the specified download path

## Bulk Quotes (Brazil and United States)

`run_quotes()` is a second, independent entry point that fetches **quotes** for a
list of tickers from **Brazil (B3) and/or the United States**.

It uses the TradingView scanner endpoint instead of the HTML pages, so:

- the whole list is resolved in **one request per market** (not one per ticker);
- the price, change, volume and fundamentals come back in a single payload;
- **no API key, account or login is required**;
- the parsed rows are **returned in memory** as well as written to a CSV file.

### Usage

```python
from financial_scraper import TradingViewProvider

provider = TradingViewProvider(download_path="./data")

# Mixed B3 and US tickers, resolved automatically
quotes = provider.run_quotes(stocks=["PETR4", "VALE3", "AAPL", "JPM", "MSFT"])

for quote in quotes:
    print(quote["ticker"], quote["price"], quote["change_percent"], quote["currency"])
    # PETR4 45.19 -0.37477954144621184 BRL
    # AAPL 350.69 2.4301194614014054 USD
```

### Class Definition

```python
class TradingViewProvider:
    def __init__(self, download_path: str, filename: str = None, quotes_filename: str = None):
        """..."""

    def run(self, stocks: List[str]) -> None:
        """Scrape name, sector and logo for each ticker (B3)."""

    def run_quotes(self, stocks: List[str], exchange: str = "auto",
                   filename: str = None) -> List[dict]:
        """Fetch quotes for B3 and/or US tickers. Returns one dict per ticker."""
```

### Exchange resolution

Plain tickers (`PETR4`, `AAPL`) are resolved against B3 and the US exchanges, so
a single call may mix both markets. Tickers may also be qualified explicitly
(`BMFBOVESPA:PETR4`, `NASDAQ:AAPL`), in which case they are sent untouched.

The `exchange` argument narrows the lookup:

| Value | Meaning |
|-------|---------|
| `auto` (default) | Probe B3 and the US exchanges |
| `brazil` / `br` / `b3` / `BMFBOVESPA` | Only B3 |
| `america` / `us` / `usa` | Only the US exchanges (NASDAQ, NYSE, AMEX, OTC) |
| `NASDAQ`, `NYSE`, `AMEX`, `OTC` | A single exchange |

Class-share tickers are normalized: `BRK_B` and `BRK-B` both resolve to
TradingView's `BRK.B`.

### Output Format

The quotes are written to `trading_view_quotes.csv` (override with the
`quotes_filename` constructor argument or the `filename` argument of
`run_quotes`) with the semicolon (`;`) delimiter and these columns:

| TICKER | COMPANY | PRICE | CHANGE_PERCENT | CHANGE_ABS | VOLUME | AVG_VOLUME_10D | MARKET_CAP | CURRENCY | EXCHANGE | SECTOR | INDUSTRY | PE_TTM | DIVIDEND_YIELD | PERF_1Y | PERF_1M | VOLATILITY_D | SYMBOL | MARKET |

The same data is returned as a list of dictionaries with the lower-cased keys
(`ticker`, `company`, `price`, `change_percent`, `change_abs`, `volume`,
`avg_volume_10d`, `market_cap`, `currency`, `exchange`, `sector`, `industry`,
`pe_ttm`, `dividend_yield`, `perf_1y`, `perf_1m`, `volatility_d`, `symbol`,
`market`).

Tickers that cannot be resolved are skipped and logged.

### Notes

- The scanner endpoint is an **undocumented internal endpoint** of the TradingView
  website. It is free and needs no key, but it carries no SLA and may change
  without notice.
- Prices are quoted in the listing currency: `BRL` for B3, `USD` for the US.
- `run()` and `run_quotes()` are independent: use `run()` for logos/sectors and
  `run_quotes()` for prices.

## Notes

- The provider relies on the TradingView website structure for scraping data.
- Stock symbols should be valid B3/BMFBOVESPA tickers (e.g., "PETR4", "VALE3").
- For some stocks, department information might not be available and will be empty.
- Image URLs point to the company logos hosted on TradingView's servers.
- If a stock ticker is invalid or not found, it will be skipped in the output.

## Related Resources

- [TradingView Brazil](https://br.tradingview.com/)
- [B3 Stock Exchange](http://www.b3.com.br/)
