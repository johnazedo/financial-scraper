# Web Scraping Financial

A Python-based web scraping tool for collecting and analyzing financial data from multiple sources. This project helps you gather information about funds, stocks, and their respective profits from various financial websites.

## Features

- Scrapes financial data from multiple sources:
  - FundsExplorer
  - StatusInvest
  - TradingView
  - Investidor 10
  - Dados de Mercado
- Collects information about:
  - Funds
  - Stocks
  - Funds profits
- Automatically saves data in organized CSV format
- Modular architecture for easy extension

## Prerequisites

- Python 3.10 or higher
- Poetry (for dependency management)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/johnazedo/web-scraping-financial.git
cd web-scraping-financial
```

2. Install dependencies using Poetry:
```bash
poetry install
```

## Usage

The project provides several commands for different data collection tasks:

### Collect FIIs Data
Get list of FIIs from funds explorer site.

```bash
poetry run get_funds
```

### Collect Stock Data
Get stocks financial data from status invest site.

```bash
poetry run get_stocks
```

### Generate Final CSV
Generate a CSV with combine data between the follow sorces

- StatusInvest Site: Financial data;
- TradingView Site: Stocks department and image;
- "Dados de Mercado" Site: Nome.

```bash
poetry run generate_final_csv
```

### Get Funds Profits
Get data from "Investidor 10" site.

```bash
poetry run get_funds_profits
```

### Get Market Data
Get stocks name from "Dados de Mercado" site.

```bash
poetry run get_market_data
```

### Get TradingView Data
Get stocks department and image from TradingView site.
This script uses data from get_stock script

```bash
poetry run get_trading_view_data
```

## Project Structure

```
├── LICENSE
├── poetry.lock
├── pyproject.toml
├── README.md
├── data/               # Organized CSV data files
│   ├── funds/         # Fund-related data
│   ├── funds_profits/ # Fund profit information
│   └── stocks/        # Stock-related data
├── downloads/         # Raw downloaded data
│   ├── README.md
├── main/             # Core application logic
│   ├── __init__.py
│   ├── core.py      # Core functionality
│   ├── main.py      # Entry point with command definitions
│   └── settings.py  # Application settings and configuration
└── services/         # Service integrations for different data sources
    ├── __init__.py
    ├── funds_explorer.py   # FundsExplorer scraping service
    ├── investor_ten.py     # Investidor 10 scraping service
    ├── market_data.py      # Market data service
    ├── service.py          # Base service class
    ├── status_invest.py    # StatusInvest scraping service
    └── trading_view.py     # TradingView scraping service
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