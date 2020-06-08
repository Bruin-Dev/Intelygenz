from http import HTTPStatus

from application.clients import telestax_client
from application.clients.telestax_client import TeleStaxClient
from unittest.mock import Mock, patch

from pytest import raises
from config import testconfig as config
import requests
import json


class TestTeleStaxClient:

    def instantiation_test(self):
        mock_logger = Mock()

        test_client = TeleStaxClient(config, mock_logger)

        assert test_client._config.TELESTAX_CONFIG is config.TELESTAX_CONFIG
        assert test_client._logger is mock_logger

        assert test_client._headers == {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Basic QUNDT1VOVF9TSUQ6QVVUSF9UT0tFTg==',
            'Accept': 'text/plain'
        }

    def send_to_sms_test(self):
        mock_logger = Mock()
        sms_from = '16666666666'
        sms_to = '17777777777'
        sms_body = 'This is a dummy SMS'
        sms_payload = {
            'sms_data': sms_body,
            'sms_to': sms_to
        }
        test_msg = {
            'From': sms_from,
            'To': sms_to,
            'Body': sms_body
        }
        msg_delivery_status = 200

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Basic QUNDT1VOVF9TSUQ6QVVUSF9UT0tFTg==',
            'Accept': 'text/plain'
        }

        sms_success_response = {
          'sid': 'SM74b94f1bd0da4546ad034fc7c69791c0',
          'date_created': 'Fri, 29 May 2020 10:22:40 +0000',
          'date_updated': 'Fri, 29 May 2020 10:22:40 +0000',
          'account_sid': 'AC0dcb17b068164ddcf208df8c63783383',
          'from': sms_from,
          'to': sms_to,
          'body': 'This is a dummy SMS',
          'status': 'queued',
          'direction': 'outbound-api',
          'price': '0',
          'price_unit': 'USD',
          'api_version': '2012-04-24',
          'uri': f'/2012-04-24/Accounts/'
                 f'AC0dcb17b068164ddcf208df8c63783383/SMS/Messages/SM74b94f1bd0da4546ad034fc7c69791c0.json'
        }

        test_client = TeleStaxClient(config, mock_logger)
        test_client._logger = Mock()

        class ReponseHttp:
            status_code = msg_delivery_status
            _sms_success_response = sms_success_response

            def json(self):
                return self._sms_success_response

        with patch.object(telestax_client.requests, 'post') as post_mock:
            post_mock.return_value = ReponseHttp()

            response = test_client.send_to_sms(sms_payload['sms_data'], sms_payload['sms_to'])

            post_mock.assert_called_once_with(
                test_client._config.TELESTAX_CONFIG['url'],
                headers=headers,
                data=test_client._get_sms_data(test_msg['Body'], test_msg['From'], test_msg['To'])
            )

            assert response['status'] == HTTPStatus.OK
            assert response['body'] == sms_success_response

    def send_to_sms_with_unauthorized_status_code_test(self):
        mock_logger = Mock()
        sms_from = '16666666666'
        sms_to = '17777777777'
        sms_body = 'This is a dummy SMS'
        test_msg = {
            'From': sms_from,
            'To': sms_to,
            'Body': sms_body
        }

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Basic QUNDT1VOVF9TSUQ6QVVUSF9UT0tFTg==',  # invalid token
            'Accept': 'text/plain'
        }

        msg_delivery_status = 401

        test_client = TeleStaxClient(config, mock_logger)
        test_client._logger.error = Mock()

        class ReponseHttp:
            status_code = msg_delivery_status
            text = 'Authentication failed'

        with patch.object(telestax_client.requests, 'post') as post_mock:
            post_mock.return_value = ReponseHttp()

            response = test_client.send_to_sms(sms_body, sms_to)

            post_mock.assert_called_once_with(
                test_client._config.TELESTAX_CONFIG['url'],
                headers=headers,
                data=test_client._get_sms_data(test_msg['Body'], test_msg['From'], test_msg['To'])
            )
            test_client._logger.error.assert_called_once()
            assert response['status'] == msg_delivery_status
            assert response['body'] == 'Authentication failed'

    def send_to_sms_with_error_500_status_code_test(self):
        mock_logger = Mock()
        sms_from = '16666666666'
        sms_to = '17777777777'
        sms_body = 'This is a dummy SMS'
        test_msg = {
            'From': sms_from,
            'To': sms_to,
            'Body': sms_body
        }

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Basic QUNDT1VOVF9TSUQ6QVVUSF9UT0tFTg==',
            'Accept': 'text/plain'
        }

        msg_delivery_status = {'status': 500, 'body': 'Error: SMS not sent, exception: mocked_error'}

        test_client = TeleStaxClient(config, mock_logger)
        test_client._logger.error = Mock()

        with patch.object(test_client, '_get_sms_data', side_effect=Exception("mocked_error")):
            response = test_client.send_to_sms(sms_body, sms_to)

        assert response == msg_delivery_status['body']
