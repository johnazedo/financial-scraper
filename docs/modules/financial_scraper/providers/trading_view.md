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

## Notes

- The provider relies on the TradingView website structure for scraping data.
- Stock symbols should be valid B3/BMFBOVESPA tickers (e.g., "PETR4", "VALE3").
- For some stocks, department information might not be available and will be empty.
- Image URLs point to the company logos hosted on TradingView's servers.
- If a stock ticker is invalid or not found, it will be skipped in the output.

## Related Resources

- [TradingView Brazil](https://br.tradingview.com/)
- [B3 Stock Exchange](http://www.b3.com.br/)
