from financial_scraper.config.selenium import Selenium
from financial_scraper.config.utils import Log, check_if_file_was_downloaded
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import os
from enum import Enum


class StatusInvestProvider():
    """
    Provider for scraping stock data from Status Invest website.
    
    This class uses Selenium WebDriver to navigate to Status Invest's advanced search page,
    filter stocks by sector (if specified), and download stock data in CSV format.
    
    Attributes:
        download_path (str): Directory where the downloaded CSV will be saved.
        filename (str, optional): Custom filename for the downloaded CSV.
        show_browser (bool): Whether to show the browser window during scraping.
        sector (Sector): Sector filter to apply during the search.
    """

    class Sector(Enum):
        """
        Enumeration of stock market sectors available on Status Invest.
        
        Each enum value is a tuple containing:
        - First element: URL/filename-friendly sector name
        - Second element: Display name as shown on Status Invest website
        """
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
    _STATUSINVEST_CSV_NEW_STOCKS_FILENAME = "statusinvest:sector:.csv"
    _NO_SECTOR = ""

    def __init__(self, download_path: str, filename: str = None, show_browser: bool = False):
        """
        Initialize the StatusInvestProvider.
        
        Args:
            download_path (str): Directory path where downloaded files will be saved.
            filename (str, optional): Custom filename for the downloaded CSV file.
                If None, a default filename based on sector will be used.
            show_browser (bool, optional): Whether to show the browser window during execution.
                Defaults to False (headless mode).
        """
        super().__init__()
        self.filename = filename
        self.download_path = download_path
        self.show_browser = show_browser

    def _config_step(self):
        Log.log("Start")
        options = Selenium.get_options(self.download_path, self.show_browser)
        self.driver = webdriver.Chrome(options=options)

    def _make_request(self):
        Log.log("Start")
        self.driver.get(self._URL)

        try:
            if (self.sector != StatusInvestProvider.Sector.UNDEFINED):
                self._select_sector()

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
            is_file_downloaded = check_if_file_was_downloaded(
                self._STATUSINVEST_CSV_ORIGIN_FILENAME, timeout, self.download_path)
            if is_file_downloaded:
                Log.log("Download completed!")
                self._rename_file()
            else:
                Log.log(f"Erro to found .csv into {self.download_path}!")

        except Exception as e:
            Log.log_error("Error when try to download csv", e)
        finally:
            self.driver.quit()

    def _rename_file(self):
        # TODO: Make this more readeble
        sector_string = self._NO_SECTOR
        if (self.sector != StatusInvestProvider.Sector.UNDEFINED):
            sector_string = f"-{self.sector.value[0]}"

        filename = self._STATUSINVEST_CSV_NEW_STOCKS_FILENAME.replace(":sector:", sector_string)

        if self.filename is not None:
            filename = self.filename

        new_path = f"{self.download_path}/{filename}"
        old_path = f"{self.download_path}/{self._STATUSINVEST_CSV_ORIGIN_FILENAME}"
        os.rename(old_path, new_path)

    def _select_sector(self):
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
                (By.XPATH,
                 f"//ul[contains(@class,'select-dropdown')]/li/span[normalize-space()='{self.sector.value[1]}']")
            )
        )
        Log.log(f"Click to {self.sector}")
        option.click()

    def run(self, sector: Sector = Sector.UNDEFINED):
        """
        Execute the complete scraping process to fetch stock data.
        
        This is the main public method to run the scraper. It configures the WebDriver,
        navigates to the website, applies filters, downloads the data, and processes it.
        
        Args:
            sector (Sector, optional): Specific sector to filter stocks by.
                Defaults to Sector.UNDEFINED (no sector filter).
                
        Returns:
            None: The results are saved as a CSV file in the download_path.
        """
        self.sector = sector
        self._config_step()
        self._make_request()
