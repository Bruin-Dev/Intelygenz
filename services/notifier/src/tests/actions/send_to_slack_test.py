from http import HTTPStatus
from unittest.mock import Mock

import pytest
from application.clients.slack_client import SlackResponse
from asynctest import CoroutineMock
from config import testconfig as config
from tests.fixtures.custom_objects import client_response


class TestSlackNotifier:
    def instantiation_test(self, send_to_slack_action, event_bus, logger, slack_repository):
        assert send_to_slack_action._config is config
        assert send_to_slack_action._event_bus is event_bus
        assert send_to_slack_action._slack_repository is slack_repository
        assert send_to_slack_action._logger is logger

    @pytest.mark.asyncio
    async def send_to_slack_test(self, send_to_slack_action, client_response):
        request_id = "123"
        response_topic = "_INBOX.2007314fe0fcb2cdc2a2914c1"
        msg_body = "Failed Edges to be slacked"
        msg_dict = {
            "request_id": request_id,
            "response_topic": response_topic,
            "message": msg_body,
        }
        response_status = HTTPStatus.OK
        response_body = "any_response_body"
        slack_response = client_response(body=response_body, status=response_status)

        send_to_slack_action._slack_repository.send_to_slack = CoroutineMock(return_value=slack_response)

        await send_to_slack_action.send_to_slack(msg=msg_dict)

        send_to_slack_action._slack_repository.send_to_slack.assert_called_once_with(msg_body)
        send_to_slack_action._event_bus.publish_message.assert_awaited_once_with(
            response_topic,
            {"request_id": request_id, "status": response_status},
        )
