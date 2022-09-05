import asyncio
import datetime as dt
import logging
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.util import undefined
from framework.nats.client import Client
from pytz import timezone

from application.repositories.bruin_repository import BruinRepository
from application.repositories.email_tagger_repository import EmailTaggerRepository
from application.repositories.new_tickets_repository import NewTicketsRepository

log = logging.getLogger(__name__)


@dataclass
class NewTicketsMonitor:
    _event_bus: Client
    _scheduler: AsyncIOScheduler
    _config: Any
    _new_tickets_repository: NewTicketsRepository
    _email_tagger_repository: EmailTaggerRepository
    _bruin_repository: BruinRepository

    def __post_init__(self):
        self._semaphore = asyncio.BoundedSemaphore(self._config.MONITOR_CONFIG["semaphores"]["new_tickets_concurrent"])

    async def start_ticket_events_monitor(self, exec_on_start=False):
        log.info("Scheduling NewTicketsMonitor feedback job...")
        next_run_time = undefined

        if exec_on_start:
            added_seconds = dt.timedelta(0, 5)
            tz = timezone(self._config.TIMEZONE)
            next_run_time = datetime.now(tz) + added_seconds
            log.info("NewTicketsMonitor feedback job is going to be executed immediately")

        try:
            scheduler_seconds = self._config.MONITOR_CONFIG["scheduler_config"]["new_tickets_seconds"]
            self._scheduler.add_job(
                self._run_new_tickets_polling,
                "interval",
                seconds=scheduler_seconds,
                next_run_time=next_run_time,
                replace_existing=False,
                id="_run_new_tickets_polling",
            )
        except ConflictingIdError as conflict:
            log.info(f"Skipping start of NewTicketsMonitor feedback job. Reason: {conflict}")

    async def _run_new_tickets_polling(self):
        log.info("Starting NewTicketsMonitor feedback process...")

        start_time = time.time()

        log.info("Getting all new tickets...")
        new_tickets = self._new_tickets_repository.get_pending_tickets()
        log.info(f"Got {len(new_tickets)} tickets that needs processing.")

        tasks = [
            self._save_metrics(data["email"], data["ticket"])
            for data in new_tickets
            if self._new_tickets_repository.validate_ticket(data)
        ]
        await asyncio.gather(*tasks, return_exceptions=True)
        log.info("NewTicketsMonitor process finished! Took {:.3f}s".format(time.time() - start_time))

    def _check_error(self, error_code: int, ticket_id: int, email_id: str):
        if error_code == 404:
            # Increase error counter for ticket
            error_counter = self._new_tickets_repository.increase_ticket_error_counter(ticket_id, error_code)
            # If max value reached, delete ticket from storage
            if error_counter >= self._config.MONITOR_CONFIG["max_retries_error_404"]:
                self._new_tickets_repository.delete_ticket(email_id, ticket_id)
                self._new_tickets_repository.delete_ticket_error_counter(ticket_id, error_code)

    async def _save_metrics(self, email_data: dict, ticket_data: dict):
        email_id = email_data["email"]["email_id"]
        ticket_id = int(ticket_data["ticket_id"])

        async with self._semaphore:

            # Get more info from Bruin
            ticket_response = await self._bruin_repository.get_single_ticket_basic_info(ticket_id)

            if ticket_response["status"] == 404:
                self._check_error(404, ticket_id, email_id)

            if ticket_response["status"] not in range(200, 300):
                return

            log.info(f"Got ticket info from Bruin: {ticket_response}")
            # Get tag from KRE
            response = await self._email_tagger_repository.save_metrics(email_data, ticket_response["body"])
            if response["status"] not in range(200, 300):
                return

            # Remove from Email Tagger name space
            self._new_tickets_repository.mark_complete(email_id, str(ticket_id))
