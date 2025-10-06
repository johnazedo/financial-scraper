import os, time
from datetime import datetime
from selenium.webdriver.chrome.options import Options
import inspect
from pathlib import Path

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR_DOWNLOAD = os.path.join(os.path.dirname(BASE_DIR), "downloads")
BASE_DIR_DATA = os.path.join(os.path.dirname(BASE_DIR), "data/stocks")
BASE_DIR_DATA_FUNDS = os.path.join(os.path.dirname(BASE_DIR), "data/funds")
BASE_DIR_DATA_FUNDS_PROFITS = os.path.join(os.path.dirname(BASE_DIR), "data/funds_profits")
HTTP_SUCCESS_CODE = 200

MARKETDATA_CSV_ORIGIN_FILENAME = "acoes-listadas-b3.csv"

TRADINGVIEW_CSV_ORIGIN_FILENAME = "trading-view-stocks.csv"


class Log():
    def _get_caller_name()-> str:
        caller_frame = inspect.stack()[2].frame
        caller_function = inspect.stack()[2].function
        caller_self = caller_frame.f_locals.get('self', None)
        if caller_self:
            return f"[{caller_self.__class__.__name__}] {caller_function.upper()}"
        else:
            return f"[No Class] {caller_function.upper()}"

    def log(msg: str):
        caller = Log._get_caller_name()
        print(f'{caller}: {msg}')
    
    def log_error(msg: str, error: Exception):
        caller = Log._get_caller_name()
        print(f'{caller}: {msg}')
        print(f'Root cause: {error}')


class Selenium():

    @staticmethod
    def get_options(download_path: str) -> Options:
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        prefs = {
            "download.default_directory": download_path,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
        }
        options.add_experimental_option('prefs', prefs)
        return options


def check_if_file_was_downloaded(filename: str, timeout: int, download_path: str) -> bool:
    found = False
    for _ in range(timeout):
        files = [f for f in os.listdir(download_path) if f.endswith(filename)]
        if files:
            found = True
            break
        time.sleep(1)

    return found


def update_download_history(filename: str):
    FILENAME = f"{BASE_DIR_DOWNLOAD}/download_history.csv"
    HEADER = "NAME;DATE;TIME\n"
    file_path = Path(FILENAME)
    edit_mode = 'a'
    put_header = False
    if not file_path.exists():
        edit_mode = 'w'
        put_header = True

    with open(FILENAME, edit_mode) as file:
        if put_header:
            file.write(HEADER)
        
        date = datetime.today().strftime('%d-%m-%Y')
        time = datetime.today().strftime('%H:%M')
        file.write(f"{filename};{date};{time}\n")


def get_download_date() -> str:
    FILENAME = f"{BASE_DIR_DOWNLOAD}/dowload_history.csv"
    return datetime.today().strftime('%d-%m-%Y')