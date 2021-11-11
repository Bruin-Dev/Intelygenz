import asyncio
import time

from datetime import datetime
from typing import Set

from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.util import undefined
from pytz import timezone
from tenacity import retry, wait_exponential, stop_after_delay


class TNBAFeedback:
    def __init__(self, event_bus, logger, scheduler, config, t7_repository, customer_cache_repository,
                 bruin_repository, notifications_repository, redis_client):
        self._event_bus = event_bus
        self._logger = logger
        self._scheduler = scheduler
        self._config = config
        self._t7_repository = t7_repository
        self._customer_cache_repository = customer_cache_repository
        self._bruin_repository = bruin_repository
        self._notifications_repository = notifications_repository
        self._redis_client = redis_client
        self._semaphore = asyncio.BoundedSemaphore(self._config.TNBA_FEEDBACK_CONFIG['semaphore'])

    async def start_tnba_automated_process(self, exec_on_start=False):
        self._logger.info('Scheduling TNBA feedback job...')
        next_run_time = undefined

        if exec_on_start:
            tz = timezone(self._config.TNBA_FEEDBACK_CONFIG["timezone"])
            next_run_time = datetime.now(tz)
            self._logger.info('TNBA feedback job is going to be executed immediately')

        try:
            self._scheduler.add_job(self._run_tickets_polling, 'interval',
                                    seconds=self._config.MONITORING_INTERVAL_SECONDS,
                                    next_run_time=next_run_time, replace_existing=False,
                                    id='_run_tickets_polling')
        except ConflictingIdError as conflict:
            self._logger.info(f'Skipping start of TNBA feedback job. Reason: {conflict}')

    async def _run_tickets_polling(self):
        self._logger.info('Starting TNBA feedback process...')

        start_time = time.time()

        self._logger.info('Getting all closed tickets for all customers...')
        closed_ticket_ids = await self._get_all_closed_tickets_for_monitored_companies()
        self._logger.info(
            f'Got {len(closed_ticket_ids)} closed ticket ids for all customers. '
            f'Going through them to find TNBA notes and sending metrics back to T7')

        tasks = [
            self._send_ticket_task_history_to_t7(ticket_id)
            for ticket_id in closed_ticket_ids
        ]
        await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()
        self._logger.info(f'TNBA feedback process finished! Took {(end_time - start_time) // 60} minutes.')

    async def _get_all_closed_tickets_for_monitored_companies(self):
        closed_ticket_ids = []

        customer_cache_response = await self._customer_cache_repository.get_cache_for_feedback_process()
        customer_cache_response_status = customer_cache_response['status']
        if customer_cache_response_status not in range(200, 300) or customer_cache_response_status == 202:
            return []

        customer_cache: list = customer_cache_response['body']
        bruin_clients_ids: Set[int] = set(elem['bruin_client_info']['client_id'] for elem in customer_cache)

        tasks = [
            self._get_closed_tickets_by_client_id(client_id, closed_ticket_ids)
            for client_id in bruin_clients_ids
        ]
        await asyncio.gather(*tasks, return_exceptions=True)

        return closed_ticket_ids

    async def _get_closed_tickets_by_client_id(self, client_id, closed_ticket_ids):
        @retry(wait=wait_exponential(multiplier=self._config.NATS_CONFIG['multiplier'],
                                     min=self._config.NATS_CONFIG['min']),
               stop=stop_after_delay(self._config.NATS_CONFIG['stop_delay']))
        async def get_closed_tickets_with_task_history_by_client_id():
            async with self._semaphore:
                closed_outage_tickets_response = await self._bruin_repository.get_outage_tickets(client_id)
                closed_outage_tickets_response_body = closed_outage_tickets_response['body']
                closed_outage_tickets_response_status = closed_outage_tickets_response['status']
                if closed_outage_tickets_response_status not in range(200, 300):
                    closed_outage_tickets_response_body = []

                closed_affecting_tickets_response = await self._bruin_repository.get_affecting_tickets(client_id)
                closed_affecting_tickets_response_body = closed_affecting_tickets_response['body']
                closed_affecting_tickets_response_status = closed_affecting_tickets_response['status']
                if closed_affecting_tickets_response_status not in range(200, 300):
                    closed_affecting_tickets_response_body = []

                all_closed_tickets: list = closed_outage_tickets_response_body + closed_affecting_tickets_response_body
                closed_tickets_ids = (ticket['ticketID'] for ticket in all_closed_tickets)
                for ticket_id in closed_tickets_ids:
                    closed_ticket_ids.append(ticket_id)

        try:
            await get_closed_tickets_with_task_history_by_client_id()
        except Exception as e:
            self._logger.error(
                f"An error occurred while trying to getting all closed tickets for Bruin client {client_id} -> {e}"
            )

    async def _send_ticket_task_history_to_t7(self, ticket_id):
        @retry(wait=wait_exponential(multiplier=self._config.NATS_CONFIG['multiplier'],
                                     min=self._config.NATS_CONFIG['min']),
               stop=stop_after_delay(self._config.NATS_CONFIG['stop_delay']))
        async def send_ticket_task_history_to_t7():
            async with self._semaphore:
                redis_key = f'{self._config.ENVIRONMENT_NAME}-{ticket_id}'

                ticket_task_history = await self._bruin_repository.get_ticket_task_history(ticket_id)
                ticket_task_history_body: list = ticket_task_history["body"]
                ticket_task_history_status = ticket_task_history["status"]
                if ticket_task_history_status not in range(200, 300):
                    self._logger.info(f"Ticket task status returned {ticket_task_history_status}"
                                      f" and task history body returned {ticket_task_history_body}")
                    return

                ticket_task_history_tnba_check = self._t7_repository.tnba_note_in_task_history(ticket_task_history_body)
                if ticket_task_history_tnba_check is False:
                    self._logger.info(f"No TNBA note found in task history of ticket id {ticket_id}. Skipping ...")
                    return

                any_ticket_row_has_asset = any(row.get('Asset') for row in ticket_task_history_body)
                if any_ticket_row_has_asset is False:
                    self._logger.info(f"No asset in history of ticket id {ticket_id}. Skipping ...")
                    return

                if self._redis_client.get(redis_key) is not None:
                    self._logger.info(f"Task history of ticket id {ticket_id} has already been sent to T7. "
                                      f"Skipping ...")
                    return

                self._logger.info(f"TNBA note found in task history of ticket id {ticket_id}")
                self._logger.info("Sending data to T7")

                post_metrics = await self._t7_repository.post_metrics(ticket_id, ticket_task_history_body)
                post_metrics_body = post_metrics["body"]
                post_metrics_status = post_metrics["status"]

                if post_metrics_status not in range(200, 300):
                    self._logger.info(f"Posting metrics to T7 status returned {post_metrics_status}"
                                      f" and posting metrics to T7 body returned {post_metrics_body}")
                    return

                self._redis_client.set(redis_key, '', ex=self._config.TNBA_FEEDBACK_CONFIG['redis_ttl'])

        try:
            await send_ticket_task_history_to_t7()
        except Exception as e:
            self._logger.error(
                f"An error occurred while trying to send ticket:{ticket_id} task history to T7 -> {e}"
            )
