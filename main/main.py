from requests import Response
import requests
from bs4 import BeautifulSoup, Tag
from main.settings import URL, HTTP_SUCCESS_CODE, Log, TIME_TO_SLEEP
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time


def get_funds():
    WSFundsExplorer()


class WSFundsExplorer():

    def __init__(self):
        self.config_step()
        self.get_page_source_code()

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

        





