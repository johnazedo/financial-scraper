# Status Invest Provider

The `StatusInvestProvider` class scrapes stock data from the Status Invest website, focusing on their advanced stock search functionality.

## Overview

The Status Invest provider uses Selenium WebDriver to automate the process of filtering, searching, and downloading stock data from the Status Invest advanced search page. It supports filtering stocks by specific sectors and handles the download of CSV data files.

## Class Definition

```python
class StatusInvestProvider:
    # Sector enumeration and constants
    # ...
    
    def __init__(self, download_path: str):
        # Initialize with download path
        
    def config_step(self):
        # Configure Selenium WebDriver
    
    def make_request(self):
        # Navigate to website and initiate download
    
    def read_page_and_get_data(self):
        # Skip this step (handled by direct CSV download)
        
    def transform_data_into_csv(self):
        # Skip this step (file already in CSV format)
        
    def run(self, sector: Sector = Sector.UNDEFINED):
        # Execute the scraping process
```

## Available Sectors

The provider defines an inner `Sector` enumeration with the following options:

| Enum Value | Website Value | Description |
|------------|---------------|-------------|
| `CYCLIC_CONSUMPTION` | "cyclic-consumption" | Consumo Cíclico |
| `NON_CYCLIC_CONSUMPTION` | "non-cyclic-consumption" | Consumo não Cíclico |
| `PUBLIC_UTILITIES` | "public-utilities" | Utilidade Pública |
| `INDUSTRIAL_GOODS` | "industrial-goods" | Bens Industriais |
| `BASIC_MATERIALS` | "basic-materials" | Materiais Básicos |
| `FINANCIAL_AND_OTHERS` | "financial-and-others" | Financeiro e Outros |
| `INFORMATION_TECHNOLOGY` | "information-technology" | Tecnologia da Informação |
| `HEALTHCARE` | "healthcare" | Saúde |
| `OIL_GAS_AND_BIOFUELS` | "oil-gas-and-biofuels" | Petróleo, Gás e Biocombustíveis |
| `COMMUNICATIONS` | "communications" | Comunicações |
| `UNDEFINED` | "undefined" | Indefinido (default) |

## Usage

```python
from financial_scraper import StatusInvestProvider

# Initialize with download path
provider = StatusInvestProvider(download_path="/path/to/downloads")

# Download all stocks
provider.run()

# Download stocks from specific sector
provider.run(sector=StatusInvestProvider.Sector.FINANCIAL_AND_OTHERS)
```

## Output

The provider downloads a CSV file with stock data from Status Invest. Depending on the selected sector, the file will be named:

- `statusinvest-busca-avancada.csv` for all stocks (default)
- `statusinvest-busca-avancada-{sector-name}.csv` when a specific sector is selected (e.g., `statusinvest-busca-avancada-financial-and-others.csv`)

## Implementation Details

The provider:

1. Configures a headless Chrome browser using Selenium
2. Navigates to the Status Invest advanced search page
3. If a sector is specified, selects it from the dropdown menu
4. Clicks the search button to filter stocks
5. Clicks the download button to download the CSV file
6. Renames the file if a specific sector was selected
7. Closes the browser

Error handling is implemented to ensure proper browser cleanup and to log any issues during the process.