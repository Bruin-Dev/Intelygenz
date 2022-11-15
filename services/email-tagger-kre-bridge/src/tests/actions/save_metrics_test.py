from unittest.mock import AsyncMock, Mock

import pytest
from application.actions.save_metrics import SaveMetrics
from application.repositories.utils_repository import to_json_bytes
from nats.aio.msg import Msg


class TestPostAutomationMetrics:
    def instance_test(self):
        email_tagger_repository = Mock()

        save_metrics = SaveMetrics(email_tagger_repository)

        assert save_metrics._email_tagger_repository == email_tagger_repository

    @pytest.mark.parametrize(
        "body_in_topic",
        [
            None,
            ({"some-key": "some-data"}),
            ({"email_id": 12345}),
        ],
        ids=[
            "without_body",
            "without_params",
            "without_email_data",
        ],
    )
    @pytest.mark.asyncio
    async def save_metrics_error_400_test(self, body_in_topic):
        request_id = 123
        msg_published_in_topic = {"request_id": request_id, "body": body_in_topic}

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg_published_in_topic)

        email_tagger_repository = Mock()
        email_tagger_repository.save_metrics = AsyncMock()

        save_metrics = SaveMetrics(email_tagger_repository)

        await save_metrics(request_msg)

        email_tagger_repository.save_metrics.assert_not_awaited()
        request_msg.respond.assert_awaited_once_with(
            to_json_bytes(
                {
                    "request_id": request_id,
                    "body": 'You must specify {.."body": {"original_email": {...}, "ticket": {...}}} in the request',
                    "status": 400,
                }
            ),
        )

    @pytest.mark.asyncio
    async def save_metrics_ok_test(self):
        request_id = 123
        params = {
            "original_email": {
                "email": {
                    "email_id": "2726244",
                    "date": "2016-08-29T09:12:33:001Z",
                    "subject": "email_subject",
                    "body": "email_body",
                    "parent_id": "2726243",
                },
                "tag_ids": ["4", "3", "2"],
            },
            "ticket": {
                "ticket_id": "123456",
                "call_type": "chg",
                "category": "aac",
                "creation_date": "2016-08-29T09:12:33:001Z",
            },
        }

        msg_published_in_topic = {
            "request_id": request_id,
            "body": params,
        }

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg_published_in_topic)

        return_value = {"body": "No content", "status": 204}

        email_tagger_repository = Mock()
        email_tagger_repository.save_metrics = AsyncMock(return_value=return_value)

        save_metrics = SaveMetrics(email_tagger_repository)

        await save_metrics(request_msg)

        email_tagger_repository.save_metrics.assert_awaited_once()
        request_msg.respond.assert_awaited_once_with(
            to_json_bytes({"request_id": request_id, "body": return_value["body"], "status": return_value["status"]}),
        )
