from services.service import Service
from services.settings import Log
from services.settings import Log, Selenium, BASE_DIR_DOWNLOAD, check_if_file_was_downloaded, update_download_history, MARKETDATA_CSV_ORIGIN_FILENAME, BASE_DIR_DATA_FUNDS_PROFITS
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import csv
from typing import List

class InvestorTenService(Service):

    _URL = "https://investidor10.com.br/fiis/dividendos/:year:/:month:/"
    _MONTHS = ["janeiro", "fevereiro", "marco", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]

    def config_step(self):
        Log.log(f"Start")
        options = Selenium.get_options()
        self.driver = webdriver.Chrome(options=options)
    
    def make_request(self):
        Log.log(f"Start for month {self.month}")
        url = self._URL.replace(":year:", self.year).replace(":month:", self.month)
        Log.log(f"Url: {url}")

        try:
            self.driver.get(url)
            table = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "table.min-w-full.bg-white.md\\:shadow.border-collapse.border-spacing-0"))
            )

            self.rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
        except Exception as e:
            Log.log_error("Error in request", e)
            self.driver.quit()
    
    def read_page_and_get_data(self):
        Log.log(f"Start for month {self.month}")
        for row in self.rows:
            cols = [col.text.strip() for col in row.find_elements(By.TAG_NAME, "td")]
            if cols:
                cleaned = self.clean_data(cols)
                self.result.append(cleaned)
        
        Log.log(f"Number of lines: {len(self.result)}")
        
        self.driver.quit()


    def transform_data_into_csv(self):
        Log.log(f"Start")
        headers = ["FII", "Data Com", "Data Pagamento", "Tipo", "Valor"]
        filename = f"funds-profits-{self.year}.csv"
        path = f"{BASE_DIR_DATA_FUNDS_PROFITS}/{filename}"
        with open(path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(headers)
            writer.writerows(self.result)
            Log.log(f"Create file {path}")
        
        update_download_history(filename)
    
    def run(self, year: str):
        self.year = year
        self.result = []
        for month in self._MONTHS:
            self.month = month 
            self.config_step()
            self.make_request()
            self.read_page_and_get_data()
        self.transform_data_into_csv()
        

    def clean_data(self, row: List[str]) -> List[str]:
        # Clean column FII
        try:
            row[0] = row[0].split('\n')[0]
        except Exception as e:
            Log.log_error(f"Unable to clean data of {row} in column FII", e)
            return row
        
        # Clean column Data com
        try:
            row[1] = row[1].replace('/', '-')
        except Exception as e:
            Log.log_error(f"Unable to clean data of {row[0]} in column Data com. Row: {row}", e)
        
        # Clean column Pagamento com
        try:
            row[2] = row[2].replace('/', '-')
        except Exception as e:
            Log.log_error(f"Unable to clean data of {row[0]} in column Pagamento com. Row: {row}", e)


        # Clean column Valor
        try:
            row[4] = row[4].split(' ')[1].replace(',', '.')
        except Exception as e:
            Log.log_error(f"Unable to clean data of {row[0]} in column . Row: {row}", e)
        
        return row
