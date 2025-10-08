# Basic Usage

This guide covers the basic usage of the Financial Scraper tool for collecting financial data from various sources.

### Collect Stock Data
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
```

For more examples, check the [examples](../examples.md) section.