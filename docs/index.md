# Financial Scraper

A Python-based web scraping tool for collecting and analyzing financial data from multiple sources. This project helps you gather information about funds, stocks, and their respective profits from various financial websites.

## Features

- Scrapes financial data from multiple sources:
  - FundsExplorer
  - StatusInvest
  - DadosDeMercado
  - TrandingView
  - Fundamentus
- Collects information about:
  - Stocks
  - REITs (Brazilian FIIs) dividends
  - Stock details (name, sector, logo)
- Automatically saves data in organized CSV format
- Modular architecture for easy extension

> **Disclaimer**: This tool relies on web scraping techniques to collect data from financial websites. If any of the algorithms stop working, it may be due to changes in the structure or content of the websites being scraped. Web scraping is inherently fragile and dependent on website stability. Regular maintenance may be required to adapt to website changes.

## Project Overview

Financial Scraper is designed to simplify the process of collecting financial data from various Brazilian investment platforms. The tool provides a unified interface to scrape and organize data that would otherwise require manual collection across multiple websites.

## Quick Start

```bash
# Install the package
pip install financial-scraper

# Or using Poetry
poetry install financial_scapper
```

For detailed installation and usage instructions, see the [Getting Started](getting-started/installation.md) guide.
