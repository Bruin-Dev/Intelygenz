import json
from unittest.mock import Mock

import pytest
from nats.aio.msg import Msg


class TestSendToEmail:
    def instance_test(self, send_to_email_action, email_repository):
        assert send_to_email_action._email_repository is email_repository

    @pytest.mark.asyncio
    async def send_to_email_job_test(self, send_to_email_action):
        msg_delivery_status = {"body": "generic okey", "status": 200}
        request_id = "123"
        response_topic = "_INBOX.2007314fe0fcb2cdc2a2914c1"
        msg_body = "Failed Edges to be emailed"
        payload = {"request_id": request_id, "response_topic": response_topic, "email_data": msg_body}
        msg_mock = Mock(spec_set=Msg)
        msg_mock.data = json.dumps(payload).encode()
        send_to_email_action._email_repository.send_to_email = Mock(return_value=msg_delivery_status)

        await send_to_email_action(msg=msg_mock)

        send_to_email_action._email_repository.send_to_email.assert_called_once_with(msg_body)

    @pytest.mark.asyncio
    async def send_to_email_job_no_message_test(self, send_to_email_action):
        request_id = "123"
        response_topic = "_INBOX.2007314fe0fcb2cdc2a2914c1c"
        msg_body = ""
        payload = {"request_id": request_id, "response_topic": response_topic, "email_data": msg_body}
        msg_mock = Mock(spec_set=Msg)
        msg_mock.data = json.dumps(payload).encode()
        send_to_email_action._email_repository.send_to_email = Mock()

        await send_to_email_action(msg=msg_mock)

        send_to_email_action._email_repository.send_to_email.assert_not_called()
