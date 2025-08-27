import os, time
from selenium.webdriver.chrome.options import Options
import inspect

URL: str = "https://www.fundsexplorer.com.br/ranking"
TIME_TO_SLEEP: int = 10
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR_DOWNLOAD = os.path.join(os.path.dirname(BASE_DIR), "downloads")


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
    def get_options() -> Options:
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        prefs = {
            "download.default_directory": BASE_DIR_DOWNLOAD,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
        }
        options.add_experimental_option('prefs', prefs)
        return options


def check_if_file_was_downloaded(filename: str, timeout: int) -> bool:
    found = False
    for _ in range(timeout):
        files = [f for f in os.listdir(BASE_DIR_DOWNLOAD) if f.endswith(filename)]
        if files:
            found = True
            break
        time.sleep(1)

    return found
