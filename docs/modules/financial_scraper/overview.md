# Financial Scraper Modules

This section provides detailed documentation for the Financial Scraper modules and their components.

## Core Modules

The project is structured around several key modules:

### financial_scraper

This is the main package that contains the core functionality:

- **Providers**: Web scraping implementations for different financial websites
- **Config**: Configuration utilities for Selenium and other tools

## Module Structure

```
financial_scraper/
├── __init__.py              # Package exports
├── config/                  # Configuration utilities
│   ├── __init__.py
│   ├── selenium.py          # Selenium WebDriver configuration
│   └── utils.py             # Utility functions and logging
└── providers/               # Web scraping providers
    ├── __init__.py
    ├── fundamentus.py       # Fundamentus data provider
    ├── investor_ten.py      # Investidor10 data provider
    ├── status_invest.py     # Status Invest data provider
    └── trading_view.py      # TradingView data provider
```

## Provider Modules

### Status Invest Provider

The `StatusInvestProvider` class in `status_invest.py` enables scraping stock data from the Status Invest website:

- Supports filtering stocks by sector (e.g., Financial, Healthcare, Technology)
- Downloads data in CSV format
- Uses Selenium for browser automation
- Handles sector-specific file naming

### Fundamentus Provider

The `FundamentusProvider` class in `fundamentus.py` scrapes stock data from the Fundamentus website:

- Uses Beautiful Soup for HTML parsing
- Direct HTTP requests with the requests library
- Converts HTML tables to pandas DataFrames
- Saves data in CSV format with date-stamped filenames

### InvestorTen Provider

The `InvestorTenProvider` class in `investor_ten.py` scrapes REIT (FII) dividend data from the Investidor10 website:

- Retrieves dividend information for Brazilian REITs for a specified year
- Collects data month by month across the entire year
- Uses Beautiful Soup for HTML parsing
- Saves data in a structured CSV format with customizable filename

### TradingView Provider

The `TradingViewProvider` class in `trading_view.py` scrapes stock information from the TradingView website:

- Retrieves basic stock information from the Brazilian stock market (B3/BMFBOVESPA)
- Collects company names, sectors, and logo image URLs
- Uses Beautiful Soup for HTML parsing
- Processes multiple stock tickers in a single run
- Saves data in a CSV format with customizable filename

## Configuration Modules

### Selenium Config

The `selenium.py` module provides configuration for the Selenium WebDriver:

- Headless browser configuration
- Download path configuration
- Browser preferences and security settings

### Utilities

The `utils.py` module contains utility functions:

- `Log` class for structured logging
- `check_if_file_was_downloaded` function to verify file downloads

## Module Architecture

The project follows a modular architecture where providers implement the core scraping functionality:

```
+---------------+     +---------------+
|   Providers   |---->|    Config     |
+---------------+     +---------------+
       |
       v
+---------------+
|  CSV Output   |
+---------------+
```

For detailed API documentation of each module, explore the corresponding section in the navigation.