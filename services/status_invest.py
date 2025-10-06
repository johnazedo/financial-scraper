from services.service import Service
from main.settings import Log, Selenium, BASE_DIR_DOWNLOAD, check_if_file_was_downloaded, update_download_history, STATUSINVEST_CSV_ALL_STOCKS_FILENAME, STATUSINVEST_CSV_FINANCIAL_STOCKS_FILENAME,STATUSINVEST_CSV_ORIGIN_FILENAME, STATUSINVEST_CSV_SECTOR_STOCKS_FILENAME
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.common.by import By
import os, time
from enum import Enum



class StatusInvestService(Service):

    class Sector(Enum):
        cyclic_consumption = ("cyclic-consumption", "Consumo Cíclico")
        non_cyclic_consumption = ("non-cyclic-consumption", "Consumo não Cíclico")
        public_utilities = ("public-utilities", "Utilidade Pública")
        industrial_goods = ("industrial-goods", "Bens Industriais")
        basic_materials = ("basic-materials", "Materiais Básicos")
        financial_and_others = ("financial-and-others", "Financeiro e Outros")
        information_technology = ("information-technology", "Tecnologia da Informação")
        healthcare = ("healthcare", "Saúde")
        oil_gas_and_biofuels = ("oil-gas-and-biofuels", "Petróleo. Gás e Biocombustíveis")
        communications = ("communications", "Comunicações")
        undefined = ("undefined", "Indefinido")

    _SEARCH_BUTTON_DATA_TOOLTIP = "Clique para fazer a busca com base nos valores informados"
    _URL = "https://statusinvest.com.br/acoes/busca-avancada"

    def __init__(self, download_path: str):
        super().__init__()
        self.download_path = download_path

    def config_step(self):
        Log.log("Start")
        options = Selenium.get_options()
        self.driver = webdriver.Chrome(options=options)
    
    def make_request(self):
        Log.log("Start")
        self.driver.get(self._URL)

        try:
            if(self.sector != StatusInvestService.Sector.undefined):
                Log.log(f"Select sector {self.sector}")
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
                        (By.XPATH, f"//ul[contains(@class,'select-dropdown')]/li/span[normalize-space()='{self.sector.value[1]}']")
                    )
                )
                Log.log(f"Click to {self.sector}")
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

            Log.log(f"Save file in {self.download_path}")

            timeout = 30
            is_file_downloaded = check_if_file_was_downloaded(STATUSINVEST_CSV_ORIGIN_FILENAME, timeout, self.download_path)
            if is_file_downloaded:
                Log.log("Download completed!")
                self._rename_file()
            else:
                Log.log(f"Erro to found .csv into {self.download_path}!")
                
        except Exception as e:
            Log.log_error("Error when try to download csv", e)
        finally:
            self.driver.quit()

    def read_page_and_get_data(self):
        Log.log("Skip read page and get data step")

    def transform_data_into_csv(self):
        Log.log("Skip transform data into csv")
    
    def _rename_file(self):
        if(self.sector != StatusInvestService.Sector.undefined):
            self.filename = STATUSINVEST_CSV_SECTOR_STOCKS_FILENAME.replace(":sector:", self.sector.value[0])
        else:
            self.filename = STATUSINVEST_CSV_ALL_STOCKS_FILENAME
        
        new_filename = f"{self.download_path}/{self.filename}"
        old_filename = f"{self.download_path}/{STATUSINVEST_CSV_ORIGIN_FILENAME}"

        os.rename(old_filename, new_filename)

    def run(self, sector: Sector = Sector.undefined):
        self.sector = sector
        super().run()
