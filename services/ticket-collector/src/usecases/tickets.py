import asyncio
import time
from datetime import date, timedelta
from typing import List

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
        self.semaphore = asyncio.BoundedSemaphore(self.config['concurrent_days'])
        self.perf_counters = {}

    def _start_perf_counter(self, counter):
        self.perf_counters[counter] = time.perf_counter()

    def _stop_perf_counter(self, counter):
        elapsed_time = time.perf_counter() - self.perf_counters[counter]
        self.perf_counters.pop(counter)
        self.logger.debug(f'{counter} took {self._humanize_time(elapsed_time)}')

    @staticmethod
    def _humanize_time(t):
        if t < 1:
            unit = 'ms'
            t = t * 1000
        elif t < 60:
            unit = 's'
        elif t < 3600:
            unit = 'm'
            t = t / 60
        else:
            unit = 'h'
            t = t / 3600
        return f'{round(t, 2)}{unit}'

    @staticmethod
    def date_range(start_date: date, end_date: date) -> List[date]:
        """
        Get date range
        :param start_date:
        :param end_date:
        :return:
        """
        days = (end_date - start_date).days
        return [start_date + timedelta(day) for day in range(days)]

    async def get_data(self) -> None:
        """
        Main function to get data from bruin or database
        """
        today = date.today()
        start_date = today - timedelta(days=self.config['days_to_retrieve'])
        date_range = self.date_range(start_date=start_date, end_date=today)

        self.logger.info(f'Getting tickets between {start_date} and {today}')
        start_time = time.perf_counter()

        tasks = [self.get_data_from_bruin(_date=_date, today=today) for _date in date_range]
        await asyncio.gather(*tasks)

        end_time = time.perf_counter()
        elapsed_time = round((end_time - start_time) / 60, 2)
        self.logger.info(f'Finished getting tickets between {start_date} and {today} in {elapsed_time}m')

    def should_update(self, _date: date, today: date) -> bool:
        """
        Check if tickets from the given date should be updated
        :param _date:
        :param today:
        :return:
        """
        days = (today - _date).days
        update = days <= self.config['days_to_update']

        if update:
            self.logger.info(f'Date {_date} should be updated')
        else:
            self.logger.info(f'Date {_date} should not be updated')

        return update

    async def get_data_from_bruin(self, _date: date, today: date) -> None:
        """
        Get data from bruin
        :param _date:
        :param today:
        """
        async with self.semaphore:
            start = _date.strftime('%Y-%m-%dT00:00:00Z')
            end = _date.strftime('%Y-%m-%dT23:59:59Z')

            self._start_perf_counter('get_tickets_from_bruin')
            tickets = await self.bruin_repository.request_tickets_by_date_range(start=start, end=end)
            self._stop_perf_counter('get_tickets_from_bruin')
            update = self.should_update(_date=_date, today=today)

            for ticket in tickets:
                ticket_id = ticket['ticketID']
                self._start_perf_counter('get_ticket_from_mongodb')
                ticket_on_mongo = self.tickets_repository.get_ticket_by_id(ticket_id=ticket_id)
                self._stop_perf_counter('get_ticket_from_mongodb')

                if update:
                    self._start_perf_counter('delete_ticket_from_mongodb')
                    self.tickets_repository.delete_ticket(ticket_id=ticket_id)
                    self._stop_perf_counter('delete_ticket_from_mongodb')

                if update or not ticket_on_mongo:
                    self._start_perf_counter('save_ticket_on_mongodb')
                    self.tickets_repository.save_ticket(ticket=ticket)
                    self._stop_perf_counter('save_ticket_on_mongodb')

                await self.save_ticket_events(ticket_id)

            self.logger.info(f'Finished getting tickets from {_date}')

    async def save_ticket_events(self, ticket_id: int) -> None:
        self._start_perf_counter('get_ticket_events_from_bruin')
        events = await self.bruin_repository.request_ticket_events(ticket_id=ticket_id)
        self._stop_perf_counter('get_ticket_events_from_bruin')

        if events:
            self._start_perf_counter('save_ticket_events_on_mongodb')
            self.tickets_repository.save_events(ticket_id=ticket_id, events=events)
            self._stop_perf_counter('save_ticket_events_on_mongodb')
        else:
            self.logger.info(f"We don't have access to ticket {ticket_id}")
            self._start_perf_counter('mark_ticket_not_accessible_on_mongodb')
            self.tickets_repository.mark_not_accessible(ticket_id=ticket_id)
            self._stop_perf_counter('mark_ticket_not_accessible_on_mongodb')
