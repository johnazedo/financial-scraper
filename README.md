# Financial Scraper 

A Python-based web scraping tool for collecting and analyzing financial data from multiple sources. This project helps you gather information about stocks from various financial websites.

## Features

- Scrapes financial data from multiple sources:
  - FundsExplorer
  - StatusInvest
  - Investidor10
  - TradingView
  - DadosDeMercado
- Collects information about:
  - Stocks
  - REITs (Brazilian FIIs) dividends
  - REITs (Brazilian FIIs) rankings and financial metrics
  - Stock details from TradingView (name, sector, logo)
  - Complete list of stocks from B3 (Brazilian stock exchange)
- Automatically saves data in organized CSV format
- Modular architecture for easy extension

> **Disclaimer**: This tool relies on web scraping techniques to collect data from financial websites. If any of the algorithms stop working, it may be due to changes in the structure or content of the websites being scraped. Web scraping is inherently fragile and dependent on website stability. Regular maintenance may be required to adapt to website changes.

## Prerequisites

- Python 3.10 or higher
- Poetry (for dependency management)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/johnazedo/financial-scraper.git
cd financial-scraper
```

2. Install dependencies using Poetry:
```bash
poetry install
```

## Usage


#### Collect Stock Data
Get stocks financial data from status invest site or fundamentus site

```bash
poetry run example_status_invest
```

```bash
poetry run example_fundamentus
```

```bash
poetry run example_investor_ten
```

```bash
poetry run example_trading_view
```

```bash
poetry run example_market_data
```

```bash
poetry run example_funds_explorer
```

### Python API

You can also use Financial Scraper as a Python library in your own code:

#### Using the Status Invest Provider

```python
from financial_scraper import StatusInvestProvider
import os

# Set the download path
download_path = os.path.dirname(os.path.abspath(__file__))

# Initialize the provider
provider = StatusInvestProvider(
    download_path=download_path,
)

# Fetch all stocks
provider.run()

provider = StatusInvestProvider(
    download_path=download_path,
    filename="financial_stocks.csv"
)

# Fetch stocks from a specific sector
provider.run(sector=StatusInvestProvider.Sector.FINANCIAL_AND_OTHERS)
```

#### Using the Fundamentus Provider

```python
from financial_scraper import FundamentusProvider
import os

# Set the download path
download_path = os.path.dirname(os.path.abspath(__file__))

# Initialize the provider
provider = FundamentusProvider(
    download_path=download_path,
)

# Fetch and save data
provider.run()
```

#### Using the InvestorTen Provider

```python
from financial_scraper import InvestorTenProvider
import os

# Set the download path
download_path = os.path.dirname(os.path.abspath(__file__))

# Initialize the provider
provider = InvestorTenProvider(
    download_path=download_path,
)

# Fetch REIT dividend data for a specific year
provider.run(year="2023")

# You can also specify a custom filename for the output
provider = InvestorTenProvider(
    download_path=download_path,
    filename="fiis-dividends-2023.csv"
)
provider.run(year="2023")
```

#### Using the TradingView Provider

```python
from financial_scraper import TradingViewProvider
import os

# Set the download path
download_path = os.path.dirname(os.path.abspath(__file__))

# Initialize the provider
provider = TradingViewProvider(
    download_path=download_path,
)

# Fetch stock data for specific tickers
provider.run(stocks=["PETR4", "VALE3", "ITUB4", "BBDC4"])

# You can also specify a custom filename for the output
provider = TradingViewProvider(
    download_path=download_path,
    filename="brazilian_stocks_info.csv"
)
provider.run(stocks=["PETR4", "VALE3", "ITUB4", "BBDC4"])
```

#### Using the MarketData Provider

```python
from financial_scraper import MarketDataProvider
import os

# Set the download path
download_path = os.path.dirname(os.path.abspath(__file__))

# Initialize the provider
provider = MarketDataProvider(
    download_path=download_path,
)

# Download the complete list of B3 stocks
provider.run()

# You can also specify a custom filename for the output
provider = MarketDataProvider(
    download_path=download_path,
    filename="b3_stocks_list.csv",
    show_browser=True  # Set to True to see the browser during execution
)
provider.run()
```

#### Using the FundsExplorer Provider

```python
from financial_scraper import FundsExplorerProvider
import os

# Set the download path
download_path = os.path.dirname(os.path.abspath(__file__))

# Initialize the provider
provider = FundsExplorerProvider(
    download_path=download_path,
)

# Fetch FII ranking data
provider.run()

# You can also specify a custom filename and wait time
provider = FundsExplorerProvider(
    download_path=download_path,
    filename="fiis_ranking.csv",
    show_browser=True,  # Set to True to see the browser during execution
    wait_time=10  # Increase wait time if the page loads slowly
)
provider.run()
```


## Project Structure

```
├── LICENSE
├── poetry.lock
├── pyproject.toml
├── README.md
├── CONTRIBUTING.md
├── mkdocs.yml
├── docs/               # Documentation files
│   ├── index.md        # Main documentation page
│   ├── examples.md     # Usage examples
│   ├── getting-started/# Installation and basic usage
│   └── modules/        # Module-specific documentation
├── examples/           # Example usage scripts
│   └── usage.py        # Example implementation
├── financial_scraper/  # Core package
│   ├── __init__.py     # Package exports
│   ├── config/         # Configuration utilities
│   │   ├── __init__.py
│   │   ├── selenium.py # Selenium configuration
│   │   └── utils.py    # Utility functions and logging
│   └── providers/      # Data providers
│       ├── __init__.py
│       ├── fundamentus.py      # Fundamentus scraper
│       ├── funds_explorer.py   # FundsExplorer scraper
│       ├── investor_ten.py     # Investidor10 scraper
│       ├── market_data.py      # DadosDeMercado scraper
│       ├── status_invest.py    # StatusInvest scraper
│       └── trading_view.py     # TradingView scraper
```

## Dependencies

- beautifulsoup4 - Web scraping and parsing
- requests - HTTP requests
- selenium - Web browser automation
- pandas - Data manipulation and analysis

## Author

- João Pedro Limão (jplimao077@gmail.com)

## License

This project is licensed under the terms of the LICENSE file included in the repository.

## Documentation

The documentation for this project, including code comments and provider-specific guides, was enhanced using AI assistance. The AI helped to create comprehensive docstrings, usage examples, and module explanations to make the codebase more accessible to contributors and users.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
