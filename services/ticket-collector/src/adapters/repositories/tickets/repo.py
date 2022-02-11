from datetime import datetime
from typing import Dict

from pymongo.collection import Collection

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
        self.collection = self.create_collection()
        self.logger.info(f"Initializing {type(self).__name__} REPO")

    def create_collection(self) -> Collection:
        """
        Create collection on default database
        :return collection:
        """

        default_database = self.database.client.get_default_database()
        list_collections = default_database.collection_names()

        if self.COLLECTION_NAME in list_collections:
            self.logger.info('The tickets collection exists on the DB')
        else:
            self.logger.info('The tickets collection does not exist on the DB')
            default_database.create_collection(self.COLLECTION_NAME)

        return default_database[self.COLLECTION_NAME]

    def save_ticket(self, ticket: Dict) -> None:
        """
        Save ticket on collection tickets
        :param ticket:
        :return None:
        """
        self.logger.info(f'Saving ticket {ticket["ticketID"]}')
        complete_ticket_info = self.create_ticket_object(ticket=ticket)
        self.collection.insert_one(complete_ticket_info)

    def save_events(self, ticket_id: int, events: Dict) -> None:
        """
        Save events on ticket by ticket ID
        :param ticket_id:
        :param events:
        :return None:
        """
        self.logger.info(f'Saving events on ticket {ticket_id}')
        self.collection.update_one({"ticket_id": ticket_id}, {"$set": {'events': events, 'status': True}})

    def delete_ticket(self, ticket_id: int) -> None:
        """
        delete ticket
        :param ticket_id:
        :return:
        """
        self.logger.info(f'Deleting ticket {ticket_id} from the DB')
        self.collection.delete_one({"ticket_id": ticket_id})

    def mark_not_accessible(self, ticket_id: int) -> None:
        """
        Save events on ticket by ticket ID
        :param ticket_id:
        :param events:
        :return None:
        """
        self.logger.info(f'Marking ticket {ticket_id} as not accessible for us')
        self.collection.update_one({"ticket_id": ticket_id}, {"$set": {'access': False}})

    def get_ticket_by_id(self, ticket_id: int) -> Dict:
        """
        Get tickets by date.
        :param ticket_id:
        :return Dict:
        """
        ticket = self.collection.find_one({'ticket_id': ticket_id})

        if ticket:
            self.logger.info(f'Ticket {ticket_id} found on the DB')
        else:
            self.logger.info(f'Ticket {ticket_id} not found on the DB')

        return ticket

    def create_ticket_object(self, ticket) -> Dict:
        """
        Return an standard ticket object to save it on mongodb
        :param ticket:
        :return Dict:
        """
        return {
            'ticket_id': ticket['ticketID'],
            'details': ticket,
            'date': self.get_creation_date_from_ticket(ticket=ticket),
            'status': False,
            'access': True,
            'events': []
        }

    @staticmethod
    def get_creation_date_from_ticket(ticket) -> datetime:
        """
        Return creation date from ticket
        :param ticket:
        :return datetime:
        """
        format_ticket = '%m/%d/%Y %I:%M:%S %p'
        return datetime.strptime(ticket['createDate'], format_ticket)
