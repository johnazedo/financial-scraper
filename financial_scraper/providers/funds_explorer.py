import time
import csv
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from financial_scraper.config.selenium import Selenium
from financial_scraper.config.utils import Log


class FundsExplorerProvider():
    """
    A provider for scraping Real Estate Investment Trust (FII) ranking data from FundsExplorer website.
    
    This class retrieves comprehensive information about Brazilian REITs (FIIs) including
    their rankings, dividend yields, prices, and other financial metrics. The data is collected
    from the FundsExplorer ranking page and saved into a CSV file.
    
    Attributes:
        download_path (str): Directory path where the CSV file will be saved.
        filename (str, optional): Custom filename for the output CSV file.
                                 If not provided, defaults to 'funds-{date}.csv'.
        show_browser (bool): Whether to show the browser window during scraping.
        wait_time (int): Time in seconds to wait for the page to fully load. Defaults to 5.
    """

    _FUNDS_EXPLORER_URL: str = "https://www.fundsexplorer.com.br/ranking"

    def __init__(self, download_path: str, filename: str = None, show_browser: bool = False, wait_time: int = 5):
        """
        Initialize the FundsExplorerProvider with download path and options.
        
        Args:
            download_path (str): Directory path where the CSV file will be saved.
            filename (str, optional): Custom filename for the output CSV file.
                                     If None, defaults to 'funds-{date}.csv' format.
            show_browser (bool, optional): Whether to show the browser window during execution.
                                          Defaults to False (headless mode).
            wait_time (int, optional): Time in seconds to wait for the page to fully load.
                                      Defaults to 5 seconds.
        """
        self.download_path = download_path
        self.filename = filename
        self.show_browser = show_browser
        self.wait_time = wait_time

    def _config_step(self):
        Log.log("Start")
        options = Selenium.get_options(self.download_path, self.show_browser)
        self.driver = webdriver.Chrome(options=options)

    def _make_request(self):
        Log.log("Start")
        try:
            self.driver.get(self._FUNDS_EXPLORER_URL)
            Log.log(f"Accessing {self._FUNDS_EXPLORER_URL}")
            time.sleep(self.wait_time)
            self.source_code = self.driver.page_source
        except Exception as e:
            Log.log_error("Error when extract data", e)
        finally:
            self.driver.quit()

    def _read_page_and_get_data(self):
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
        Log.log(f"Load {len(self.rows)} items")

    def _transform_data_into_csv(self):
        Log.log("Start")
        today = datetime.today().strftime("%d-%m-%Y")
        filename = f"funds-{today}.csv"
        if self.filename:
            filename = self.filename
        path = f"{self.download_path}/{filename}"
        Log.log(f"Get path: {path}")

        with open(path, "w", encoding="utf-8") as f:
            writer = csv.writer(f)
            Log.log("Write header into file")
            writer.writerow(self.heads)
            Log.log("Write rows into file")
            writer.writerows(self.rows)

    def run(self):
        """
        Run the complete process to scrape and save FII ranking data.
        
        This is the main method that executes the entire workflow:
        1. Configure the Selenium WebDriver
        2. Make a request to the FundsExplorer website
        3. Parse the page and extract FII data from the ranking table
        4. Save the data to a CSV file
        
        The data includes comprehensive information about REITs such as:
        - Ticker symbols
        - Current prices
        - Dividend yields
        - Liquidity metrics
        - P/VP ratios
        - And other financial indicators
        
        Example:
            >>> provider = FundsExplorerProvider(download_path="./data")
            >>> provider.run()
        """
        self._config_step()
        self._make_request()
        self._read_page_and_get_data()
        self._transform_data_into_csv()
