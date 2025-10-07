from config.selenium import Selenium
from config.utils import Log, check_if_file_was_downloaded
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import os
from enum import Enum


class StatusInvestProvider():

    class Sector(Enum):
        CYCLIC_CONSUMPTION = ("cyclic-consumption", "Consumo Cíclico")
        NON_CYCLIC_CONSUMPTION = ("non-cyclic-consumption", "Consumo não Cíclico")
        PUBLIC_UTILITIES = ("public-utilities", "Utilidade Pública")
        INDUSTRIAL_GOODS = ("industrial-goods", "Bens Industriais")
        BASIC_MATERIALS = ("basic-materials", "Materiais Básicos")
        FINANCIAL_AND_OTHERS = ("financial-and-others", "Financeiro e Outros")
        INFORMATION_TECHNOLOGY = ("information-technology", "Tecnologia da Informação")
        HEALTHCARE = ("healthcare", "Saúde")
        OIL_GAS_AND_BIOFUELS = ("oil-gas-and-biofuels", "Petróleo. Gás e Biocombustíveis")
        COMMUNICATIONS = ("communications", "Comunicações")
        UNDEFINED = ("undefined", "Indefinido")

    _SEARCH_BUTTON_DATA_TOOLTIP = "Clique para fazer a busca com base nos valores informados"
    _URL = "https://statusinvest.com.br/acoes/busca-avancada"
    _STATUSINVEST_CSV_ORIGIN_FILENAME = "statusinvest-busca-avancada.csv"
    _STATUSINVEST_CSV_SECTOR_STOCKS_FILENAME = "statusinvest-busca-avancada-:sector:.csv"

    def __init__(self, download_path: str):
        super().__init__()
        self.download_path = download_path

    def config_step(self):
        Log.log("Start")
        options = Selenium.get_options(self.download_path)
        self.driver = webdriver.Chrome(options=options)
    
    def make_request(self):
        Log.log("Start")
        self.driver.get(self._URL)

        try:
            if(self.sector != StatusInvestProvider.Sector.UNDEFINED):
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
            is_file_downloaded = check_if_file_was_downloaded(self._STATUSINVEST_CSV_ORIGIN_FILENAME, timeout, self.download_path)
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
        if(self.sector == StatusInvestProvider.Sector.UNDEFINED):
            return

        filename = self._STATUSINVEST_CSV_SECTOR_STOCKS_FILENAME.replace(":sector:", self.sector.value[0])
        new_path = f"{self.download_path}/{filename}"
        old_path = f"{self.download_path}/{self._STATUSINVEST_CSV_ORIGIN_FILENAME}"
        os.rename(old_path, new_path)

    def run(self, sector: Sector = Sector.UNDEFINED):
        self.sector = sector
        self.config_step()
        self.make_request()
        self.read_page_and_get_data()
        self.transform_data_into_csv()