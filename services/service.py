from abc import ABC, abstractmethod

class Service(ABC):

    def __init__(self):
        super().__init__()

    @abstractmethod
    def config_step(self):
        pass

    @abstractmethod
    def make_request(self):
        pass

    @abstractmethod
    def read_page_and_get_data(self):
        pass

    @abstractmethod
    def transform_data_into_csv(self):
        pass

    def run(self):
        self.config_step()
        self.make_request()
        self.read_page_and_get_data()
        self.transform_data_into_csv()