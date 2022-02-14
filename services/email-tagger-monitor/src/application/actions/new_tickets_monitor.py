import asyncio
import time
import datetime as dt

from datetime import datetime

from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.util import undefined
from pytz import timezone


class NewTicketsMonitor:
    def __init__(
        self, event_bus, logger, scheduler, config, new_tickets_repository, email_tagger_repository, bruin_repository
    ):
        self._event_bus = event_bus
        self._logger = logger
        self._scheduler = scheduler
        self._config = config
        self._new_tickets_repository = new_tickets_repository
        self._email_tagger_repository = email_tagger_repository
        self._bruin_repository = bruin_repository
        self._semaphore = asyncio.BoundedSemaphore(self._config.MONITOR_CONFIG["semaphores"]["new_tickets_concurrent"])

    async def start_ticket_events_monitor(self, exec_on_start=False):
        self._logger.info("Scheduling NewTicketsMonitor feedback job...")
        next_run_time = undefined

        if exec_on_start:
            added_seconds = dt.timedelta(0, 5)
            tz = timezone(self._config.TIMEZONE)
            next_run_time = datetime.now(tz) + added_seconds
            self._logger.info("NewTicketsMonitor feedback job is going to be executed immediately")

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
            self._logger.info(f"Skipping start of NewTicketsMonitor feedback job. Reason: {conflict}")

    async def _run_new_tickets_polling(self):
        self._logger.info("Starting NewTicketsMonitor feedback process...")

        start_time = time.time()

        self._logger.info("Getting all new tickets...")
        new_tickets = self._new_tickets_repository.get_pending_tickets()
        self._logger.info(f"Got {len(new_tickets)} tickets that needs processing.")

        tasks = [
            self._save_metrics(data["email"], data["ticket"])
            for data in new_tickets
            if self._new_tickets_repository.validate_ticket(data)
        ]
        # TODO: We have no visibility over this taks results. Errors happend and we will not receive anything
        # TODO: when some errors occur we are breaking the task loop and it no running anymore until restarting the service
        await asyncio.gather(*tasks, return_exceptions=True)
        self._logger.info("NewTicketsMonitor process finished! Took {:.3f}s".format(time.time() - start_time))

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
        self._logger.info(f"2 - Running save metric: {email_id} - {ticket_id}")

        async with self._semaphore:
            self._logger.info("Go in to sem")
            # Get more info from Bruin
            ticket_response = await self._bruin_repository.get_single_ticket_basic_info(ticket_id)
            self._logger.info(f"Ticket response: {ticket_response}")

            if ticket_response["status"] == 404:
                self._check_error(404, ticket_id, email_id)

            if ticket_response["status"] not in range(200, 300):
                return

            self._logger.info(f"Got ticket info from Bruin: {ticket_response}")
            # Get tag from KRE
            response = await self._email_tagger_repository.save_metrics(email_data, ticket_response["body"])
            if response["status"] not in range(200, 300):
                return

            # Remove from Email Tagger name space
            self._new_tickets_repository.mark_complete(email_id, ticket_id)
