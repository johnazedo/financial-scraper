from selenium.webdriver.chrome.options import Options


class Selenium():

    @staticmethod
    def get_options(download_path: str, show_browser: bool = False) -> Options:
        options = Options()
        if not show_browser:
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
            "profile.default_content_settings.popups": 0,
            "profile.content_settings.exceptions.automatic_downloads.*.setting": 1,
            "safebrowsing.disable_download_protection": True,
            "browser.download.folderList": 2,
            "browser.helperApps.neverAsk.saveToDisk": "application/csv,text/csv,application/vnd.ms-excel"
        }
        options.add_experimental_option('prefs', prefs)
        
        # Disable the "Save As" dialog and enable downloads in headless mode
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        return options
