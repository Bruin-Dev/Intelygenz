import pytest
from asynctest import Mock
from config import testconfig as config


class TestSendToEmail:
    def instantiation_test(self, send_to_email_action, event_bus, logger, email_repository):
        assert send_to_email_action._config is config
        assert send_to_email_action._event_bus is event_bus
        assert send_to_email_action._logger is logger
        assert send_to_email_action._email_repository is email_repository

    @pytest.mark.asyncio
    async def send_to_email_job_test(self, send_to_email_action):
        msg_delivery_status = 200
        request_id = "123"
        response_topic = "_INBOX.2007314fe0fcb2cdc2a2914c1"
        msg_body = "Failed Edges to be emailed"
        msg_dict = {
            "request_id": request_id,
            "response_topic": response_topic,
            "email_data": msg_body,
        }
        send_to_email_action._email_repository.send_to_email = Mock(return_value=msg_delivery_status)

        await send_to_email_action.send_to_email(msg=msg_dict)

        send_to_email_action._email_repository.send_to_email.assert_called_once_with(msg_body)
        send_to_email_action._event_bus.publish_message.assert_awaited_once_with(
            response_topic, {"request_id": request_id, "status": msg_delivery_status}
        )

    @pytest.mark.asyncio
    async def send_to_email_job_no_message_test(self, send_to_email_action):
        request_id = "123"
        response_topic = "_INBOX.2007314fe0fcb2cdc2a2914c1c"
        msg_body = ""
        msg_dict = {
            "request_id": request_id,
            "response_topic": response_topic,
            "email_data": msg_body,
        }
        send_to_email_action._email_repository.send_to_email = Mock()

        await send_to_email_action.send_to_email(msg=msg_dict)

        send_to_email_action._email_repository.send_to_email.assert_not_called()
        send_to_email_action._event_bus.publish_message.assert_awaited_once_with(
            response_topic, {"request_id": request_id, "status": 500}
        )
