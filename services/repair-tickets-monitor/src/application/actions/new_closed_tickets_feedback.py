import asyncio

from datetime import datetime, timedelta

from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.util import undefined
from pytz import timezone

from typing import Any, List, Dict


class NewClosedTicketsFeedback:

    def __init__(
            self,
            event_bus,
            logger,
            scheduler,
            config,
            rta_repository,
            bruin_repository
    ):
        self._event_bus = event_bus
        self._logger = logger
        self._scheduler = scheduler
        self._config = config
        self._rta_repository = rta_repository
        self._bruin_repository = bruin_repository
        self._semaphore = asyncio.BoundedSemaphore(
            self._config.MONITOR_CONFIG['semaphores']['closed_tickets_concurrent']
        )

    async def start_closed_ticket_feedback(self, exec_on_start=False):
        self._logger.info('Scheduling New Closed Tickets feedback job...')
        next_run_time = undefined

        if exec_on_start:
            added_seconds = timedelta(0, 5)
            tz = timezone(self._config.MONITOR_CONFIG["timezone"])
            next_run_time = datetime.now(tz) + added_seconds
            self._logger.info('NewClosedTicketsFeedback feedback job is going to be executed immediately')

        try:
            scheduler_seconds = self._config.MONITOR_CONFIG['scheduler_config']['new_closed_tickets_feedback']
            self._scheduler.add_job(
                self._run_closed_tickets_polling,
                'interval',
                seconds=scheduler_seconds,
                next_run_time=next_run_time,
                replace_existing=False,
                id='_run_closed_tickets_polling'
            )
        except ConflictingIdError as conflict:
            self._logger.info(f'Skipping start of NewClosedTicketsFeedback feedback job. Reason: {conflict}')

    def _get_igz_created_tickets(self, tickets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return [ticket for ticket in tickets if ticket['created_by'] == 'Intelygenz Ai']

    async def get_closed_tickets_created_during_last_3_days(self) -> List[Dict[str, Any]]:
        creation_date_limit = datetime.utcnow() - timedelta(days=3)
        response = await self._bruin_repository.get_closed_tickets_with_creation_date_limit(creation_date_limit)
        if response['status'] not in range(200, 300):
            self._logger.error('Error while getting bruin closed tickets')
            return []

        return response['body']

    async def _run_closed_tickets_polling(self):
        self._logger.info('Starting NewClosedTicketsFeedback feedback process...')
        closed_tickets = await self.get_closed_tickets_created_during_last_3_days()
        igz_tickets = self._get_igz_created_tickets(closed_tickets)
        self._logger.info(f'Got igz closed tickets: {len(igz_tickets)}')
        tasks = [self._save_closed_ticket_feedback(ticket) for ticket in igz_tickets]
        await asyncio.gather(*tasks)

    async def _save_closed_ticket_feedback(self, ticket_data: dict):
        ticket_id = ticket_data['ticket_id']
        client_id = ticket_data['client_id']

        async with self._semaphore:
            status_response = await self._bruin_repository.get_status_and_cancellation_reasons(ticket_id)
            if status_response['status'] not in range(200, 300):
                self._logger.error(f"Error while while getting ticket status for {ticket_id}")
                return

            save_closed_ticket_response = await self._rta_repository.save_closed_ticket_feedback(
                ticket_id,
                client_id,
                status_response['body']['ticket_status'],
                status_response['body']['cancellation_reasons']
            )
            if save_closed_ticket_response['status'] not in range(200, 300):
                self._logger.error(f"Error while saving closed ticket feedback for {ticket_id}")
                return

            return
