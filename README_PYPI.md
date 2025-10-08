# financial-scraper

A Python-based web scraping tool for collecting and analyzing financial data from multiple sources. This project helps you gather information about stocks from various Brazilian financial websites.

## Installation

```bash
pip install financial-scraper
```

Or with Poetry:

```bash
poetry add financial-scraper
```

## Usage

### Python API

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

# Fetch stocks from a specific sector
provider.run(sector=StatusInvestProvider.Sector.FINANCIAL_AND_OTHERS)
```

### Available Providers

- `StatusInvestProvider`: Scrapes stock data from Status Invest
- `FundamentusProvider`: Scrapes stock data from Fundamentus

## Disclaimer

This tool relies on web scraping techniques to collect data from financial websites. If any of the algorithms stop working, it may be due to changes in the structure or content of the websites being scraped. Web scraping is inherently fragile and dependent on website stability. Regular maintenance may be required to adapt to website changes.

## Documentation

For full documentation, visit the [GitHub repository](https://github.com/johnazedo/financial-scraper).

## License

This project is licensed under the MIT License - see the LICENSE file for details.