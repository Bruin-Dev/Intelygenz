from unittest.mock import AsyncMock, Mock

import pytest
from application.actions.get_email_inference import GetInference
from application.repositories.utils_repository import to_json_bytes
from nats.aio.msg import Msg


class TestGetInference:
    def instance_test(self):
        kre_repository = Mock()

        inference = GetInference(kre_repository)

        assert inference._kre_repository == kre_repository

    @pytest.mark.parametrize(
        "body_in_topic",
        [
            {},
            ({"some-key": "some-data"}),
        ],
        ids=[
            "without_body",
            "without_params",
        ],
    )
    @pytest.mark.asyncio
    async def get_email_inference_error_400_test(self, body_in_topic):
        request_id = 123
        response_topic = "_INBOX.2007314fe0fcb2cdc2a2914c1"
        msg_published_in_topic = {"request_id": request_id, "response_topic": response_topic, "body": body_in_topic}

        kre_repository = Mock()
        kre_repository.get_email_inference = AsyncMock()

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg_published_in_topic)

        inference_action = GetInference(kre_repository)

        await inference_action(request_msg)

        request_msg.respond.assert_awaited_once_with(
            to_json_bytes(
                {
                    "request_id": request_id,
                    "body": 'You must specify {.."body": { "email_id", "subject", ...}} in the request',
                    "status": 400,
                }
            ),
        )
        inference_action._kre_repository.get_email_inference.assert_not_awaited()

    @pytest.mark.asyncio
    async def get_email_inference_test(self, make_email, make_inference_request_payload, make_inference_data):
        request_id = 123
        email = make_email(email_id="1234")
        request_body = make_inference_request_payload(email_data=email)
        msg_published_in_topic = {
            "request_id": request_id,
            "body": request_body,
        }
        expected_inference = {"body": make_inference_data(), "status": 200}

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg_published_in_topic)

        kre_repository = Mock()
        kre_repository.get_email_inference = AsyncMock(return_value=expected_inference)

        inference_action = GetInference(kre_repository)

        await inference_action(request_msg)

        inference_action._kre_repository.get_email_inference.assert_awaited_once_with(request_body)
        request_msg.respond.assert_awaited_once_with(
            to_json_bytes(
                {
                    "request_id": request_id,
                    **expected_inference,
                }
            ),
        )
