from services.service import Service
from typing import List
import requests
from requests import Response
from bs4 import BeautifulSoup, Tag
from main.settings import HTTP_SUCCESS_CODE, Log

class TradingViewService(Service):

    _SYMBOL = ":stock:"
    _URL = f"https://br.tradingview.com/symbols/BMFBOVESPA-{_SYMBOL}/"
    _IMG_SEARCH_STRING = 'img[class*="logo-"]'
    _IMG_WANTED_ATTRIBUTE  = "src"

    def config_step(self):
        self.url = self._URL.replace(":stock:", self.stock)

    def make_request(self):
        response: Response = requests.get(self.url)
        if response.status_code == HTTP_SUCCESS_CODE:
            html = response.text
            self.page = BeautifulSoup(html, 'html.parser')
        else:
            Log.log(f"Failed request with status code {response.status_code}")

    def read_page_and_get_data(self):
            img_tag: Tag = self.page.select_one(self._IMG_SEARCH_STRING)

            if img_tag == None:
                Log.log(f"It is not possible find tag")
            
            image = img_tag[self._IMG_WANTED_ATTRIBUTE]
            name_tag: Tag = self.page.select_one(self._)

    def transform_data_into_csv(self):
        pass

    def run(self, stocks: List[str]):
        for stock in stocks:
            self.stock = stock
            super().run()