from main.settings import BASE_DIR_DOWNLOAD, Log
import pandas as pd


class FinalCSV():

    def __init__(self):
        try:
            self.get_data_from_status_invest()
            self.get_data_from_market_data()
            self.get_data_from_trading_view()
        except Exception as e:
            Log.log_error("Unable to open file", e)

    def get_data_from_status_invest(self) -> None:
        Log.log("Get data from status invest")
        FILENAME = f"{BASE_DIR_DOWNLOAD}/statusinvest-busca-avancada.csv"
        self.status_invest_data = pd.read_csv(FILENAME, delimiter=";")

    def get_data_from_market_data(self) -> None:
        Log.log("Get data from market data")
        FILENAME = f"{BASE_DIR_DOWNLOAD}/acoes-listadas-b3.csv"
        self.market_data = pd.read_csv(FILENAME, delimiter=",")

    def get_data_from_trading_view(self) -> None:
        Log.log("Get data from trading view")
        FILENAME = f"{BASE_DIR_DOWNLOAD}/trading-view-stocks.csv"
        self.trading_view_data = pd.read_csv(FILENAME, delimiter=";")

    def generate_final_csv(self) -> None:
        pass
