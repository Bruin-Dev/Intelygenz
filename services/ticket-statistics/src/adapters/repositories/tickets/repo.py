from datetime import datetime
from typing import Dict
from adapters.db.mongodb import IDB


class TicketsRepository(object):
    COLLECTION_NAME = 'tickets'

    def __init__(self, database: IDB, logger):
        """
        Creation object of tickets repository
        :param database:
        :param logger:
        """
        self.database = database
        self.logger = logger

        default_database = self.database.client.get_default_database()

        self.collection = default_database[self.COLLECTION_NAME]
        self.logger.info(f"Initializing {type(self).__name__} REPO")

    def get_ticket_by_date(self, start: datetime, end: datetime, status: bool) -> Dict:
        """
        Get tickets by date.
        :param start:
        :param end:
        :param status:
        :return Dict:
        """

        tickets = self.collection.find({'date': {'$gte': start, '$lte': end}, 'status': status})

        if tickets.count() == 0:
            self.logger.info(f'No tickets found between {start} and {end} on the DB')
        else:
            self.logger.info(f'Found {tickets.count()} tickets between {start} and {end} on the DB')

        return tickets
