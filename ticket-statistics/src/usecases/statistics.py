from datetime import date, datetime
from datetime import timedelta

from adapters.repositories.tickets.repo import TicketsRepository


class StatisticsUseCase:
    def __init__(self, logger, tickets_repository: TicketsRepository):
        """
        Creation of ticket use case object
        :param logger:
        :param tickets_repository:
        """
        self.tickets_repository = tickets_repository
        self.logger = logger

