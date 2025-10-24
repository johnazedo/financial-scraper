# FundsExplorer Provider

The `FundsExplorerProvider` allows you to scrape comprehensive ranking data for Brazilian REITs (FIIs) from the FundsExplorer website.

## Overview

This provider retrieves detailed information about Brazilian Real Estate Investment Trusts (FIIs) from the FundsExplorer ranking page. The data includes:

- FII ticker symbols
- Current prices
- Dividend yields (DY)
- Price-to-Book Value ratios (P/VP)
- Liquidity metrics
- Daily variation
- Net equity
- Last dividend amounts
- And other financial indicators

The data is collected from the FundsExplorer website and saved to a CSV file for further analysis.

## Usage

### Basic Usage

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
```

### Custom Filename

You can specify a custom filename for the output CSV:

```python
from financial_scraper import FundsExplorerProvider
import os

download_path = os.path.dirname(os.path.abspath(__file__))

# Initialize with custom filename
provider = FundsExplorerProvider(
    download_path=download_path,
    filename="fiis_ranking.csv"
)

provider.run()
```

### Visible Browser Mode

By default, the browser runs in headless mode (invisible). If you want to see the browser during execution (useful for debugging):

```python
from financial_scraper import FundsExplorerProvider
import os

download_path = os.path.dirname(os.path.abspath(__file__))

# Initialize with visible browser
provider = FundsExplorerProvider(
    download_path=download_path,
    show_browser=True
)

provider.run()
```

### Custom Wait Time

If the page loads slowly or you're experiencing issues, you can increase the wait time:

```python
from financial_scraper import FundsExplorerProvider
import os

download_path = os.path.dirname(os.path.abspath(__file__))

# Initialize with custom wait time (in seconds)
provider = FundsExplorerProvider(
    download_path=download_path,
    wait_time=10  # Wait 10 seconds for page to load
)

provider.run()
```

### Complete Example with All Options

```python
from financial_scraper import FundsExplorerProvider
import os

download_path = os.path.dirname(os.path.abspath(__file__))

# Initialize with all options
provider = FundsExplorerProvider(
    download_path=download_path,
    filename="fiis_ranking_2025.csv",
    show_browser=True,
    wait_time=8
)

provider.run()
```

## Output Format

The provider generates a CSV file with comprehensive FII data. The file naming depends on your configuration:

1. **When using a custom filename** (specified in constructor):
   - The file will be saved with your specified name (e.g., `fiis_ranking.csv`)

2. **When using the default filename** (no custom filename specified):
   - The file will be named `funds-{date}.csv` (e.g., `funds-24-10-2025.csv`)

The CSV file contains multiple columns with detailed information about each REIT, including financial indicators, prices, yields, and performance metrics as provided by FundsExplorer.

## How It Works

The FundsExplorerProvider uses the following process to collect data:

1. **Configuration**: Sets up a Chrome browser using Selenium with specified options
2. **Navigation**: Opens the FundsExplorer ranking page
3. **Wait**: Waits for the specified time to ensure the page fully loads (including dynamic content)
4. **Extraction**: Parses the HTML to find the ranking table and extracts all rows and columns
5. **Processing**: Organizes the data into a structured format
6. **Export**: Saves the data to a CSV file with proper headers

## Notes

- The provider uses Selenium WebDriver, so a compatible Chrome/Chromium installation is required.
- The headless mode is more efficient but doesn't allow you to see the automation process.
- For debugging purposes, you can set `show_browser=True` to see the browser automation in action.
- The default wait time is 5 seconds, which is usually sufficient. Increase it if you experience issues with incomplete data.
- Make sure your download path exists and is writable before running the provider.
- The provider automatically cleans up resources (closes the browser) even if errors occur during the process.
- Internet connection speed and website responsiveness may affect scraping time.

## Related Resources

- [FundsExplorer](https://www.fundsexplorer.com.br/ranking)
- [B3 - Brazil Stock Exchange](http://www.b3.com.br/)