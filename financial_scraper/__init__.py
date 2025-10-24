"""
Financial Scraper - A library for scraping Brazilian market data
"""

from .providers.status_invest import StatusInvestProvider
from .providers.fundamentus import FundamentusProvider
from .providers.investor_ten import InvestorTenProvider
from .providers.trading_view import TradingViewProvider
from .providers.market_data import MarketDataProvider
from .providers.funds_explorer import FundsExplorerProvider

__version__ = "1.0.0"
__all__ = ['StatusInvestProvider', 'FundamentusProvider',
           'InvestorTenProvider', 'TradingViewProvider', 'MarketDataProvider',  'FundsExplorerProvider']
