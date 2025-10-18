from typing import List
import requests
from requests import Response
from bs4 import BeautifulSoup
from financial_scraper.config.utils import Log


class TradingViewProvider():

    _SYMBOL = ":stock:"
    _URL = f"https://br.tradingview.com/symbols/BMFBOVESPA-{_SYMBOL}/"
    # _URL_STATISTICS = f"https://br.tradingview.com/symbols/BMFBOVESPA-{_SYMBOL}/financials-statistics-and-ratios/"
    # _URL_DEMOSTRATIONS = f"https://br.tradingview.com/symbols/BMFBOVESPA-{_SYMBOL}/financials-income-statement/"
    _DEFUALT_FILENAME = "trading_view.csv"
    # - SEARCH_STRING - HEADER

    def __init__(self, download_path: str, filename: str = None):
        self.download_path = download_path
        self.filename = filename if filename else self._DEFUALT_FILENAME

    def _config_step(self):
        Log.log("Start")
        self.HEADER = "STOCK;NAME;DEPARTMENT;IMAGE\n"
        self.lines = []

    def _make_request(self):
        url = self._URL.replace(self._SYMBOL, self.stock)
        response: Response = requests.get(url)
        Log.log(f"Making request for {self.stock}")

        if response.status_code == 200:
            html = response.text
            self.page = BeautifulSoup(html, 'html.parser')
            self.execute_next_step = True
        else:
            Log.log(f"Failed request with status code {response.status_code} when call for {self.stock}")
            self.execute_next_step = False

    def _read_page_and_get_data(self):
        if not self.execute_next_step:
            Log.log("Skip step")
            return

        Log.log(f"Reading page and getting data for {self.stock}")

        img_tag = self.page.select_one('img[class*="logo-"]')
        image = img_tag["src"]

        name_tag = self.page.find("h1", class_="apply-overflow-tooltip title-HDE_EEoW")
        name = name_tag.get_text(strip=True)

        prefix = "/markets/stocks-brazil/sectorandindustry-sector/"
        department_tag = self.page.select_one(f'a[href^="{prefix}"]')

        if department_tag is None:
            department = ""
        else:
            department = department_tag.get_text(strip=True)

        self.lines.append(f"{self.stock};{name};{department};{image}\n")

    def _transform_data_into_csv(self):
        if not self.lines:
            Log.log("No data to write")
            return

        file_path = f"{self.download_path}/{self.filename}"
        Log.log(f"Writing data to CSV at {file_path}")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(self.HEADER)
            f.writelines(self.lines)

    def run(self, stocks: List[str]):
        self._config_step()
        for stock in stocks:
            self.stock = stock
            self._make_request()
            self._read_page_and_get_data()
        self._transform_data_into_csv()
