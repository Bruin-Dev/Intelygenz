import asyncio
import time

from typing import Tuple, Iterator

from datetime import datetime

from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.util import undefined
from pytz import timezone


class RepairTicketsMonitor:
    def __init__(
        self,
        event_bus,
        logger,
        scheduler,
        config,
        new_tagged_emails_repository,
        repair_tickets_kre_repository,
    ):
        self._event_bus = event_bus
        self._logger = logger
        self._scheduler = scheduler
        self._config = config
        self._new_tagged_emails_repository = new_tagged_emails_repository
        self._repair_tickets_kre_repository = repair_tickets_kre_repository

        self._semaphore = asyncio.BoundedSemaphore(
            self._config.MONITOR_CONFIG["semaphores"]["repair_tickets_concurrent"]
        )

    async def start_repair_tickets_monitor(self, exec_on_start: bool = False):
        self._logger.info("Scheduling RepairTicketsMonitor job...")
        next_run_time = undefined

        if exec_on_start:
            tz = timezone(self._config.MONITOR_CONFIG["timezone"])
            next_run_time = datetime.now(tz)
            self._logger.info(
                "RepairTicketsMonitor job is going to be executed immediately"
            )

        try:
            scheduler_seconds = self._config.MONITOR_CONFIG["scheduler_config"]["repair_ticket_monitor"]
            self._scheduler.add_job(
                self._run_repair_tickets_polling,
                "interval",
                seconds=scheduler_seconds,
                next_run_time=next_run_time,
                replace_existing=False,
                id="_run_repair_tickets_polling",
            )
        except ConflictingIdError as conflict:
            self._logger.info(
                f"Skipping start of repair tickets monitor job. Reason: {conflict}"
            )

    async def _run_repair_tickets_polling(self):
        self._logger.info("Starting RepairTicketsMonitor process...")

        start_time = time.time()

        self._logger.info("Getting all tagged emails...")
        tagged_emails = self._new_tagged_emails_repository.get_tagged_pending_emails()
        repair_emails, other_tags_emails = self._triage_emails_by_tag(tagged_emails)
        self._logger.info(f"Got {len(tagged_emails)} tagged emails of those where {repair_emails} repair emails.")

        other_tags_tasks = [self._process_other_tags_email(email_data) for email_data in repair_emails]
        repair_tasks = [self._process_repair_email(email_data) for email_data in repair_emails]
        tasks = repair_tasks + other_tags_tasks

        output = await asyncio.gather(*tasks, return_exceptions=True)
        self._logger.info(
            "RepairTicketsMonitor process finished! Took {:.3f}s".format(
                time.time() - start_time
            )
        )
        self._logger.info(f"Output: {output}")

    def _triage_emails_by_tag(self, tagged_emails) -> Tuple[Iterator, Iterator]:
        repair_tag_id = self._config.MONITOR_CONFIG["tag_ids"]["Repair"]
        repair_emails = filter(lambda x: x['tag_id'] == repair_tag_id, tagged_emails)
        other_tags_emails = filter(lambda x: x['tag_id'] != repair_tag_id, tagged_emails)

        return repair_emails, other_tags_emails

    async def _get_inference(self, email_data):
        prediction_response = await self._repair_tickets_kre_repository.get_email_inference(
            email_data
        )
        if prediction_response["status"] not in range(200, 300):
            self._logger.info(
                f"Error predicion response status code {prediction_response['status']}"
            )
            return
        return prediction_response.get("body")

    async def _process_other_tags_email(self, email):
        self._new_tagged_emails_repository.mark_complete(email['email_id'])

    async def _process_repair_email(self, email: dict):
        # TODO: Things left to do
        # Validate information
        # Bucket into site_ids
        # Diff between validate vs ticket creation
        # Diff voo/vas
        # save_outputs to kre
        # Remove emails from redis
        email_id = email["email_id"]
        email_data = self._new_tagged_emails_repository.get_email_details(email_id)
        self._logger.info(f"Running Repair Email Process for email_id: {email_id}")

        async with self._semaphore:
            prediction = await self._get_inference(email_data)
