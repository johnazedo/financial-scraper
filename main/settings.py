import os

URL: str = "https://www.fundsexplorer.com.br/ranking"
TIME_TO_SLEEP: int = 10
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Log():
    def log(tag: str, msg: str):
        print(f'{tag}: {msg}')
    
    def log_error(tag: str, msg: str, error: Exception):
        print(f'{tag}: {msg}')
        print(f'Root cause: {error}')