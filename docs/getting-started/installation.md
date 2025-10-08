# Installation

This guide will help you set up the Financial Scraper tool on your system.

## Prerequisites

Before installing Financial Scraper, ensure you have the following:

- Python 3.10 or higher
- pip or Poetry (for dependency management)
- Git (for cloning the repository)

## Installation Methods

### Using Poetry (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/johnazedo/financial-scraper.git
cd financial-scraper
```

2. Install dependencies using Poetry:
```bash
poetry install
```

3. Activate the virtual environment:
```bash
poetry shell
```

### Using pip

You can also install the package directly using pip:

```bash
pip install git+https://github.com/johnazedo/financial-scraper.git
```

## Verify Installation

To verify that Financial Scraper is installed correctly, run one of the example scripts:

```bash
poetry run example_status_invest
```

If successful, you should see the script executing and potentially downloading data from the Status Invest website.

## Troubleshooting

### Common Issues

#### Selenium WebDriver Issues

If you encounter issues related to Selenium:

1. Ensure you have a compatible web browser installed
2. Check that the WebDriver is in your PATH
3. Consider using the bundled WebDriver configuration:

```python
from financial_scraper.config.selenium import setup_driver

driver = setup_driver()
```

#### Package Not Found

If Python cannot find the package after installation:

1. Verify that you are in the correct virtual environment
2. Try reinstalling using:
```bash
poetry install --no-dev
```

For more help, please [open an issue](https://github.com/johnazedo/financial-scraper/issues/new) on GitHub.