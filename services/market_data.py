from services.service import Service
from main.settings import Log, Selenium, BASE_DIR_DOWNLOAD, check_if_file_was_downloaded
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import os, time

class MarketDataService(Service):

    _URL = "https://www.dadosdemercado.com.br/acoes"
    _CSV_ORIGIN_FILENAME = "acoes-listadas-b3.csv"

    def config_step(self):
        Log.log("Start")
        options = Selenium.get_options()
        self.driver = webdriver.Chrome(options=options)
    
    def make_request(self):
        Log.log("Start")
        self.driver.get(self._URL)

        try:
            Log.log("Get download button")
            download_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "download-csv"))
            )

            Log.log("Click download button")
            self.driver.execute_script("arguments[0].click();", download_button)

            Log.log(f"Save file in {BASE_DIR_DOWNLOAD}")

            timeout = 30
            is_file_downloaded = check_if_file_was_downloaded(self._CSV_ORIGIN_FILENAME, timeout)
            if is_file_downloaded:
                Log.log("Download completed!")
            else:
                Log.log("Erro to found .csv into downloads folder!")

        except Exception as e:
            Log.log_error("Error when try to download csv", e)
        finally:
            self.driver.quit()

    def read_page_and_get_data(self):
        Log.log("Skip read page and get data step")

    def transform_data_into_csv(self):
        Log.log("Skip transform data into csv")