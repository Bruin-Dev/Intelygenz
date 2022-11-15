from unittest.mock import AsyncMock, Mock

import pytest
from application.actions.save_outputs import SaveOutputs
from application.repositories.utils_repository import to_json_bytes
from nats.aio.msg import Msg


class TestPostAutomationMetrics:
    def instance_test(self):
        kre_repository = Mock()

        save_outputs = SaveOutputs(kre_repository)

        assert save_outputs._kre_repository == kre_repository

    @pytest.mark.parametrize(
        "body_in_topic",
        [
            ({}),
        ],
        ids=[
            "no_body",
        ],
    )
    @pytest.mark.asyncio
    async def save_outputs_error_400_test(self, body_in_topic):
        request_id = 123
        msg_published_in_topic = {"request_id": request_id, "body": body_in_topic}

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg_published_in_topic)

        kre_repository = Mock()
        kre_repository.save_outputs = AsyncMock()

        save_outputs = SaveOutputs(kre_repository)

        await save_outputs(request_msg)

        kre_repository.save_outputs.assert_not_awaited()
        request_msg.respond.assert_awaited_once_with(
            to_json_bytes(
                {
                    "request_id": request_id,
                    "body": "You must specify body in the request",
                    "status": 400,
                }
            ),
        )

    @pytest.mark.asyncio
    async def save_outputs_ok_test(self, valid_output_request):
        request_id = 123
        msg_published_in_topic = {
            "request_id": request_id,
            "body": valid_output_request,
        }

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg_published_in_topic)

        return_value = {"body": "No content", "status": 204}

        kre_repository = Mock()
        kre_repository.save_outputs = AsyncMock(return_value=return_value)

        save_outputs = SaveOutputs(kre_repository)

        await save_outputs(request_msg)

        kre_repository.save_outputs.assert_awaited_once()
        request_msg.respond.assert_awaited_once_with(
            to_json_bytes({"request_id": request_id, "body": return_value["body"], "status": return_value["status"]}),
        )
