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

    def get_ticket_by_date(self, query_date: datetime, status: bool) -> Dict:
        """
        Get tickets by date.
        :param query_date:
        :param status:
        :return Dict:
        """
        query_start = query_date.replace(hour=0, minute=0, second=0)
        query_end = query_date.replace(hour=23, minute=59, second=59)

        tickets = self.collection.find({"date": {'$lt': query_end, '$gte': query_start}, 'status': status})
        self.logger.info(f'Number of tickets found: {tickets.count()}')

        if tickets.count() == 0:
            self.logger.info(f'No tickets found in {query_date} on mongodb')
        else:
            self.logger.info(f'Found tickets on {query_date} the number of them is {tickets.count()}')

        return tickets
