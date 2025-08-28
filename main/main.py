from services.funds_explorer import FundsExplorerService
from services.status_invest import StatusInvestService
from services.market_data import MarketDataService

def get_funds():
    service = FundsExplorerService()
    service.run()

def get_stocks():
    status_invest_service = StatusInvestService()
    status_invest_service.run()

    market_data_service = MarketDataService()
    market_data_service.run()

    # TODO: Join all data into one csv
