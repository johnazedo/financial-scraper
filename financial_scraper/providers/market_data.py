from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from financial_scraper.config.selenium import Selenium
from financial_scraper.config.utils import Log, check_if_file_was_downloaded
import os

# TODO: Change name to MarketDataProvider


class MarketDataService():
    """
    A service for downloading comprehensive Brazilian stock market data from dadosdemercado.com.br.

    This class retrieves a complete list of stocks listed on B3 (Brazil's stock exchange)
    with their respective information. The data is downloaded as a CSV file and can be 
    saved with a custom filename.

    Attributes:
        download_path (str): Directory path where the CSV file will be saved.
        filename (str, optional): Custom filename for the output CSV file.
                                 If not provided, the original filename is used.
        show_browser (bool): Whether to show the browser window during scraping.
    """

    _URL = "https://www.dadosdemercado.com.br/acoes"
    _MARKETDATA_CSV_ORIGIN_FILENAME = "acoes-listadas-b3.csv"

    def __init__(self, download_path: str, filename: str = None, show_browser: bool = False):
        """
        Initialize the MarketDataService.

        Args:
            download_path (str): Directory path where downloaded files will be saved.
            filename (str, optional): Custom filename for the downloaded CSV file.
                If None, a default filename will be used.
            show_browser (bool, optional): Whether to show the browser window during execution.
                Defaults to False (headless mode).
        """
        self.filename = filename
        self.download_path = download_path
        self.show_browser = show_browser

    def config_step(self):
        Log.log("Start")
        options = Selenium.get_options(download_path=self.download_path, show_browser=self.show_browser)
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

            Log.log(f"Save file in {self.download_path}")

            timeout = 30
            is_file_downloaded = check_if_file_was_downloaded(
                self._MARKETDATA_CSV_ORIGIN_FILENAME, timeout, self.download_path)
            if is_file_downloaded:
                Log.log("Download completed!")
            else:
                Log.log("Erro to found .csv into downloads folder!")
        except Exception as e:
            Log.log_error("Error when try to download csv", e)
        finally:
            self.driver.quit()

    def transform_data_into_csv(self):
        Log.log("Start")
        origin_file_path = os.path.join(self.download_path, self._MARKETDATA_CSV_ORIGIN_FILENAME)
        if self.filename:
            os.rename(origin_file_path, os.path.join(self.download_path, self.filename))

    def run(self):
        """
        Run the complete process to download stock market data.

        This is the main method that executes the entire workflow:
        1. Configure the Selenium WebDriver
        2. Make a request to the website and download the CSV file
        3. Rename the file if a custom filename was provided

        Example:
            >>> service = MarketDataService(download_path="./data")
            >>> service.run()
        """
        self.config_step()
        self.make_request()
        self.transform_data_into_csv()
