from typing import List
import requests
from requests import Response
from bs4 import BeautifulSoup
from financial_scraper.config.utils import Log


class TradingViewProvider():

    _SYMBOL = ":stock:"
    _URL = f"https://br.tradingview.com/symbols/BMFBOVESPA-{_SYMBOL}/"
    _DEFUALT_FILENAME = "trading_view.csv"

    def __init__(self, download_path: str, filename: str = None):
        super().__init__(download_path, filename)
        self.download_path = download_path
        self.filename = filename if filename else self._DEFUALT_FILENAME

    def config_step(self):
        Log.log("Start")
        HEADER = "STOCK;NAME;DEPARTMENT;IMAGE\n"
        self.lines = []

    def make_request(self):
        url = self._URL.replace(self._SYMBOL, self.stock)
        response: Response = requests.get(url)

        if response.status_code == 200:
            html = response.text
            self.page = BeautifulSoup(html, 'html.parser')
            self.execute_next_step = True
        else:
            Log.log(f"Failed request with status code {response.status_code} when call for {self.stock}")
            self.execute_next_step = False

    def read_page_and_get_data(self):
        if not self.execute_next_step:
            Log.log("Skip step")
            return

        img_tag = self.page.select_one('img[class*="logo-"]')
        image = img_tag["src"]

        name_tag = self.page.find("h1", class_="apply-overflow-tooltip title-HDE_EEoW")
        name = name_tag.get_text(strip=True)

        prefix = "/markets/stocks-brazil/sectorandindustry-sector/"
        department_tag = self.page.select_one(f'a[href^="{prefix}"]')

        if department_tag == None:
            department = ""
        else:
            department = department_tag.get_text(strip=True)

        self.lines.append(f"{self.stock};{name};{department};{image}\n")

    def transform_data_into_csv(self):
        if not self.lines:
            Log.log("No data to write")
            return

    def run(self, stocks: List[str]):
        self.config_step()
        for stock in stocks:
            self.stock = stock
            self.make_request()
            self.read_page_and_get_data()
        self.transform_data_into_csv()
