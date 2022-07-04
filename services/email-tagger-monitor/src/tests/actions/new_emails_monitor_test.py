from datetime import datetime
from unittest.mock import Mock, call, patch, ANY

import pytest
from application.actions import new_emails_monitor as new_emails_monitor_module
from application.actions.new_emails_monitor import NewEmailsMonitor
from framework.storage.model.email_storage import Email, EmailMetadata
from asynctest import CoroutineMock
from config import testconfig
from shortuuid import uuid

uuid_ = uuid()
uuid_mock = patch.object(new_emails_monitor_module, "uuid", return_value=uuid_)


class TestNewEmailsMonitor:
    def instance_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        bruin_repository = Mock()
        predicted_tag_repository = Mock()
        new_emails_repository = Mock()
        repair_parent_email_storage = Mock()
        repair_reply_email_storage = Mock()
        email_tagger_repository = Mock()

        new_emails_monitor = NewEmailsMonitor(
            event_bus,
            logger,
            scheduler,
            config,
            predicted_tag_repository,
            new_emails_repository,
            repair_parent_email_storage,
            repair_reply_email_storage,
            email_tagger_repository,
            bruin_repository,
        )

        assert new_emails_monitor._event_bus is event_bus
        assert new_emails_monitor._logger is logger
        assert new_emails_monitor._scheduler is scheduler
        assert new_emails_monitor._config is config
        assert new_emails_monitor._predicted_tag_repository is predicted_tag_repository
        assert new_emails_monitor._bruin_repository is bruin_repository
        assert new_emails_monitor._email_tagger_repository is email_tagger_repository
        assert new_emails_monitor._new_emails_repository is new_emails_repository

    @pytest.mark.asyncio
    async def start_new_emails_monitor_job_with_exec_on_start_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        bruin_repository = Mock()
        new_emails_repository = Mock()
        repair_parent_email_storage = Mock()
        repair_reply_email_storage = Mock()
        email_tagger_repository = Mock()
        predicted_tag_repository = Mock()
        new_emails_monitor = NewEmailsMonitor(
            event_bus,
            logger,
            scheduler,
            config,
            predicted_tag_repository,
            new_emails_repository,
            repair_parent_email_storage,
            repair_reply_email_storage,
            email_tagger_repository,
            bruin_repository,
        )
        next_run_time = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)
        with patch.object(new_emails_monitor_module, "datetime", new=datetime_mock):
            with patch.object(new_emails_monitor_module, "timezone", new=Mock()):
                await new_emails_monitor.start_email_events_monitor(exec_on_start=True)

        scheduler.add_job.assert_called_once_with(
            new_emails_monitor._run_new_emails_polling,
            "interval",
            seconds=testconfig.MONITOR_CONFIG["scheduler_config"]["new_emails_seconds"],
            next_run_time=next_run_time,
            replace_existing=False,
            id="_run_new_emails_polling",
        )

    @pytest.mark.asyncio
    async def new_emails_monitor_process_ok_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        bruin_repository = Mock()
        new_emails_repository = Mock()
        repair_parent_email_storage = Mock()
        repair_reply_email_storage = Mock()
        email_tagger_repository = Mock()
        predicted_tag_repository = Mock()
        new_emails_monitor = NewEmailsMonitor(
            event_bus,
            logger,
            scheduler,
            config,
            predicted_tag_repository,
            new_emails_repository,
            repair_parent_email_storage,
            repair_reply_email_storage,
            email_tagger_repository,
            bruin_repository,
        )

        pending_emails = [
            {"email": {"email_id": "100"}},
            {"email": {"email_id": "101"}},
        ]
        prediction_tag_id = "1001"
        tag_info = {"id": prediction_tag_id, "probability": 0.9}

        new_emails_monitor._new_emails_repository.get_pending_emails = Mock(return_value=pending_emails)
        new_emails_monitor._email_tagger_repository.get_prediction = CoroutineMock(
            return_value={"status": 200, "body": ["prediction_dict_1", "prediction_dict_2"]}
        )
        new_emails_monitor.get_most_probable_tag_id = Mock(return_value=tag_info)
        new_emails_monitor._bruin_repository.post_email_tag = CoroutineMock(return_value={"status": 200})
        new_emails_monitor._new_emails_repository.mark_complete = Mock()

        await new_emails_monitor._run_new_emails_polling()

        email_calls = [call(pending_emails[0]), call(pending_emails[1])]
        new_emails_monitor._email_tagger_repository.get_prediction.assert_has_awaits(email_calls, any_order=True)
        new_emails_monitor._new_emails_repository.mark_complete.assert_has_calls(
            [
                call(pending_emails[0]["email"]["email_id"]),
                call(pending_emails[1]["email"]["email_id"]),
            ],
            any_order=True,
        )
        new_emails_monitor._bruin_repository.post_email_tag.assert_has_awaits(
            [
                call(pending_emails[0]["email"]["email_id"], prediction_tag_id),
                call(pending_emails[1]["email"]["email_id"], prediction_tag_id),
            ],
            any_order=True,
        )

    @pytest.mark.asyncio
    async def new_emails_monitor_process_tag_already_present_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        bruin_repository = Mock()
        new_emails_repository = Mock()
        repair_parent_email_storage = Mock()
        repair_reply_email_storage = Mock()
        email_tagger_repository = Mock()
        predicted_tag_repository = Mock()
        new_emails_monitor = NewEmailsMonitor(
            event_bus,
            logger,
            scheduler,
            config,
            predicted_tag_repository,
            new_emails_repository,
            repair_parent_email_storage,
            repair_reply_email_storage,
            email_tagger_repository,
            bruin_repository,
        )

        email_id = "TEST101"
        pending_email = {"email": {"email_id": email_id}}
        prediction_tag_id = "1001"
        tag_info = {"id": prediction_tag_id, "probability": 0.9}

        new_emails_monitor._new_emails_repository.get_pending_emails = Mock(return_value=[pending_email])
        new_emails_monitor._email_tagger_repository.get_prediction = CoroutineMock(
            return_value={"status": 200, "body": ["prediction_dict_1", "prediction_dict_2"]}
        )
        new_emails_monitor.get_most_probable_tag_id = Mock(return_value=tag_info)
        new_emails_monitor._bruin_repository.post_email_tag = CoroutineMock(
            return_value={"status": 409, "body": "Tag already present"}
        )
        new_emails_monitor._new_emails_repository.mark_complete = Mock()

        await new_emails_monitor._run_new_emails_polling()

        new_emails_monitor._email_tagger_repository.get_prediction.assert_awaited_once_with(pending_email)
        new_emails_monitor._email_tagger_repository.get_prediction.assert_awaited_once_with(pending_email)
        new_emails_monitor._bruin_repository.post_email_tag.assert_awaited_once_with(email_id, prediction_tag_id)
        new_emails_monitor._new_emails_repository.mark_complete.assert_called_once_with(email_id)

    @pytest.mark.asyncio
    async def _process_new_email_ok_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        bruin_repository = Mock()
        new_emails_repository = Mock()
        repair_parent_email_storage = Mock()
        repair_reply_email_storage = Mock()
        email_tagger_repository = Mock()
        predicted_tag_repository = Mock()
        new_emails_monitor = NewEmailsMonitor(
            event_bus,
            logger,
            scheduler,
            config,
            predicted_tag_repository,
            new_emails_repository,
            repair_parent_email_storage,
            repair_reply_email_storage,
            email_tagger_repository,
            bruin_repository,
        )

        email_id = "123456"
        email_data = {
            "email": {
                "email_id": email_id,
                "subject": "the title",
                "body": "the issue here",
                "date": "2021-01-01T08:00:00.001Z",
            }
        }
        prediction_response = [
            {"tag_id": "TEST", "probability": 0.77},
            {"tag_id": "TEST2", "probability": 0.23},
        ]
        most_prob_tag_data = {"id": "TEST", "probability": 0.77}

        new_emails_monitor._email_tagger_repository.get_prediction = CoroutineMock(
            return_value={"status": 200, "body": prediction_response}
        )
        new_emails_monitor.get_most_probable_tag_id = Mock(return_value=most_prob_tag_data)
        new_emails_monitor._bruin_repository.post_email_tag = CoroutineMock(return_value={"status": 200, "body": "ok"})
        new_emails_monitor._new_emails_repository.mark_complete = Mock()

        await new_emails_monitor._process_new_email(email_data)

        new_emails_monitor._email_tagger_repository.get_prediction.assert_awaited_once_with(email_data)
        new_emails_monitor._bruin_repository.post_email_tag.assert_awaited_once_with(
            email_data["email"]["email_id"], prediction_response[0]["tag_id"]
        )
        new_emails_monitor._new_emails_repository.mark_complete.assert_called_once_with(email_id)

        predicted_tag_repository.save_new_tag.assert_called_once()

    @pytest.mark.asyncio
    async def _process_new_reply_email_when_parent_id_exists_ok_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        bruin_repository = Mock()
        new_emails_repository = Mock()
        repair_parent_email_storage = Mock()
        repair_reply_email_storage = Mock()
        email_tagger_repository = Mock()
        predicted_tag_repository = Mock()
        new_emails_monitor = NewEmailsMonitor(
            event_bus,
            logger,
            scheduler,
            config,
            predicted_tag_repository,
            new_emails_repository,
            repair_parent_email_storage,
            repair_reply_email_storage,
            email_tagger_repository,
            bruin_repository,
        )

        email_id = "123456"
        parent_id = "654321"
        email_data = {
            "email": {
                "email_id": email_id,
                "parent_id": parent_id,
                "previous_email_id": "123455",
                "client_id": "123123",
                "subject": "the title",
                "body": "the issue here",
                "date": "2021-01-01T08:00:00.001Z",
                "from_address": "mettel@intelygenz.com",
                "to_address": ["a@mettel.com", "b@mettel.com"],
            }
        }

        email_model = Email(
            email_id=email_data["email"]["email_id"],
            client_id=email_data["email"]["client_id"],
            date=email_data["email"]["date"],
            subject=email_data["email"]["subject"],
            body=email_data["email"]["body"],
            from_address=email_data["email"]["from_address"],
            to_address=email_data["email"]["to_address"],
            send_cc=email_data["email"].get("send_cc", []),
            parent_id=email_data["email"].get("parent_id", None),
            previous_id=email_data["email"].get("previous_email_id", None),
            tag=email_data["email"].get("tag", None),
            metadata=EmailMetadata()
        )

        new_emails_monitor._repair_parent_email_storage.exists.return_value = 1
        new_emails_monitor._repair_reply_email_storage.set = Mock()
        new_emails_monitor._new_emails_repository.mark_complete = Mock()
        new_emails_monitor._email_tagger_repository.get_prediction = Mock()

        await new_emails_monitor._process_new_email(email_data)

        new_emails_monitor._repair_parent_email_storage.exists.assert_called_once_with(parent_id)
        new_emails_monitor._repair_reply_email_storage.set.assert_called_once_with(
            id=email_id, data=email_model
        )
        new_emails_monitor._new_emails_repository.mark_complete.assert_called_once_with(email_id)
        new_emails_monitor._email_tagger_repository.get_prediction.assert_not_called()

    @pytest.mark.asyncio
    async def _process_new_reply_email_when_parent_id_does_not_exist_ok_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        bruin_repository = Mock()
        new_emails_repository = Mock()
        repair_parent_email_storage = Mock()
        repair_reply_email_storage = Mock()
        email_tagger_repository = Mock()
        predicted_tag_repository = Mock()
        new_emails_monitor = NewEmailsMonitor(
            event_bus,
            logger,
            scheduler,
            config,
            predicted_tag_repository,
            new_emails_repository,
            repair_parent_email_storage,
            repair_reply_email_storage,
            email_tagger_repository,
            bruin_repository,
        )

        email_id = "123456"
        parent_id = "654321"
        email_data = {
            "email": {
                "email_id": email_id,
                "parent_id": parent_id,
                "subject": "the title",
                "body": "the issue here",
                "date": "2021-01-01T08:00:00.001Z",
            }
        }
        prediction_response = [
            {"tag_id": "TEST", "probability": 0.77},
            {"tag_id": "TEST2", "probability": 0.23},
        ]
        most_prob_tag_data = {"id": "TEST", "probability": 0.77}

        new_emails_monitor._repair_parent_email_storage.exists.return_value = 0
        new_emails_monitor._repair_reply_email_storage.set = Mock()
        new_emails_monitor._email_tagger_repository.get_prediction = CoroutineMock(
            return_value={"status": 200, "body": prediction_response}
        )
        new_emails_monitor.get_most_probable_tag_id = Mock(return_value=most_prob_tag_data)
        new_emails_monitor._bruin_repository.post_email_tag = CoroutineMock(return_value={"status": 200, "body": "ok"})
        new_emails_monitor._new_emails_repository.mark_complete = Mock()

        await new_emails_monitor._process_new_email(email_data)

        new_emails_monitor._repair_parent_email_storage.exists.assert_called_once_with(parent_id)
        new_emails_monitor._repair_reply_email_storage.set.assert_not_called()
        new_emails_monitor._email_tagger_repository.get_prediction.assert_awaited_once_with(email_data)
        new_emails_monitor._bruin_repository.post_email_tag.assert_awaited_once_with(
            email_data["email"]["email_id"], prediction_response[0]["tag_id"]
        )
        new_emails_monitor._new_emails_repository.mark_complete.assert_called_once_with(email_id)

        predicted_tag_repository.save_new_tag.assert_called_once()

    @pytest.mark.asyncio
    async def _process_new_email_non_2xx_get_prediction_status_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        bruin_repository = Mock()
        new_emails_repository = Mock()
        repair_parent_email_storage = Mock()
        repair_reply_email_storage = Mock()
        email_tagger_repository = Mock()
        predicted_tag_repository = Mock()
        new_emails_monitor = NewEmailsMonitor(
            event_bus,
            logger,
            scheduler,
            config,
            predicted_tag_repository,
            new_emails_repository,
            repair_parent_email_storage,
            repair_reply_email_storage,
            email_tagger_repository,
            bruin_repository,
        )

        email_id = "123456"
        email_data = {
            "email": {
                "email_id": email_id,
                "subject": "the title",
                "body": "the issue here",
                "date": "2021-01-01T08:00:00.001Z",
            }
        }

        new_emails_monitor._email_tagger_repository.get_prediction = CoroutineMock(
            return_value={"request_id": uuid(), "body": "Failed", "status": 400}
        )
        new_emails_monitor._bruin_repository.post_email_tag = CoroutineMock()
        new_emails_monitor._new_emails_repository.mark_complete = Mock()

        await new_emails_monitor._process_new_email(email_data)

        new_emails_monitor._email_tagger_repository.get_prediction.assert_awaited_once_with(email_data)
        new_emails_monitor._bruin_repository.post_email_tag.assert_not_awaited()
        new_emails_monitor._new_emails_repository.mark_complete.assert_not_called()

    @pytest.mark.asyncio
    async def _process_new_email_non_2xx_post_email_tag_status_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        bruin_repository = Mock()
        new_emails_repository = Mock()
        repair_parent_email_storage = Mock()
        repair_reply_email_storage = Mock()
        email_tagger_repository = Mock()
        predicted_tag_repository = Mock()
        new_emails_monitor = NewEmailsMonitor(
            event_bus,
            logger,
            scheduler,
            config,
            predicted_tag_repository,
            new_emails_repository,
            repair_parent_email_storage,
            repair_reply_email_storage,
            email_tagger_repository,
            bruin_repository,
        )

        email_id = "123456"
        email_data = {
            "email": {
                "email_id": email_id,
                "subject": "the title",
                "body": "the issue here",
                "date": "2021-01-01T08:00:00.001Z",
            }
        }
        prediction_response = [
            {"tag_id": "TEST", "probability": 0.77},
            {"tag_id": "TEST2", "probability": 0.23},
        ]

        most_prob_tag = {"id": "TEST", "probability": 0.77}

        new_emails_monitor._email_tagger_repository.get_prediction = CoroutineMock(
            return_value={"status": 200, "body": prediction_response}
        )
        new_emails_monitor._bruin_repository.post_email_tag = CoroutineMock(
            return_value={"status": 400, "body": "Failed"}
        )

        new_emails_monitor.get_most_probable_tag_id = Mock(return_value=most_prob_tag)
        new_emails_monitor._bruin_repository.post_email_tag = CoroutineMock()
        new_emails_monitor._new_emails_repository.mark_complete = Mock()

        await new_emails_monitor._process_new_email(email_data)

        new_emails_monitor._email_tagger_repository.get_prediction.assert_awaited_once_with(email_data)
        new_emails_monitor._bruin_repository.post_email_tag.assert_awaited_once_with(
            email_data["email"]["email_id"], prediction_response[0]["tag_id"]
        )
        new_emails_monitor._new_emails_repository.mark_complete.assert_not_called()

    def get_most_probable_tag_id_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        bruin_repository = Mock()
        new_emails_repository = Mock()
        repair_parent_email_storage = Mock()
        repair_reply_email_storage = Mock()
        email_tagger_repository = Mock()
        predicted_tag_repository = Mock()
        new_emails_monitor = NewEmailsMonitor(
            event_bus,
            logger,
            scheduler,
            config,
            predicted_tag_repository,
            new_emails_repository,
            repair_parent_email_storage,
            repair_reply_email_storage,
            email_tagger_repository,
            bruin_repository,
        )

        tag_id = new_emails_monitor.get_most_probable_tag_id(
            [
                {"tag_id": "WRONG1", "probability": 0.1},
                {"tag_id": "WRONG2", "probability": 0.2},
                {"tag_id": "CORRECT", "probability": 0.5},
                {"tag_id": "WRONG3", "probability": 0.2},
            ]
        )

        assert tag_id == {"id": "CORRECT", "probability": 0.5}
