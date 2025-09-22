from main.settings import BASE_DIR_DOWNLOAD, Log, BASE_DIR_DATA, STATUSINVEST_CSV_ALL_STOCKS_FILENAME, STATUSINVEST_CSV_FINANCIAL_STOCKS_FILENAME, STATUSINVEST_CSV_ORIGIN_FILENAME, MARKETDATA_CSV_ORIGIN_FILENAME, TRADINGVIEW_CSV_ORIGIN_FILENAME
import pandas as pd


class FinalCSV():

    def __init__(self):
        try:
            self.get_data_from_status_invest()
            self.get_data_from_market_data()
            self.get_data_from_trading_view()
        except FileNotFoundError as e:
            Log.log_error("Unable to open file", e)

    def get_data_from_status_invest(self) -> None:
        # Get all columns from statusinvest
        Log.log("Get data from status invest")
        filename = f"{BASE_DIR_DOWNLOAD}/{STATUSINVEST_CSV_ALL_STOCKS_FILENAME}"
        self.status_invest_data = pd.read_csv(filename, delimiter=";")
        Log.log("Get data from status invest financial")
        filename = f"{BASE_DIR_DOWNLOAD}/{STATUSINVEST_CSV_FINANCIAL_STOCKS_FILENAME}"
        self.status_invest_financial_data = pd.read_csv(filename, delimiter=";")


    def get_data_from_market_data(self) -> None:
        # Get name, price and price variation
        Log.log("Get data from market data")
        FILENAME = f"{BASE_DIR_DOWNLOAD}/{MARKETDATA_CSV_ORIGIN_FILENAME}"
        self.market_data = pd.read_csv(FILENAME, delimiter=",")

    def get_data_from_trading_view(self) -> None:
        # Get image and department
        Log.log("Get data from trading view")
        FILENAME = f"{BASE_DIR_DOWNLOAD}/{TRADINGVIEW_CSV_ORIGIN_FILENAME}"
        self.trading_view_data = pd.read_csv(FILENAME, delimiter=";")

    def generate_final_csv(self, filename: str) -> None:
        df_sel_market_data = self.market_data[["Ticker", "Nome", "Última (R$)", "Variação"]]
        df_sel_trading_view = self.trading_view_data[["STOCK", "DEPARTMENT","IMAGE"]]

        df_merged = self.status_invest_data.merge(df_sel_market_data, left_on="TICKER", right_on="Ticker", how="left")
        df_merged = df_merged.merge(df_sel_trading_view, left_on="TICKER", right_on="STOCK", how="left")

        df_merged.to_csv(f"{BASE_DIR_DATA}/{filename}", index=False, sep=";")

