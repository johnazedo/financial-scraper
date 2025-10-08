# Examples

This page provides examples of how to use the Financial Scraper library in your Python code.

## Using Status Invest Provider

The Status Invest provider allows you to scrape stock data from the Status Invest website. You can use it to fetch data for all stocks or for a specific sector.

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

### Available Sectors

The Status Invest provider supports the following sectors:

- `CYCLIC_CONSUMPTION` - Consumo Cíclico
- `NON_CYCLIC_CONSUMPTION` - Consumo não Cíclico
- `PUBLIC_UTILITIES` - Utilidade Pública
- `INDUSTRIAL_GOODS` - Bens Industriais
- `BASIC_MATERIALS` - Materiais Básicos
- `FINANCIAL_AND_OTHERS` - Financeiro e Outros
- `INFORMATION_TECHNOLOGY` - Tecnologia da Informação
- `HEALTHCARE` - Saúde
- `OIL_GAS_AND_BIOFUELS` - Petróleo, Gás e Biocombustíveis
- `COMMUNICATIONS` - Comunicações
- `UNDEFINED` - Indefinido (default)

## Using Fundamentus Provider

The Fundamentus provider allows you to scrape stock data from the Fundamentus website.

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

## Complete Example

The following example demonstrates how to use both providers in a single script:

```python
from financial_scraper import StatusInvestProvider, FundamentusProvider
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def status_invest_example():
    # Initialize the service with Status Invest provider
    provider = StatusInvestProvider(
        download_path=BASE_DIR,
    )
    
    # Fetch and save data
    provider.run()

def fundamentus_example():
    # Initialize the service with Fundamentus provider
    provider = FundamentusProvider(
        download_path=BASE_DIR,
    )
    
    # Fetch and save data
    provider.run()

if __name__ == "__main__":
    status_invest_example()
    fundamentus_example()
```

## Output Files

After running these examples, you'll find CSV files in your specified download path:

- For Status Invest: `statusinvest-busca-avancada.csv` or sector-specific files like `statusinvest-busca-avancada-financial-and-others.csv`
- For Fundamentus: `fundamentus-DD-MM-YYYY.csv` with the current date