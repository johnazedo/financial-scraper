# MarketData Provider

The `MarketDataProvider` allows you to download a comprehensive list of stocks from B3 (Brazilian stock exchange) using the DadosDeMercado website.

## Overview

This provider automates the process of downloading the complete list of stocks available on the Brazilian stock exchange. The data includes:

- Stock tickers
- Company names
- Sectors
- Other relevant information provided by DadosDeMercado

The provider uses Selenium to interact with the website, click on the download button, and save the CSV file to a specified location.

## Usage

### Basic Usage

```python
from financial_scraper import MarketDataProvider
import os

# Set the download path
download_path = os.path.dirname(os.path.abspath(__file__))

# Initialize the provider
provider = MarketDataProvider(
    download_path=download_path,
)

# Download the complete list of stocks
provider.run()
```

### Custom Filename

You can specify a custom filename for the downloaded CSV:

```python
from financial_scraper import MarketDataProvider
import os

download_path = os.path.dirname(os.path.abspath(__file__))

# Initialize with custom filename
provider = MarketDataProvider(
    download_path=download_path,
    filename="b3_stocks_list.csv"
)

provider.run()
```

### Visible Browser

By default, the browser runs in headless mode (invisible). If you want to see the browser during execution (useful for debugging):

```python
from financial_scraper import MarketDataProvider
import os

download_path = os.path.dirname(os.path.abspath(__file__))

# Initialize with visible browser
provider = MarketDataProvider(
    download_path=download_path,
    show_browser=True
)

provider.run()
```

## Output Format

The provider downloads a CSV file with information about all stocks listed on B3. The specific columns and format depend on what DadosDeMercado provides, but typically include:

- Stock ticker
- Company name
- Sector
- ISIN code
- Market segments
- And other relevant information

## Notes

- The provider relies on Selenium to interact with the DadosDeMercado website.
- A stable internet connection is required for the download to complete successfully.
- The download might take some time depending on the file size and your connection speed.
- By default, the download timeout is set to 30 seconds. If your internet connection is slow, the download might fail.
- The provider will automatically close the browser after the download is complete or if an error occurs.

## Related Resources

- [DadosDeMercado](https://www.dadosdemercado.com.br/acoes)
- [B3 - Brazil Stock Exchange](http://www.b3.com.br/)
