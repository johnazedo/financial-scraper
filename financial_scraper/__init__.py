"""
Financial Scraper - A library for scraping Brazilian market data
"""

from .providers.status_invest import StatusInvestProvider
from .providers.fundamentus import FundamentusProvider
from .providers.investor_ten import InvestorTenProvider

__version__ = "1.0.0"
__all__ = ['StatusInvestProvider', 'FundamentusProvider', 'InvestorTenProvider']
