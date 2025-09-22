from services.service import Service
from main.settings import Log, Selenium, BASE_DIR_DOWNLOAD, check_if_file_was_downloaded, update_download_history, STATUSINVEST_CSV_ALL_STOCKS_FILENAME, STATUSINVEST_CSV_FINANCIAL_STOCKS_FILENAME,STATUSINVEST_CSV_ORIGIN_FILENAME
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.common.by import By
import os, time


class StatusInvestService(Service):

    _SEARCH_BUTTON_DATA_TOOLTIP = "Clique para fazer a busca com base nos valores informados"
    _URL = "https://statusinvest.com.br/acoes/busca-avancada"
    
    def config_step(self):
        Log.log("Start")
        options = Selenium.get_options()
        self.driver = webdriver.Chrome(options=options)
        self.filename = STATUSINVEST_CSV_ORIGIN_FILENAME
    
    def make_request(self):
        Log.log("Start")
        self.driver.get(self._URL)

        try:
            if(self.get_only_financial_sector):
                Log.log("Select sector Financeiro e Outros")
                Log.log("Search for dropdown-item Sectors")
                span_element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//span[text()='-- Todos setores --']")
                    )
                )
                dropdown_item = span_element.find_element(By.XPATH, "./ancestor::div[@class='select-wrapper']/input")

                Log.log("Click to open sector dropdown")
                dropdown_item.click()

                Log.log("Wait to the options")
                option = WebDriverWait(self.driver, 10).until(
                    EC.visibility_of_element_located(
                        (By.XPATH, "//ul[contains(@class,'select-dropdown')]/li/span[normalize-space()='Financeiro e Outros']")
                    )
                )
                Log.log("Click to Financeiro e Outros")
                option.click()

            Log.log("Get search button")
            search_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, f"//button[@data-tooltip='{self._SEARCH_BUTTON_DATA_TOOLTIP}']"))
            )

            Log.log("Click search button")
            self.driver.execute_script("arguments[0].click();", search_button)

            Log.log("Get download button")
            download_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a.btn-download"))
            )

            Log.log("Click download button")
            self.driver.execute_script("arguments[0].click();", download_button)

            Log.log(f"Save file in {BASE_DIR_DOWNLOAD}")

            timeout = 30
            is_file_downloaded = check_if_file_was_downloaded(self.filename, timeout)
            if is_file_downloaded:
                Log.log("Download completed!")
                self._rename_file()
            else:
                Log.log("Erro to found .csv into downloads folder!")
                
        except Exception as e:
            Log.log_error("Error when try to download csv", e)
        finally:
            update_download_history(self.filename)
            self.driver.quit()

    def read_page_and_get_data(self):
        Log.log("Skip read page and get data step")

    def transform_data_into_csv(self):
        Log.log("Skip transform data into csv")
    
    def _rename_file(self):
        if(self.get_only_financial_sector):
            self.filename = STATUSINVEST_CSV_FINANCIAL_STOCKS_FILENAME
        else:
            self.filename = STATUSINVEST_CSV_ALL_STOCKS_FILENAME
        
        new_filename = f"{BASE_DIR_DOWNLOAD}/{self.filename}"
        old_filename = f"{BASE_DIR_DOWNLOAD}/{STATUSINVEST_CSV_ORIGIN_FILENAME}"

        os.rename(old_filename, new_filename)

    def run(self, get_financial_sector: bool):
        self.get_only_financial_sector = get_financial_sector
        super().run()
