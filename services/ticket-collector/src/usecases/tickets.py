from datetime import date, timedelta

from adapters.repositories.bruin.repo import BruinRepository
from adapters.repositories.tickets.repo import TicketsRepository


class TicketUseCase:
    def __init__(self, config, logger, bruin_repository: BruinRepository, tickets_repository: TicketsRepository):
        """
        Creation of ticket use case object
        :param logger:
        :param bruin_repository:
        :param tickets_repository:
        """
        self.bruin_repository = bruin_repository
        self.tickets_repository = tickets_repository
        self.config = config
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
        today = date.today()
        start_date = today - timedelta(days=self.config['days_to_retrieve'])

        self.logger.info(f'Getting tickets data between {start_date} and {today}')

        for _date in self.date_range(start_date=start_date, end_date=today):
            update = self.should_update(_date=_date)
            self.get_data_from_bruin(query_date=_date, update=update)

        self.logger.info(f'Finished getting tickets between {start_date} and {today}')

    def should_update(self, _date: date) -> bool:
        """
        Check if tickets from the given date should be updated
        :param _date:
        :return:
        """
        days = (date.today() - _date).days
        update = days <= self.config['days_to_update']

        if update:
            self.logger.info(f'Date {_date} should be updated')
        else:
            self.logger.info(f'Date {_date} should not be updated')

        return update

    def get_data_from_bruin(self, query_date: date, update: bool) -> None:
        """
        Get data from bruin
        :param query_date:
        :param update:
        """
        try:
            query_start = query_date.strftime('%Y-%m-%dT00:00:00Z')
            query_end = query_date.strftime('%Y-%m-%dT23:59:59Z')

            tickets = self.bruin_repository.request_tickets_by_date_range(start=query_start, end=query_end)

            for ticket in tickets:
                ticket_id = ticket['ticketID']
                ticket_on_mongo = self.tickets_repository.get_ticket_by_id(ticket_id=ticket_id)
                events_on_mongo = self.tickets_repository.get_ticket_events(ticket_id=ticket_id, ticket=ticket_on_mongo)

                if update:
                    self.tickets_repository.delete_ticket(ticket_id=ticket_id)

                if update or not ticket_on_mongo:
                    self.tickets_repository.save_ticket(ticket=ticket)

                if update or not events_on_mongo:
                    self.save_ticket_events(ticket_id)
        except Exception as e:
            self.logger.error(e)

    def save_ticket_events(self, ticket_id: int) -> None:
        try:
            events = self.bruin_repository.request_ticket_events(ticket_id=ticket_id)

            if events:
                self.tickets_repository.save_events(ticket_id=ticket_id, events=events)
            else:
                self.logger.info(f"We don't have access to ticket {ticket_id}")
                self.tickets_repository.mark_not_accessible(ticket_id=ticket_id)
        except Exception as e:
            self.logger.error(e)
