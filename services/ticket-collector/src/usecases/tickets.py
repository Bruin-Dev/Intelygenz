from datetime import date, timedelta

from adapters.repositories.bruin.repo import BruinRepository
from adapters.repositories.tickets.repo import TicketsRepository


class TicketUseCase:
    def __init__(self, logger, bruin_repository: BruinRepository, tickets_repository: TicketsRepository):
        """
        Creation of ticket use case object
        :param logger:
        :param bruin_repository:
        :param tickets_repository:
        """
        self.bruin_repository = bruin_repository
        self.tickets_repository = tickets_repository
        self.logger = logger

    @staticmethod
    def date_range(start_date: date, end_date: date):
        """
        Get date range
        :param start_date:
        :param end_date:
        :return:
        """
        days = (end_date - start_date).days
        return [start_date + timedelta(day) for day in range(days)]

    def get_data(self) -> None:
        """
        Main function to get data from bruin or database
        """
        self.logger.info('Start getting data')
        days_to_retrieve = 14
        days_to_update = 3

        today = date.today()
        update_start_date = today - timedelta(days=days_to_update)
        retrieve_start_date = today - timedelta(days=days_to_retrieve)

        self.logger.info(f'Getting tickets data between {retrieve_start_date} and {today}')

        for _date in self.date_range(start_date=retrieve_start_date, end_date=today):
            update = self.check_if_it_must_be_updated(start=update_start_date, end=today, requested_date=_date)
            self.get_data_from_bruin(query_date=_date, update=update)

    def check_if_it_must_be_updated(self, start: date, end: date, requested_date: date) -> bool:
        """
        Check on database if we have tickets there
        :param start:
        :param end:
        :param requested_date:
        :return:
        """
        must_be_updated = start <= requested_date <= end

        if must_be_updated:
            self.logger.info(f'Date {requested_date} is between {start} and {end}')
        else:
            self.logger.info(f'Date {requested_date} is not between {start} and {end}')

        return must_be_updated

    def get_data_from_bruin(self, query_date: date, update: bool) -> None:
        """
        Get data from bruin
        :param query_date:
        :param update:
        """
        query_start = query_date.strftime('%Y-%m-%dT00:00:00Z')
        query_end = query_date.strftime('%Y-%m-%dT23:59:59Z')

        tickets = self.bruin_repository.request_tickets_by_date_range(start=query_start, end=query_end)

        for key, ticket in enumerate(tickets):
            ticket_on_mongo = self.tickets_repository.get_ticket_by_id(ticket_id=ticket["ticketID"])

            if ticket_on_mongo is None or update is True:
                if update is True:
                    self.logger.info(f"Ticket {ticket['ticketID']} in range to be updated (Deleting it first)")
                    self.tickets_repository.delete_ticket(ticket_id=ticket['ticketID'])
                self.tickets_repository.save_ticket(ticket=ticket)

        for key, ticket in enumerate(tickets):
            try:
                events = self.bruin_repository.request_ticket_events(ticket_id=ticket['ticketID'])

                if events:
                    self.tickets_repository.save_events(ticket_id=ticket['ticketID'], events=events)
                else:
                    self.logger.info(f"We don't have access to {ticket['ticketID']}")
                    self.tickets_repository.mark_not_accessible(ticket_id=ticket['ticketID'])
            except Exception as e:
                self.logger.info(f'Error: {e}')
