from services.funds_explorer import FundsExplorerService
from services.status_invest import StatusInvestService
from services.market_data import MarketDataService
from services.trading_view import TradingViewService

def get_funds():
    service = FundsExplorerService()
    service.run()

def get_stocks():
    status_invest_service = StatusInvestService()
    status_invest_service.run()

    market_data_service = MarketDataService()
    market_data_service.run()

    stocks = ["BBAS3", "BEEF3", "BIDI4"]
    service = TradingViewService()
    service.run(stocks)
    # TODO: Join all data into one csv

