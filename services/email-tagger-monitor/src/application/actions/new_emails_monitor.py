import asyncio
import time

from datetime import datetime

from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.util import undefined
from pytz import timezone


class NewEmailsMonitor:
    def __init__(
        self,
        event_bus,
        logger,
        scheduler,
        config,
        predicted_tag_repository,
        new_emails_repository,
        email_tagger_repository,
        bruin_repository,
    ):
        self._event_bus = event_bus
        self._logger = logger
        self._scheduler = scheduler
        self._config = config
        self._new_emails_repository = new_emails_repository
        self._predicted_tag_repository = predicted_tag_repository
        self._email_tagger_repository = email_tagger_repository
        self._bruin_repository = bruin_repository
        self._semaphore = asyncio.BoundedSemaphore(self._config.MONITOR_CONFIG["semaphores"]["new_emails_concurrent"])

    async def start_email_events_monitor(self, exec_on_start=False):
        self._logger.info("Scheduling NewEmailsMonitor feedback job...")
        next_run_time = undefined

        if exec_on_start:
            tz = timezone(self._config.TIMEZONE)
            next_run_time = datetime.now(tz)
            self._logger.info("NewEmailsMonitor feedback job is going to be executed immediately")

        try:
            scheduler_seconds = self._config.MONITOR_CONFIG["scheduler_config"]["new_emails_seconds"]
            self._scheduler.add_job(
                self._run_new_emails_polling,
                "interval",
                seconds=scheduler_seconds,
                next_run_time=next_run_time,
                replace_existing=False,
                id="_run_new_emails_polling",
            )
        except ConflictingIdError as conflict:
            self._logger.info(f"Skipping start of NewEmailsMonitor feedback job. Reason: {conflict}")

    async def _run_new_emails_polling(self):
        self._logger.info("Starting NewEmailsMonitor feedback process...")

        start_time = time.time()

        self._logger.info("Getting all new emails...")
        new_emails = self._new_emails_repository.get_pending_emails()
        self._logger.info(f"Got {len(new_emails)} emails that needs tagging.")

        tasks = [self._process_new_email(email_data) for email_data in new_emails]
        await asyncio.gather(*tasks, return_exceptions=True)
        self._logger.info("NewEmailsMonitor process finished! Took {:.3f}s".format(time.time() - start_time))

    async def _process_new_email(self, email_data: dict):
        email_id = email_data["email"]["email_id"]
        parent_id = email_data["email"].get("parent_id", None)

        async with self._semaphore:
            # Get tag from KRE
            response = await self._email_tagger_repository.get_prediction(email_data)
            prediction = response.get('body')
            self._logger.info("email_id=%s - Got prediction %s", email_id, prediction)
            if response["status"] not in range(200, 300):
                return

            if prediction is not None and len(prediction) > 0:
                self._logger.info(
                    f"Got prediction with {len(prediction)} tags from KRE [email_id='{email_id}', "
                    f"parent_id='{parent_id}'] {prediction}"
                )
                # Send tag to Bruin
                tag = self.get_most_probable_tag_id(prediction)
                response = await self._bruin_repository.post_email_tag(email_id, tag["id"])

                # NOTE: Status 409 means "Tag already present", and the email is treated as complete
                if not (response["status"] in range(200, 300) or response["status"] == 409):
                    return

            # Remove from email tagger namespace
            self._new_emails_repository.mark_complete(email_id)

            # add predicted tag to DB
            self._predicted_tag_repository.save_new_tag(email_id, tag["id"], tag["probability"])

    @staticmethod
    def get_most_probable_tag_id(prediction):
        prediction.sort(key=lambda x: x["probability"], reverse=True)
        tags = [{"id": tag["tag_id"], "probability": tag["probability"]} for tag in prediction]

        return tags[0]
