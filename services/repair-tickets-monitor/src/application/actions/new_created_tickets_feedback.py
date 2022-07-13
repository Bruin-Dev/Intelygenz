import asyncio
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List

from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.util import undefined
from framework.nats.client import Client as NatsClient
from pytz import timezone

from application.repositories.bruin_repository import BruinRepository
from application.repositories.new_created_tickets_repository import NewCreatedTicketsRepository
from application.repositories.repair_ticket_kre_repository import RepairTicketKreRepository

log = logging.getLogger(__name__)


@dataclass
class NewCreatedTicketsFeedback:
    _event_bus: NatsClient
    _scheduler: AsyncIOScheduler
    _config: Any
    _new_created_tickets_repository: NewCreatedTicketsRepository
    _rta_repository: RepairTicketKreRepository
    _bruin_repository: BruinRepository

    def __post_init__(self):
        self._semaphore = asyncio.BoundedSemaphore(
            self._config.MONITOR_CONFIG["semaphores"]["created_tickets_concurrent"]
        )

    async def start_created_ticket_feedback(self, exec_on_start=False):
        log.info("Scheduling New Created Tickets feedback job...")
        next_run_time = undefined

        if exec_on_start:
            added_seconds = timedelta(0, 5)
            tz = timezone(self._config.TIMEZONE)
            next_run_time = datetime.now(tz) + added_seconds
            log.info("NewCreatedTicketsFeedback feedback job is going to be executed immediately")

        try:
            scheduler_seconds = self._config.MONITOR_CONFIG["scheduler_config"]["new_created_tickets_feedback"]
            self._scheduler.add_job(
                self._run_created_tickets_polling,
                "interval",
                seconds=scheduler_seconds,
                next_run_time=next_run_time,
                replace_existing=False,
                id="_run_created_tickets_polling",
            )
        except ConflictingIdError as conflict:
            log.info(f"Skipping start of NewCreatedTicketsFeedback feedback job. Reason: {conflict}")

    async def _run_created_tickets_polling(self):
        log.info("Starting NewCreatedTicketsFeedback feedback process...")

        start_time = time.time()

        log.info("Getting all new tickets...")
        new_tickets = self._new_created_tickets_repository.get_pending_tickets()
        log.info(f"Got {len(new_tickets)} tickets that needs processing.")

        tasks = [self._save_created_ticket_feedback(data["email"]["email"], data["ticket"]) for data in new_tickets]
        output = await asyncio.gather(*tasks, return_exceptions=True)
        log.info(f"print output {output}")
        log.info("NewCreatedTicketsFeedback process finished! Took {:.3f}s".format(time.time() - start_time))

    def _check_error(self, error_code: int, ticket_id: int, email_id: str):
        if error_code == 404:
            # Increase error counter for ticket
            error_counter = self._new_created_tickets_repository.increase_ticket_error_counter(ticket_id, error_code)
            # If max value reached, delete ticket from storage
            if error_counter >= self._config.MONITOR_CONFIG["max_retries_error_404"]:
                self._new_created_tickets_repository.delete_ticket_error_counter(ticket_id, error_code)

    async def _save_created_ticket_feedback(self, email_data: dict, ticket_data: dict):
        email_id = email_data["email_id"]
        ticket_id = int(ticket_data["ticket_id"])
        client_id = email_data["client_id"]

        async with self._semaphore:

            # Get more info from Bruin
            ticket_response = await self._bruin_repository.get_single_ticket_info_with_service_numbers(ticket_id)

            if ticket_response["status"] == 404:
                self._check_error(404, ticket_id, email_id)

            if ticket_response["status"] not in range(200, 300):
                return

            log.info(f"Got ticket info from Bruin: {ticket_response}")
            ticket_data = ticket_response["body"]

            # Get site map
            site_map = await self._get_site_map_for_ticket(client_id, ticket_data["service_numbers"])
            if not site_map:
                log.error(f"Could not create a site map for ticket {ticket_id}")
                return

            #  Save feedback
            response = await self._rta_repository.save_created_ticket_feedback(email_data, ticket_data, site_map)
            log.info(f"Got response from kre {response}")
            if response["status"] not in range(200, 300):
                return

            # Remove from DB
            self._new_created_tickets_repository.mark_complete(email_id, ticket_id)

    async def _get_site_map_for_ticket(self, client_id: str, service_numbers: List[str]) -> Dict[str, str]:
        site_map = {}
        for service_number in service_numbers:
            response = await self._bruin_repository.verify_service_number_information(client_id, service_number)
            if response["status"] not in range(200, 300):
                continue

            site_map[service_number] = str(response["body"].get("site_id"))

        return site_map
