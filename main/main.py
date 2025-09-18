from services.funds_explorer import FundsExplorerService
from services.status_invest import StatusInvestService
from services.market_data import MarketDataService
from services.trading_view import TradingViewService
from main.settings import BASE_DIR_DOWNLOAD, get_download_date
from main.core import FinalCSV
from typing import List
import pandas as pd

def get_funds():
    service = FundsExplorerService()
    service.run()

def get_stocks():
    status_invest_service = StatusInvestService()
    status_invest_service.run()
    market_data_service = MarketDataService()
    market_data_service.run()

def get_data_from_trading_view():
    stocks = get_stocks_for_csv()
    service = TradingViewService()
    service.run(stocks)

def generate_final_csv():
    fc = FinalCSV()
    filename = f"stocks-{get_download_date()}.csv"
    fc.generate_final_csv(filename)


def get_stocks_for_csv() -> List[str]:
    FILENAME = f"{BASE_DIR_DOWNLOAD}/statusinvest-busca-avancada.csv"
    COLUMN = "TICKER"

    data = pd.read_csv(FILENAME, delimiter=";")
    tickets = data[COLUMN].tolist()

    return tickets    
    

