# Status Invest Provider

The `StatusInvestProvider` class scrapes stock data from the Status Invest website, focusing on their advanced stock search functionality.

## Overview

The Status Invest provider uses Selenium WebDriver to automate the process of filtering, searching, and downloading stock data from the Status Invest advanced search page. It supports filtering stocks by specific sectors and handles the download of CSV data files.

The provider allows you to:
- Filter stocks by specific market sectors
- Choose between headless or visible browser operation
- Customize the output filename for the downloaded data

## Class Definition

```python
class StatusInvestProvider:
    """
    Provider for scraping stock data from Status Invest website.
    """
    
    class Sector(Enum):
        """
        Enumeration of stock market sectors available on Status Invest.
        """
        # Sector enumeration values...
    
    def __init__(self, download_path: str, filename: str = None, show_browser: bool = False):
        """
        Initialize the StatusInvestProvider with download path and options.
        """
        
    def run(self, sector: Sector = Sector.UNDEFINED):
        """Execute the complete scraping process to fetch stock data"""
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

### Basic Usage

```python
from financial_scraper import StatusInvestProvider
import os

# Set the download path
download_path = os.path.dirname(os.path.abspath(__file__))

# Initialize the provider
provider = StatusInvestProvider(
    download_path=download_path,
)

# Download all stocks (no sector filter)
provider.run()
```

### With Sector Filter

```python
from financial_scraper import StatusInvestProvider
import os

download_path = os.path.dirname(os.path.abspath(__file__))

provider = StatusInvestProvider(
    download_path=download_path,
)

# Download stocks from a specific sector
provider.run(sector=StatusInvestProvider.Sector.FINANCIAL_AND_OTHERS)
```

### Custom Filename

```python
from financial_scraper import StatusInvestProvider
import os

download_path = os.path.dirname(os.path.abspath(__file__))

provider = StatusInvestProvider(
    download_path=download_path,
    filename="financial_stocks.csv"
)

provider.run(sector=StatusInvestProvider.Sector.FINANCIAL_AND_OTHERS)
```

### Visible Browser Mode

```python
from financial_scraper import StatusInvestProvider
import os

download_path = os.path.dirname(os.path.abspath(__file__))

# Initialize with visible browser (useful for debugging)
provider = StatusInvestProvider(
    download_path=download_path,
    show_browser=True
)

provider.run()
```

## Output Format

The provider downloads a CSV file containing stock data from Status Invest. The file naming depends on your configuration:

1. **When using a custom filename** (specified in constructor):
   - The file will be saved with your specified name (e.g., `financial_stocks.csv`)

2. **When using the default filename** (no custom filename specified):
   - For all stocks (no sector filter): `statusinvest.csv` 
   - For a specific sector: `statusinvest-{sector-name}.csv` (e.g., `statusinvest-financial-and-others.csv`)

The CSV file contains detailed information about each stock, including:
- Ticker symbols
- Company names
- Current prices
- Financial indicators (P/E, P/VP, etc.)
- Dividend information
- And other metrics provided by Status Invest

## Implementation Details

The provider follows this workflow:

1. Configures a Chrome browser using Selenium (headless by default, visible if `show_browser=True`)
2. Navigates to the Status Invest advanced search page
3. If a sector is specified, selects it from the dropdown menu
4. Clicks the search button to filter stocks
5. Clicks the download button to download the CSV file
6. Waits for the download to complete with a timeout of 30 seconds
7. Renames the file if a custom filename was provided or a specific sector was selected
8. Closes the browser

Error handling is implemented to ensure proper browser cleanup and to log any issues during the process.

## Parameter Details

### Constructor Parameters

- `download_path` (str): Directory path where downloaded files will be saved.
- `filename` (str, optional): Custom filename for the downloaded CSV file. If None, a default filename based on sector will be used.
- `show_browser` (bool, optional): Whether to show the browser window during execution. Defaults to False (headless mode).

### Run Method Parameters

- `sector` (Sector, optional): Specific sector to filter stocks by. Defaults to `Sector.UNDEFINED` (no sector filter).

## Notes

- The provider uses Selenium WebDriver, so a compatible Chrome/Chromium installation is required.
- The headless mode is more efficient but doesn't allow you to see the automation process.
- For debugging purposes, you can set `show_browser=True` to see the browser automation in action.
- If you encounter issues with downloads, make sure your download path exists and is writable.
- The provider automatically cleans up resources even if errors occur during the process.
