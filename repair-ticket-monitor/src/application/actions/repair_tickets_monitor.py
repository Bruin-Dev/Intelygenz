import asyncio
import time

from datetime import datetime

from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.util import undefined
from pytz import timezone


class RepairTicketsMonitor:
    def __init__(self, event_bus, logger, scheduler, config, repair_tickets_repository,
                 repair_tickets_kre_repository, bruin_repository):
        self._event_bus = event_bus
        self._logger = logger
        self._scheduler = scheduler
        self._config = config
        self._repair_tickets_repository = repair_tickets_repository
        self._repair_tickets_kre_repository = repair_tickets_kre_repository

        self._bruin_repository = bruin_repository
        self._semaphore = asyncio.BoundedSemaphore(
            self._config.MONITOR_CONFIG['semaphores']['repair_tickets_concurrent'])

    async def start_repair_tickets_monitor(self, exec_on_start=False):
        self._logger.info('Scheduling RepairTicketsMonitor feedback job...')
        next_run_time = undefined

        if exec_on_start:
            tz = timezone(self._config.MONITOR_CONFIG["timezone"])
            next_run_time = datetime.now(tz)
            self._logger.info('NewEmailsMonitor feedback job is going to be executed immediately')

        try:
            scheduler_seconds = self._config.MONITOR_CONFIG['scheduler_config']['new_emails_seconds']
            self._scheduler.add_job(self._run_repair_tickets_polling, 'interval', seconds=scheduler_seconds,
                                    next_run_time=next_run_time, replace_existing=False,
                                    id='_run_repair_tickets_polling')
        except ConflictingIdError as conflict:
            self._logger.info(f'Skipping start of NewEmailsMonitor feedback job. Reason: {conflict}')

    async def _run_repair_tickets_polling(self):
        self._logger.info('Starting RepairTicketsMonitor feedback process...')

        start_time = time.time()

        self._logger.info('Getting all repair emails...')
        repair_emails = self._repair_tickets_repository.get_pending_repair_emails()
        self._logger.info(f'Got {len(repair_emails)} repair emails.')

        tasks = [
            self._process_repair_email(email_data)
            for email_data in repair_emails
        ]
        await asyncio.gather(*tasks, return_exceptions=True)
        self._logger.info("RepairTicketsMonitor process finished! Took {:.3f}s".format(time.time() - start_time))

    async def _process_repair_email(self, email_data: dict):
        # TODO: define the new logic
        email_id = email_data["email"]["email_id"]
        parent_id = email_data["email"].get("parent_id", None)

        async with self._semaphore:
            # Get tag from KRE
            # response = await self._repair_tickets_kre_repository.get_prediction(email_data)
            # TODO: change
            response = {}
            prediction = response.get('body')
            if response["status"] not in range(200, 300):
                return

            if prediction is not None and len(prediction) > 0:
                self._logger.info(
                    f"Got prediction with {len(prediction)} tags from KRE [email_id='{email_id}', "
                    f"parent_id='{parent_id}'] {prediction}"
                )
                # Send tag to Bruin
                # response = await self._bruin_repository.post_email_tag(email_id, tag_id)
                # TODO: change
                response = {}

                # NOTE: Status 409 means "Tag already present", and the email is treated as complete
                if not (response["status"] in range(200, 300) or response["status"] == 409):
                    return

            # Remove from DB
            # self._repair_tickets_repository.mark_complete(email_id)
