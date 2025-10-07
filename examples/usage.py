# Examples of using the market_scraper library

from financial_scraper import  StatusInvestProvider, FundamentusProvider
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def status_invest_example():
    # Initialize the service with Status Invest provider
    service = StatusInvestProvider(
        download_path=BASE_DIR,
    )
    
    # Fetch and save data
    service.run()

def fundamentus_example():
    # Initialize the service with Fundamentus provider
    service = FundamentusProvider(
        download_path=BASE_DIR,
    )
    
    # Fetch and save data
    service.run()

        
if __name__ == "__main__":
    status_invest_example()
    fundamentus_example()
