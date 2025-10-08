"""
Financial Scraper - A library for scraping Brazilian market data
"""

from .providers.status_invest import StatusInvestProvider
from .providers import FundamentusProvider

__version__ = "1.0.0"
__all__ = ['StatusInvestProvider', 'FundamentusProvider']
