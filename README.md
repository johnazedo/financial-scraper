# Financial Scraper 

A Python-based web scraping tool for collecting and analyzing financial data from multiple sources. This project helps you gather information about stocks from various financial websites.

## Features

- Scrapes financial data from multiple sources:
  - FundsExplorer
  - StatusInvest
- Collects information about:
  - Stocks
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
│       └── status_invest.py    # StatusInvest scraper
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

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.