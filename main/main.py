from services.funds_explorer import FundsExplorerService
from services.status_invest import StatusInvestService

def get_funds():
    service = StatusInvestService()
    service.run()



