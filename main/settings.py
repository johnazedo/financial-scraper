
URL: str = "https://www.fundsexplorer.com.br/ranking"
HTTP_SUCCESS_CODE: int = 200
DRIVER_WAITING_SECONDS: int = 30
TIME_TO_SLEEP: int = 10


class Log():

    def log(tag: str, msg: str):
        print(f'{tag}: {msg}')
    
    def log_error(tag: str, msg: str, error: Exception):
        print(f'{tag}: {msg}')
        print(f'Root cause: {error}')