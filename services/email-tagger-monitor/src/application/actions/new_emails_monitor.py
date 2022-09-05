import asyncio
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
from application.repositories.new_emails_repository import NewEmailsRepository
from application.repositories.predicted_tags_repository import PredictedTagsRepository
from framework.storage.model import RepairParentEmailStorage

log = logging.getLogger(__name__)


@dataclass
class NewEmailsMonitor:
    _event_bus: Client
    _scheduler: AsyncIOScheduler
    _config: Any
    _predicted_tag_repository: PredictedTagsRepository
    _new_emails_repository: NewEmailsRepository
    _repair_parent_email_storage: RepairParentEmailStorage
    _email_tagger_repository: EmailTaggerRepository
    _bruin_repository: BruinRepository

    def __post_init__(self):
        self._semaphore = asyncio.BoundedSemaphore(self._config.MONITOR_CONFIG["semaphores"]["new_emails_concurrent"])

    async def start_email_events_monitor(self, exec_on_start=False):
        log.info("Scheduling NewEmailsMonitor feedback job...")
        next_run_time = undefined

        if exec_on_start:
            tz = timezone(self._config.TIMEZONE)
            next_run_time = datetime.now(tz)
            log.info("NewEmailsMonitor feedback job is going to be executed immediately")

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
            log.info(f"Skipping start of NewEmailsMonitor feedback job. Reason: {conflict}")

    async def _run_new_emails_polling(self):
        log.info("Starting NewEmailsMonitor feedback process...")

        start_time = time.time()

        log.info("Getting all new emails...")
        new_emails = self._new_emails_repository.get_pending_emails()
        log.info(f"Got {len(new_emails)} emails that needs tagging.")

        tasks = [self._process_new_email(email_data) for email_data in new_emails]
        await asyncio.gather(*tasks, return_exceptions=True)
        log.info("NewEmailsMonitor process finished! Took {:.3f}s".format(time.time() - start_time))

    async def _process_new_email(self, email_data: dict):
        email_id = email_data["email"]["email_id"]
        parent_id = email_data["email"].get("parent_id", None)

        async with self._semaphore:
            # KRE will fail if the mail is not a parent email, but currently KRE monitors the number of processed emails
            # So, always get tag from KRE event if we know the mail is not a parent email.
            response = await self._email_tagger_repository.get_prediction(email_data)
            prediction = response.get("body")
            log.info("email_id=%s parent_id=%s - Got prediction %s", email_id, parent_id, prediction)

            # Once KRE was informed, we check if the email is a reply
            store_replies_enabled = self._config.MONITOR_CONFIG["store_replies_enabled"]
            if parent_id and store_replies_enabled:
                parent = self._repair_parent_email_storage.find(parent_id)
                if parent:
                    log.info("email_id=%s is a reply to email %s", email_id, parent_id)
                    # add predicted tag to DB
                    self._predicted_tag_repository.save_new_tag(email_id, parent.tag.type, parent.tag.probability)

                self._new_emails_repository.mark_complete(email_id)
                return

            # If the mail is a reply email, status won't be in the 200~300 range
            if response["status"] not in range(200, 300):
                return

            if prediction is not None and len(prediction) > 0:
                log.info(
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
