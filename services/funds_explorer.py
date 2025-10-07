import time
import csv
import os
from datetime import datetime
from bs4 import BeautifulSoup
from services.settings import Log, BASE_DIR, Selenium, update_download_history, BASE_DIR_DATA_FUNDS
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from services.service import Service

class FundsExplorerService(Service):

    _FUNDS_EXPLORER_URL: str = "https://www.fundsexplorer.com.br/ranking"
    _TIME_TO_SLEEP: int = 10

    def config_step(self):
        Log.log("Start")
        options = Selenium.get_options()
        self.driver = webdriver.Chrome(options=options)

    def make_request(self):
        Log.log("Start")
        try:
            self.driver.get(self._FUNDS_EXPLORER_URL)
            Log.log(f"Accessing {self._FUNDS_EXPLORER_URL}")
            time.sleep(self._TIME_TO_SLEEP)
            self.source_code = self.driver.page_source
        except Exception as e:
            Log.log_error("Error when extract data", e)
        finally:
            self.driver.quit()
    
    def read_page_and_get_data(self):
        Log.log("Start")
        self.rows = []

        soup = BeautifulSoup(self.source_code, "html.parser")
        table = soup.select_one("table")
        if not table:
            return None

        Log.log("Get header from table")
        self.heads = [th.get_text(strip=True) for th in table.select("thead th")]
        if not self.heads:
            return None
        Log.log("Load table header")
        
        Log.log("Get information from table")
        body_rows = table.select("tbody tr")
        for tr in body_rows:
            cells = [td.get_text(strip=True) for td in tr.select("td,th")]
            self.rows.append(cells)
        Log.log(f"Load {len(self.rows)} itens")

    def transform_data_into_csv(self):
        Log.log("Start")
        today = datetime.today().strftime("%d-%m-%Y")
        filename = f"funds-{today}.csv"
        path = f"{BASE_DIR_DATA_FUNDS}/{filename}"
        Log.log(f"Get path: {path}")

        with open(path, "w", encoding="utf-8") as f:
            writer = csv.writer(f)
            Log.log("Write header into file")
            writer.writerow(self.heads)
            Log.log("Write rows into file")
            writer.writerows(self.rows)
        
        update_download_history(filename)