import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from config.utils import Log


class FundamentusProvider():
    _URL = "https://fundamentus.com.br/resultado.php"
    _HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    def __init__(self, download_path: str):
        super().__init__()
        self.data = []
        self.download_path = download_path

    def config_step(self):
        Log.log("Skip config step")

    def make_request(self):
        """Make request to Fundamentus website"""
        try:
            Log.log(f"Making request to {self._URL}")
            response = requests.get(self._URL, headers=self._HEADERS)
            response.raise_for_status()
            self.html_content = response.content
            Log.log("Request successful")
        except Exception as e:
            Log.log_error("Error making request to Fundamentus", e)
            raise e

    def read_page_and_get_data(self):
        """Parse HTML and extract table data"""
        try:
            Log.log("Parsing HTML content")
            soup = BeautifulSoup(self.html_content, 'html.parser')
            table = soup.find('table')
            
            headers = []
            for th in table.find_all('th'):
                headers.append(th.text.strip())
            
            for tr in table.find_all('tr')[1:]:
                row = []
                for td in tr.find_all('td'):
                    row.append(td.text.strip())
                if row:
                    self.data.append(row)
            
            Log.log(f"Successfully parsed {len(self.data)} rows of data")
            
            self.df = pd.DataFrame(self.data, columns=headers)
            
        except Exception as e:
            Log.log_error("Error parsing HTML content", e)
            raise e

    def transform_data_into_csv(self):
        """Save the data to CSV file"""
        try:
            current_date = datetime.now().strftime("%d-%m-%Y")
            filename = f"fundamentus-{current_date}.csv"
            filepath = f"{self.download_path}/{filename}"
            
            Log.log(f"Saving data to {filepath}")
            self.df.to_csv(filepath, index=False, sep=';')
            Log.log("Data successfully saved to CSV")
            
        except Exception as e:
            Log.log_error("Error saving data to CSV", e)
            raise e
        
    def run(self):
        self.config_step()
        self.make_request()
        self.read_page_and_get_data()
        self.transform_data_into_csv()