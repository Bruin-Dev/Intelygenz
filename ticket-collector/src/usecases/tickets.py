from datetime import date, datetime
from datetime import timedelta

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
    def date_range(start_date: datetime, end_date: datetime):
        """
        Get date range
        :param start_date:
        :param end_date:
        :return:
        """
        for n in range(int((end_date - start_date).days)):
            yield start_date + timedelta(n)

    def get_data(self) -> None:
        """
        Main function to get data from bruin or database
        """
        self.logger.info('Start getting data')
        # days_per_year = 365.24
        days_per_year = 2
        days_to_update = 1

        today = datetime.today()
        range_date_to_force_update = today - timedelta(days=days_to_update)
        year_ago = today - timedelta(days=days_per_year)

        self.logger.info(f'Getting tickets data between {year_ago} and {today}')

        for single_date in self.date_range(start_date=year_ago, end_date=today):
            update_this_date = self.check_if_it_must_be_updated(start=range_date_to_force_update,
                                                                end=today,
                                                                requested_date=single_date)

            self.get_data_from_bruin(query_date=single_date, update=update_this_date)

    def check_if_it_must_be_updated(self, start: datetime, end: datetime, requested_date: datetime) -> bool:
        """
        Check on database if we have tickets there
        :param start:
        :param end:
        :param requested_date:
        :return:
        """
        if start.date() <= requested_date.date() <= end.date():
            self.logger.info(f'Date {requested_date} is between {start} and {end}')
            return True
        self.logger.info(f'Date {requested_date} is not between {start} and {end}')
        return False

    def get_data_from_bruin(self, query_date: datetime, update: bool) -> None:
        """
        Get data from bruin
        :param query_date:
        :param update:
        """
        query_start = query_date.replace(hour=0, minute=0, second=0).strftime("%Y-%m-%dT%H:%M:%SZ")
        query_end = query_date.replace(hour=23, minute=59, second=59).strftime("%Y-%m-%dT%H:%M:%SZ")

        tickets = self.bruin_repository.request_tickets_by_date_range(start=query_start, end=query_end)

        for key, ticket in enumerate(tickets):
            ticket_on_mongo = self.tickets_repository.get_ticket_by_id(ticket_id=ticket["ticketID"])

            if ticket_on_mongo is None or update is True:
                if update is True:
                    self.logger.info(f'Ticket {ticket["ticketID"]} in range to be updated (Deleting it first)')
                    self.tickets_repository.delete_ticket(ticket_id=ticket["ticketID"])
                self.tickets_repository.save_ticket(ticket=ticket)

        for key, ticket in enumerate(tickets):
            try:
                events = self.bruin_repository.request_ticket_events(ticket_id=ticket['ticketID'])

                if events:
                    self.tickets_repository.save_events(ticket_id=ticket["ticketID"], events=events)
                else:
                    self.logger.info(f'We don\'t have access to {ticket["ticketID"]}')
                    self.tickets_repository.mark_not_accessible(ticket_id=ticket['ticketID'])
            except Exception as e:
                self.logger.info(f'Error: {e}')
