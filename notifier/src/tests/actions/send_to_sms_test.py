from unittest.mock import Mock
from application.actions.send_to_sms import SendToSms
from asynctest import CoroutineMock
from config import testconfig as config
import pytest


class TestTeleStaxNotifier:

    def instantiation_test(self):
        mock_telestax_repository = Mock()
        test_bus = Mock()
        mock_logger = Mock()

        test_actions = SendToSms(config, test_bus, mock_logger, mock_telestax_repository)

        assert test_actions._config is config
        assert test_actions._event_bus is test_bus
        assert test_actions._logger is mock_logger
        assert test_actions._telestax_repository is mock_telestax_repository

    @pytest.mark.asyncio
    async def send_to_sms_test(self):
        mock_telestax_repository = Mock()
        test_bus = Mock()
        test_bus.publish_message = CoroutineMock()
        mock_logger = Mock()

        msg_delivery_status = 200
        request_id = "123"
        response_topic = "notifications.sms.request"
        sms_body = "This is a dummy SMS"
        sms_to = '17777777777'
        sms_payload = {
            'sms_data': sms_body,
            'sms_to': sms_to
        }
        msg_dict = {
            "request_id": request_id,
            "response_topic": response_topic,
            "body": sms_payload,
        }

        test_actions = SendToSms(config, test_bus, mock_logger, mock_telestax_repository)
        test_actions._telestax_repository.send_to_sms = Mock(return_value=msg_delivery_status)

        await test_actions.send_to_sms(msg=msg_dict)

        test_actions._telestax_repository.send_to_sms.assert_called_once_with(
            sms_body,
            sms_to
        )
        test_bus.publish_message.assert_awaited_once_with(
            response_topic,
            {'request_id': request_id, 'status': msg_delivery_status, 'body': sms_payload},
        )

    @pytest.mark.asyncio
    async def send_to_sms_payload_not_valid_error_500_test(self):
        mock_telestax_repository = Mock()
        test_bus = Mock()
        test_bus.publish_message = CoroutineMock()
        mock_logger = Mock()

        msg_delivery_status = 400
        request_id = "123"
        response_topic = "notifications.sms.request"
        sms_body = "This is a dummy SMS"
        sms_to = '17777777777'
        sms_payload = {
            'sms_data_NOT_FOUNDsms_data': sms_body,
            'sms_to_NOT_FOUND': sms_to
        }
        msg_dict = {
            "request_id": request_id,
            "response_topic": response_topic,
            "body": sms_payload,
        }

        test_actions = SendToSms(config, test_bus, mock_logger, mock_telestax_repository)
        test_actions._telestax_repository.send_to_sms = Mock(return_value=msg_delivery_status)

        await test_actions.send_to_sms(msg=msg_dict)

        test_actions._telestax_repository.send_to_sms.assert_not_called()
        test_bus.publish_message.assert_awaited_with(
            response_topic,
            {'request_id': request_id, 'status': msg_delivery_status, 'body': sms_payload},
        )
