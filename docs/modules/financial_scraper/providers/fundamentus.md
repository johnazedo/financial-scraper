# Fundamentus Provider

The `FundamentusProvider` class scrapes stock data from the Fundamentus website, which provides fundamental analysis data for Brazilian stocks.

## Overview

The Fundamentus provider uses the `requests` library and `BeautifulSoup` to fetch and parse stock data from the Fundamentus website. Unlike the Status Invest provider, it doesn't require browser automation as it directly parses HTML content.

## Class Definition

```python
class FundamentusProvider:
    _URL = "https://fundamentus.com.br/resultado.php"
    _HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    def __init__(self, download_path: str):
        # Initialize with download path
        
    def config_step(self):
        # No configuration needed
    
    def make_request(self):
        # Make HTTP request to Fundamentus website
    
    def read_page_and_get_data(self):
        # Parse HTML and extract table data
        
    def transform_data_into_csv(self):
        # Save parsed data to CSV file
        
    def run(self):
        # Execute the scraping process
```

## Usage

```python
from financial_scraper import FundamentusProvider

# Initialize with download path
provider = FundamentusProvider(download_path="/path/to/downloads")

# Fetch and save data
provider.run()
```

## Output

The provider generates a CSV file with a date stamp in the filename:

```
fundamentus-DD-MM-YYYY.csv
```

Where `DD-MM-YYYY` is the current date (e.g., `fundamentus-08-10-2023.csv`).

## Data Fields

The Fundamentus provider extracts a variety of fundamental stock data. The exact fields may vary, but typically include:

- Ticker symbol
- Company name
- Market price
- P/E ratio (Price/Earnings)
- P/B ratio (Price/Book)
- Market capitalization
- Enterprise Value
- ROIC (Return on Invested Capital)
- ROE (Return on Equity)
- Dividend yield
- And other fundamental indicators

## Implementation Details

The provider:

1. Makes an HTTP request to the Fundamentus website
2. Parses the HTML content using BeautifulSoup
3. Extracts table headers and data rows
4. Converts the data into a pandas DataFrame
5. Saves the DataFrame to a CSV file with the current date in the filename

The implementation includes error handling and logging to track the progress and catch any issues during the scraping process.

## Dependencies

- `pandas`: For data manipulation and CSV export
- `requests`: For HTTP requests
- `BeautifulSoup`: For HTML parsing
- `datetime`: For generating date stamps