import asyncio
import time

from datetime import datetime

from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.util import undefined
from pytz import timezone


class NewTicketsMonitor:
    def __init__(self, event_bus, logger, scheduler, config, new_tickets_repository, email_tagger_repository,
                 bruin_repository):
        self._event_bus = event_bus
        self._logger = logger
        self._scheduler = scheduler
        self._config = config
        self._new_tickets_repository = new_tickets_repository
        self._email_tagger_repository = email_tagger_repository
        self._bruin_repository = bruin_repository
        self._semaphore = asyncio.BoundedSemaphore(self._config.MONITOR_CONFIG['semaphores']['new_tickets_concurrent'])

    async def start_ticket_events_monitor(self, exec_on_start=False):
        self._logger.info('Scheduling NewTicketsMonitor feedback job...')
        next_run_time = undefined

        if exec_on_start:
            tz = timezone(self._config.MONITOR_CONFIG["timezone"])
            next_run_time = datetime.now(tz)
            self._logger.info('NewTicketsMonitor feedback job is going to be executed immediately')

        try:
            scheduler_seconds = self._config.MONITOR_CONFIG['scheduler_config']['new_tickets_seconds']
            self._scheduler.add_job(self._run_new_tickets_polling, 'interval',
                                    seconds=scheduler_seconds,
                                    next_run_time=next_run_time, replace_existing=False,
                                    id='_run_new_tickets_polling')
        except ConflictingIdError as conflict:
            self._logger.info(f'Skipping start of NewTicketsMonitor feedback job. Reason: {conflict}')

    async def _run_new_tickets_polling(self):
        self._logger.info('Starting NewTicketsMonitor feedback process...')

        start_time = time.time()

        self._logger.info('Getting all new tickets...')
        new_tickets = self._new_tickets_repository.get_pending_tickets()
        self._logger.info(f'Got {len(new_tickets)} tickets that needs processing.')

        tasks = [
            self._save_metrics(data['email'], data['ticket'])
            for data in new_tickets
            if self._new_tickets_repository.validate_ticket(data)
        ]
        await asyncio.gather(*tasks, return_exceptions=True)
        self._logger.info("NewTicketsMonitor process finished! Took {:.3f}s".format(time.time() - start_time))

    async def _save_metrics(self, email_data: dict, ticket_data: dict):
        email_id = email_data["email"]["email_id"]
        ticket_id = int(ticket_data["ticket_id"])

        async with self._semaphore:

            # Get more info from Bruin
            ticket_response = await self._bruin_repository.get_single_ticket_basic_info(ticket_id)

            if ticket_response["status"] not in range(200, 300):
                return

            self._logger.info(f"Got ticket info from Bruin: {ticket_response}")
            # Get tag from KRE
            response = await self._email_tagger_repository.save_metrics(email_data, ticket_response['body'])
            if response["status"] not in range(200, 300):
                return

            # Remove from DB
            self._new_tickets_repository.mark_complete(email_id, ticket_id)
