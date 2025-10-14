import csv
import os
import requests
from typing import List
from bs4 import BeautifulSoup
from financial_scraper.config.utils import Log


class InvestorTenProvider():
    """
    A provider for scraping Real Estate Investment Trust (FIIS) dividend data from Investidor10 website.
    
    This class retrieves information about dividends paid by Brazilian REITs (FIIs) 
    for specified years and months. The data is collected from the Investidor10 
    website and saved into a CSV file.
    
    Attributes:
        download_path (str): Directory path where the CSV file will be saved.
        filename (str, optional): Custom filename for the output CSV file.
                                 If not provided, defaults to 'funds-{year}.csv'.
    """

    _URL = "https://investidor10.com.br/fiis/dividendos/:year:/:month:/"
    _MONTHS = ["janeiro", "fevereiro", "marco", "abril", "maio", "junho",
               "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
    _FILENAME = "funds-:year:.csv"
    _HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Referer': 'https://investidor10.com.br',
        'Connection': 'keep-alive'
    }

    def __init__(self, download_path: str, filename: str = None):
        super().__init__()
        self.download_path = download_path
        self.filename = filename
        os.makedirs(self.download_path, exist_ok=True)

    def _make_request(self):
        Log.log(f"Start for month {self.month}")
        url = self._URL.replace(":year:", self.year).replace(":month:", self.month)
        Log.log(f"Url: {url}")

        try:
            response = requests.get(url, headers=self._HEADERS)
            response.raise_for_status()
            self.response = response.text
        except Exception as e:
            Log.log_error(f"Error making request for {self.month} {self.year}", e)
            raise e

        try:
            soup = BeautifulSoup(self.response, 'html.parser')
            self.table = soup.select_one("table.min-w-full.bg-white.md\\:shadow.border-collapse.border-spacing-0")
            if not self.table:
                Log.log(f"No dividend table found for {self.month} {self.year}")
                return
        except Exception as e:
            Log.log_error(f"Error parsing HTML for {self.month} {self.year}", e)
            raise e

    def _read_page_and_get_data(self):
        rows = self.table.select("tbody tr")
        Log.log(f"Found {len(rows)} rows for {self.month}")
        for row in rows:
            cols = row.select("td")
            if not cols:
                continue

            ticker = cols[0].select_one(".ticker-name").get_text(strip=True)
            vector_cols = [col.get_text(strip=True) for col in cols]
            if vector_cols:
                vector_cols[0] = ticker
                cleaned = self._clean_data(vector_cols)
                self.result.append(cleaned)

    def _transform_data_into_csv(self):
        Log.log("Start")
        headers = ["FII", "Data Com", "Data Pagamento", "Tipo", "Valor"]
        path = f"{self.download_path}/{self._FILENAME.replace(':year:', self.year)}"
        if self.filename:
            path = f"{self.download_path}/{self.filename}"
        with open(path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(headers)
            writer.writerows(self.result)
            Log.log(f"Create file {path}")

    def run(self, year: str):
        """
        Run the scraping process for a specific year.
        
        This is the main method to execute the scraping process. It iterates through
        all months of the specified year, collects dividend data for each month,
        and saves the results to a CSV file.
        
        Args:
            year (str): The year to collect dividend data for (e.g., "2023").
        """
        self.year = year
        self.result = []
        for month in self._MONTHS:
            self.month = month
            try:
                self._make_request()
            except:
                continue
            self._read_page_and_get_data()
        self._transform_data_into_csv()

    def _clean_data(self, row: List[str]) -> List[str]:
        # Clean column FII
        try:
            row[0] = row[0].split('\n')[0]
        except Exception as e:
            Log.log_error(f"Unable to clean data of {row} in column FII", e)
            return row

        # Clean column Data com
        try:
            row[1] = row[1].replace('/', '-')
            row[1] = row[1].replace('Data Com', '').strip()
        except Exception as e:
            Log.log_error(f"Unable to clean data of {row[0]} in column Data com. Row: {row}", e)

        # Clean column Pagamento com
        try:
            row[2] = row[2].replace('/', '-')
            row[2] = row[2].replace('Pgto', '').strip()
        except Exception as e:
            Log.log_error(f"Unable to clean data of {row[0]} in column Pagamento com. Row: {row}", e)

        try:
            value_text = row[4]
            if "R$" in value_text:
                value_text = value_text.split("R$")[1].strip()
            row[4] = value_text.replace(',', '.')
        except Exception as e:
            Log.log_error(f"Unable to clean data of {row[0]} in column Valor. Row: {row}", e)

        return row
