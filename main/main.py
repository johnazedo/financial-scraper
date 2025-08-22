import time
import csv
import os
from datetime import datetime
from bs4 import BeautifulSoup
from main.settings import URL, Log, TIME_TO_SLEEP, BASE_DIR
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


def get_funds():
    WSFundsExplorer()


class WSFundsExplorer():

    def __init__(self):
        self.config_step()
        self.get_page_source_code()
        self.read_source_code_and_get_data()
        self.transform_data_into_csv()

    def config_step(self):
        Log.log("CONFIG_STEP", "Start")
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        self.driver = webdriver.Chrome(options=chrome_options)

    def get_page_source_code(self):
        tag = "GET_PAGE_SOURCE_CODE"
        Log.log(tag, "Start")
        try:
            self.driver.get(URL)
            Log.log(tag, f"Accessing {URL}")
            time.sleep(TIME_TO_SLEEP)
            self.source_code = self.driver.page_source
        except Exception as e:
            Log.log_error(tag, "Error when extract data", e)
        finally:
            self.driver.quit()
    
    def read_source_code_and_get_data(self):
        tag = "READ_SOURCE_CODE_AND_GET_DATA"
        Log.log(tag, "Start")
        self.rows = []

        soup = BeautifulSoup(self.source_code, "html.parser")
        table = soup.select_one("table")
        if not table:
            return None

        Log.log(tag, "Get header from table")
        self.heads = [th.get_text(strip=True) for th in table.select("thead th")]
        if not self.heads:
            return None
        Log.log(tag, "Load table header")
        
        Log.log(tag, "Get information from table")
        body_rows = table.select("tbody tr")
        for tr in body_rows:
            cells = [td.get_text(strip=True) for td in tr.select("td,th")]
            self.rows.append(cells)
        Log.log(tag, f"Load {len(self.rows)} itens")

    def transform_data_into_csv(self):
        tag = "TRANSFORM_DATA_INTO_CSV"
        Log.log(tag, "Start")

        today = datetime.today().strftime("%d-%m-%Y")
        path = os.path.join(BASE_DIR, f"../data/funds-{today}.csv")
        Log.log(tag, f"Get path: {path}")

        with open(path, "w", encoding="utf-8") as f:
            writer = csv.writer(f)
            Log.log(tag, "Write header into file")
            writer.writerow(self.heads)
            Log.log(tag, "Write rows into file")
            writer.writerows(self.rows)
