# InvestorTen Provider

The `InvestorTenProvider` allows you to scrape dividend data for Brazilian REITs (FIIs) from the Investidor10 website.

## Overview

This provider collects detailed information about dividends paid by REITs for a specific year, including:

- FII ticker symbol
- Record date ("Data Com")
- Payment date ("Data Pagamento")
- Dividend type
- Dividend value

The data is collected from the Investidor10 website and saved to a CSV file for further analysis.

## Usage

### Basic Usage

```python
from financial_scraper import InvestorTenProvider
import os

# Set the download path
download_path = os.path.dirname(os.path.abspath(__file__))

# Initialize the provider
provider = InvestorTenProvider(
    download_path=download_path,
)

# Fetch REIT dividend data for year 2023
provider.run(year="2023")
```

### Custom Filename

You can specify a custom filename for the output CSV:

```python
from financial_scraper import InvestorTenProvider
import os

download_path = os.path.dirname(os.path.abspath(__file__))

# Initialize with custom filename
provider = InvestorTenProvider(
    download_path=download_path,
    filename="fiis-dividends-2023.csv"
)

provider.run(year="2023")
```

## Output Format

The provider generates a CSV file with the following columns:

| FII | Data Com | Data Pagamento | Tipo | Valor |
|-----|----------|---------------|------|-------|
| HGLG11 | 21-03-2023 | 27-03-2023 | Rendimento | 1.25 |
| ... | ... | ... | ... | ... |

## Notes

- The data is collected month by month for the specified year.
- The CSV file uses a semicolon (`;`) as the delimiter.
- The dividend values are converted to decimal format (using `.` as the decimal separator).
- Date formats are standardized to use hyphens (`-`) instead of slashes (`/`).