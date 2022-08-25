import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Iterator

from application.domain.email import EmailStatus
from application.rpc import RpcError
from application.rpc.set_email_status_rpc import SetEmailStatusRpc
from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.util import undefined
from dataclasses import dataclass
from framework.nats.client import Client as NatsClient
from framework.storage.model.email_storage import Email, RepairParentEmailStorage
from pytz import timezone

log = logging.getLogger(__name__)


@dataclass
class ReprocessOldParentEmails:
    _event_bus: NatsClient
    _scheduler: AsyncIOScheduler
    _config: Any
    _repair_parent_email_storage: RepairParentEmailStorage
    _set_email_status_rpc: SetEmailStatusRpc

    def __post_init__(self):
        self._semaphore = asyncio.BoundedSemaphore(
            self._config.MONITOR_CONFIG["semaphores"]["old_parent_emails_reprocessing_concurrent"]
        )

    async def start_old_parent_email_reprocess(self, exec_on_start=False):
        log.info("Scheduling Reprocess Old Parent Emails job...")
        next_run_time = undefined

        if exec_on_start:
            added_seconds = timedelta(0, 5)
            tz = timezone(self._config.TIMEZONE)
            next_run_time = datetime.now(tz) + added_seconds
            log.info("ReprocessOldParentEmails job is going to be executed immediately")

        try:
            scheduler_seconds = self._config.MONITOR_CONFIG["scheduler_config"]["old_parent_emails_reprocessing"]
            self._scheduler.add_job(
                self._run_old_email_reprocessing_polling,
                "interval",
                seconds=scheduler_seconds,
                next_run_time=next_run_time,
                replace_existing=False,
                id="_run_old_email_reprocessing_polling",
            )
        except ConflictingIdError as conflict:
            log.info(f"Skipping start of ReprocessOldParentEmails job. Reason: {conflict}")

    async def _run_old_email_reprocessing_polling(self):
        log.info("Starting ReprocessOldParentEmails process...")
        old_parent_emails = await self._get_old_parent_emails()
        log.info(f"Found {len(list(old_parent_emails))} old parent emails")

        old_parent_emails_filtered = [
            old_parent_email
            for old_parent_email in old_parent_emails
            if (datetime.utcnow() - old_parent_email.metadata.utc_creation_datetime).total_seconds()
            > self._config.MONITOR_CONFIG["old_parent_email_ttl_seconds"]
        ]
        log.info(f"Found {len(old_parent_emails_filtered)} old parent emails to be discarded")

        tasks = [self._prepare_email_to_reprocess(old_parent_email) for old_parent_email in old_parent_emails_filtered]
        await asyncio.gather(*tasks)

    async def _get_old_parent_emails(self) -> Iterator[Email]:
        return self._repair_parent_email_storage.find_all()

    async def _prepare_email_to_reprocess(self, old_parent_email: Email):
        async with self._semaphore:
            try:
                log.info(f"Discarding {old_parent_email.id} old parent email")
                await self._set_email_status_rpc(old_parent_email.id, EmailStatus.NEW)
                self._remove_email_from_storage(old_parent_email)
            except RpcError as e:
                log.error(f"Error while while marking email as new for email Id {old_parent_email.id}: {e}")

    def _remove_email_from_storage(self, old_parent_email: Email):
        deleted_parent_email = self._repair_parent_email_storage.delete(old_parent_email)
        if deleted_parent_email == 0:
            log.error(f"Error while removing old parent email with id {old_parent_email.id} from storage")
