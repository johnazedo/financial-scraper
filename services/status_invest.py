from services.service import Service
from main.settings import Log, Selenium, BASE_DIR
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import os, time


class StatusInvestService(Service):

    _search_button_data_tooltip = "Clique para fazer a busca com base nos valores informados"
    _search_ahref_data_class = "btn-download.btn.btn-main-green.btn-small.waves-effect.waves-light"
    _download_dir = f"{BASE_DIR}/../downloads/"
    
    def config_step(self):
        Log.log("Start")
        options = Selenium.get_options()
        prefs = {
            "download.default_directory": self._download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        options.add_experimental_option("prefs", prefs)
        self.driver = webdriver.Chrome(options=options)
    
    def make_request(self):
        Log.log("Start")
        self.driver.get("https://statusinvest.com.br/acoes/busca-avancada")
        
        try:
            Log.log("Get search button")
            search_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clicked((By.XPATH, f"//button[@data-tooltip='{self._search_button_data_tooltip}']"))
            )
            Log.log("Click search button")
            search_button.click()

            Log.log("Get download button")
            download_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clicked((By.CSS_SELECTOR, f"a.{self._search_ahref_data_class}"))
            )

            Log.log("Click download button")
            download_button.click()


            timeout, found = 30, False
            for _ in range(timeout):
                files = [f for f in os.listdir(self._download_dir) if f.endswith(".csv")]
                if files:
                    Log.log("Download completed!")
                    found = True
                    break
                time.sleep(1)
            if not found:
                pass

        except Exception as e:
            Log.log_error("Error when try to download csv", e)

        finally:
            self.driver.quit()

    def read_page_and_get_data(self):
        Log.log("Skip read page and get data step")

    def transform_data_into_csv(self):
        Log.log("Skip transform data into csv")