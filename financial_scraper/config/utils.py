import inspect
import time
import os

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


def check_if_file_was_downloaded(filename: str, timeout: int, download_path: str) -> bool:
    found = False
    for _ in range(timeout):
        files = [f for f in os.listdir(download_path) if f.endswith(filename)]
        if files:
            found = True
            break
        time.sleep(1)

    return found
