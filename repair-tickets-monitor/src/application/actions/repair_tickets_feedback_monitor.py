import asyncio
import time

from datetime import datetime

from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.util import undefined
from pytz import timezone


class RepairTicketsFeedbackMonitor:
    def __init__(self, event_bus, logger, scheduler, config, repair_tickets_repository, repair_tickets_kre_repository):
        self._event_bus = event_bus
        self._logger = logger
        self._scheduler = scheduler
        self._config = config
        self._repair_tickets_repository = repair_tickets_repository
        self._repair_tickets_kre_repository = repair_tickets_kre_repository

        self._semaphore = asyncio.BoundedSemaphore(
            self._config.MONITOR_CONFIG['semaphores']['repair_tickets_concurrent'])

    async def start_repair_tickets_feedback_monitor(self, exec_on_start=False):
        self._logger.info('Scheduling RepairTicketsMonitor feedback job...')
        next_run_time = undefined

        if exec_on_start:
            tz = timezone(self._config.MONITOR_CONFIG["timezone"])
            next_run_time = datetime.now(tz)
            self._logger.info('RepairTicketsFeedbackMonitor feedback job is going to be executed immediately')

        try:
            # TODO: change to do it once per day
            scheduler_seconds = self._config.MONITOR_CONFIG['scheduler_config']['repair_ticket_feedback_seconds']
            self._scheduler.add_job(self._run_repair_tickets_feedback_polling, 'interval', seconds=scheduler_seconds,
                                    next_run_time=next_run_time, replace_existing=False,
                                    id='_run_repair_tickets_feedback_polling')
        except ConflictingIdError as conflict:
            self._logger.info(f'Skipping start of repair tickets feedback monitor job. Reason: {conflict}')

    async def _run_repair_tickets_feedback_polling(self):
        self._logger.info('Starting RepairTicketsFeedbackMonitor feedback process...')

        start_time = time.time()

        self._logger.info('Getting all repair emails for feedback...')
        feedback_emails = self._repair_tickets_repository.get_feedback_emails()
        self._logger.info(f'Got {len(feedback_emails)} feedbacks.')

        tasks = [
            self._process_repair_email(email_data)
            for email_data in feedback_emails
        ]
        await asyncio.gather(*tasks, return_exceptions=True)
        self._logger.info("RepairTicketsFeedbackMonitor process finished! Took {:.3f}s".format(time.time()
                          - start_time))

    async def _process_repair_email(self, email_data: dict):
        # TODO: define the new logic
        email_id = email_data["email"]["email_id"]
        client_id = email_data["email"]["client_id"]
        parent_id = email_data["email"].get("parent_id", None)
        tag = email_data["tag"]
        tag_mock = {'tag_id': 0, 'confidence': 1.0}

        async with self._semaphore:
            prediction_response = await self._repair_tickets_kre_repository.get_prediction(email_data, tag)

            # TODO
            pass
