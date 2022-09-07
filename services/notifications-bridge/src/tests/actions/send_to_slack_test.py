import json
from http import HTTPStatus
from unittest.mock import AsyncMock, Mock

import pytest
from nats.aio.msg import Msg


class TestSendToSlack:
    def instance_test(self, send_to_slack_action, slack_repository):
        assert send_to_slack_action._slack_repository is slack_repository

    @pytest.mark.asyncio
    async def send_to_slack_test(self, send_to_slack_action, client_response):
        request_id = "123"
        response_topic = "_INBOX.2007314fe0fcb2cdc2a2914c1"
        msg = "Failed Edges to be slacked"
        payload = {
            "request_id": request_id,
            "response_topic": response_topic,
            "body": {
                "message": msg,
            },
        }
        msg_mock = Mock(spec_set=Msg)
        msg_mock.data = json.dumps(payload).encode()
        response_status = HTTPStatus.OK
        response_body = "any_response_body"
        slack_response = client_response(body=response_body, status=response_status)

        send_to_slack_action._slack_repository.send_to_slack = AsyncMock(return_value=slack_response)

        await send_to_slack_action(msg=msg_mock)

        send_to_slack_action._slack_repository.send_to_slack.assert_called_once_with(msg)
