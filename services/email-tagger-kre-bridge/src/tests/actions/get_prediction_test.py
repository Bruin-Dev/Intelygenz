from unittest.mock import AsyncMock, Mock

import pytest
from nats.aio.msg import Msg

from application.actions.get_prediction import GetPrediction
from application.repositories.utils_repository import to_json_bytes


class TestGetPrediction:
    valid_email_data = {"email": {"email_id": 123, "body": "test body", "subject": "test subject"}}

    def instance_test(self):
        email_tagger_repository = Mock()

        prediction = GetPrediction(email_tagger_repository)

        assert prediction._email_tagger_repository == email_tagger_repository

    @pytest.mark.parametrize(
        "body_in_topic",
        [
            None,
            ({"some-key": "some-data"}),
        ],
        ids=[
            "without_body",
            "without_params",
        ],
    )
    @pytest.mark.asyncio
    async def get_prediction_error_400_test(self, body_in_topic):
        request_id = 123
        msg_published_in_topic = {"request_id": request_id, "body": body_in_topic}

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg_published_in_topic)

        email_tagger_repository = Mock()
        email_tagger_repository.get_prediction = AsyncMock()

        prediction_action = GetPrediction(email_tagger_repository)

        await prediction_action(request_msg)

        request_msg.respond.assert_awaited_once_with(
            to_json_bytes(
                {
                    "request_id": request_id,
                    "body": 'You must specify {.."body": { "email": {"email_id", "subject", ...}}} in the request',
                    "status": 400,
                }
            ),
        )
        prediction_action._email_tagger_repository.get_prediction.assert_not_awaited()

    @pytest.mark.asyncio
    async def get_prediction_test(self):
        request_id = 123
        msg_published_in_topic = {
            "request_id": request_id,
            "body": self.valid_email_data,
        }
        expected_prediction = {
            "body": {
                "email_id": 123,
                "prediction": [
                    {"tag_id": "1002", "probability": 0.67},
                    {"tag_id": "1004", "probability": 0.27},
                    {"tag_id": "1001", "probability": 0.03},
                ],
            },
            "status": 200,
        }

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg_published_in_topic)

        email_tagger_repository = Mock()
        email_tagger_repository.get_prediction = AsyncMock(return_value=expected_prediction)

        prediction_action = GetPrediction(email_tagger_repository)

        await prediction_action(request_msg)

        prediction_action._email_tagger_repository.get_prediction.assert_awaited_once_with(self.valid_email_data)
        request_msg.respond.assert_awaited_once_with(
            to_json_bytes(
                {
                    "request_id": request_id,
                    **expected_prediction,
                }
            ),
        )
