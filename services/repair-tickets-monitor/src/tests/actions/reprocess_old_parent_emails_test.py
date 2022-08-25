from datetime import datetime, timedelta
from typing import List
from unittest.mock import AsyncMock, Mock, patch

import pytest
from application.domain.email import EmailStatus
from application.rpc import RpcError
from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.util import undefined
from config import testconfig as config
from framework.storage.model import Email, EmailMetadata, EmailTag
from pydantic import Field
from shortuuid import uuid

uuid_ = uuid()
uuid_mock = patch("application.actions.reprocess_old_parent_emails.uuid", return_value=uuid_)


class TestReprocessOldParentEmails:
    @pytest.mark.asyncio
    async def start_reprocess_old_parent_emails_job_with_exec_on_start_test(
        self, reprocess_old_parent_emails, scheduler
    ):
        next_run_time = datetime.now()
        added_seconds = timedelta(0, 5)

        datetime_mock = Mock()
        datetime_mock.now.return_value = next_run_time

        with patch("application.actions.reprocess_old_parent_emails.datetime", datetime_mock):
            await reprocess_old_parent_emails.start_old_parent_email_reprocess(exec_on_start=True)

        scheduler.add_job.assert_called_once_with(
            reprocess_old_parent_emails._run_old_email_reprocessing_polling,
            "interval",
            seconds=config.MONITOR_CONFIG["scheduler_config"]["old_parent_emails_reprocessing"],
            next_run_time=next_run_time + added_seconds,
            replace_existing=False,
            id="_run_old_email_reprocessing_polling",
        )

    @pytest.mark.asyncio
    async def start_reprocess_old_parent_emails_not_deleted_test(
        self, reprocess_old_parent_emails, scheduler, repair_parent_email_storage
    ):
        next_run_time = datetime.now()
        added_seconds = timedelta(0, 5)

        datetime_mock = Mock()
        datetime_mock.now.return_value = next_run_time
        repair_parent_email_storage.delete = 0

        with patch("application.actions.reprocess_old_parent_emails.datetime", datetime_mock):
            await reprocess_old_parent_emails.start_old_parent_email_reprocess(exec_on_start=True)

        scheduler.add_job.assert_called_once_with(
            reprocess_old_parent_emails._run_old_email_reprocessing_polling,
            "interval",
            seconds=config.MONITOR_CONFIG["scheduler_config"]["old_parent_emails_reprocessing"],
            next_run_time=next_run_time + added_seconds,
            replace_existing=False,
            id="_run_old_email_reprocessing_polling",
        )

    @pytest.mark.asyncio
    async def start_reprocess_old_parent_emails_job_without_exec_on_start_test(
        self, reprocess_old_parent_emails, scheduler
    ):
        next_run_time = undefined

        datetime_mock = Mock()
        datetime_mock.now.return_value = next_run_time

        with patch("application.actions.reprocess_old_parent_emails.datetime", datetime_mock):
            await reprocess_old_parent_emails.start_old_parent_email_reprocess(exec_on_start=False)

        scheduler.add_job.assert_called_once_with(
            reprocess_old_parent_emails._run_old_email_reprocessing_polling,
            "interval",
            seconds=config.MONITOR_CONFIG["scheduler_config"]["old_parent_emails_reprocessing"],
            next_run_time=next_run_time,
            replace_existing=False,
            id="_run_old_email_reprocessing_polling",
        )

    @pytest.mark.asyncio
    async def start_reprocess_old_parent_emails_exception_in_scheduled_job_test(
        self, reprocess_old_parent_emails, repair_parent_email_storage, scheduler
    ):
        next_run_time = datetime.now()

        datetime_mock = Mock()
        datetime_mock.now.return_value = next_run_time
        scheduler.add_job.side_effect = ConflictingIdError("some error")

        with patch("application.actions.reprocess_old_parent_emails.datetime", datetime_mock):
            await reprocess_old_parent_emails.start_old_parent_email_reprocess(exec_on_start=True)

        repair_parent_email_storage.find_all.assert_not_called()

    @pytest.mark.asyncio
    async def start_reprocess_old_parent_emails_exception_in_bruin_repository_test(
        self, reprocess_old_parent_emails, bruin_repository, repair_parent_email_storage
    ):
        next_run_time = datetime.now()

        datetime_mock = Mock()
        datetime_mock.now.return_value = next_run_time
        bruin_repository.mark_email_as_done = {
            "request_id": 1234,
            "status": 400,
            "body": 'Must include "body" in request',
        }

        with patch("application.actions.reprocess_old_parent_emails.datetime", datetime_mock):
            await reprocess_old_parent_emails.start_old_parent_email_reprocess(exec_on_start=True)

        repair_parent_email_storage.delete.assert_not_called()

    @pytest.mark.asyncio
    async def only_old_parents_are_properly_processed_test(
        self,
        reprocess_old_parent_emails,
        repair_parent_email_storage,
    ):
        # given
        reprocess_old_parent_emails._set_email_status_rpc = AsyncMock()

        expired_time = datetime.utcnow() - timedelta(seconds=config.MONITOR_CONFIG["old_parent_email_ttl_seconds"] + 1)
        any_old_parent_email = AnyEmail(metadata=EmailMetadata(utc_creation_datetime=expired_time))
        any_recent_parent_email = AnyEmail(metadata=EmailMetadata(utc_creation_datetime=datetime.utcnow()))
        repair_parent_email_storage.find_all = Mock(return_value=[any_old_parent_email, any_recent_parent_email])
        repair_parent_email_storage.delete = Mock()

        # when
        await reprocess_old_parent_emails._run_old_email_reprocessing_polling()

        # then
        repair_parent_email_storage.delete.assert_called_once_with(any_old_parent_email)
        reprocess_old_parent_emails._set_email_status_rpc.assert_awaited_once_with(
            any_old_parent_email.id, EmailStatus.NEW
        )

    @pytest.mark.asyncio
    async def old_parents_are_removed_only_when_marked_as_done_test(
        self, reprocess_old_parent_emails, repair_parent_email_storage
    ):
        # given
        reprocess_old_parent_emails._set_email_status_rpc = AsyncMock(side_effect=RpcError())

        expired_time = datetime.utcnow() - timedelta(seconds=config.MONITOR_CONFIG["old_parent_email_ttl_seconds"] + 1)
        any_old_parent_email = AnyEmail(metadata=EmailMetadata(utc_creation_datetime=expired_time))
        repair_parent_email_storage.find_all = Mock(return_value=[any_old_parent_email])
        repair_parent_email_storage.delete = Mock()

        # when
        await reprocess_old_parent_emails._run_old_email_reprocessing_polling()

        # then
        reprocess_old_parent_emails._set_email_status_rpc.assert_awaited_once_with(
            any_old_parent_email.id, EmailStatus.NEW
        )
        repair_parent_email_storage.delete.assert_not_called()


class AnyEmailTag(EmailTag):
    type: str = "any_type"
    probability: float = hash("any_probability")


class AnyEmail(Email):
    id: str = "any_id"
    client_id: str = "any_client_id"
    date: datetime = Field(default_factory=lambda: datetime.utcnow())
    subject: str = "any_subject"
    body: str = "any_body"
    sender_address: str = "any_sender_address"
    recipient_addresses: List[str] = Field(default_factory=lambda: ["any_recipient_address"])
    cc_addresses: List[str] = Field(default_factory=lambda: ["any_cc_address"])
    tag: EmailTag = Field(default_factory=lambda: AnyEmailTag())
