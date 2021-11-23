import abc

from pymongo import MongoClient


class IDB(metaclass=abc.ABCMeta):

    def __init__(self, config, logger) -> None:
        self.config = config
        self.logger = logger
        self.logger.info("Init Mongo DB")
        self.client = None
        self.initialize()

    @abc.abstractmethod
    def initialize(self):
        pass


class MongoDB(IDB):
    def initialize(self):
        self.logger.info("Connected to Mongo DB")
        self.client = MongoClient(self.config['mongo']['url'])
        self.logger.info(f'Mongo server info: {self.client.server_info()}')
