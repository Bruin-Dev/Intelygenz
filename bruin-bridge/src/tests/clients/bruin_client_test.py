from unittest.mock import Mock
import requests

from application.clients.bruin_client import BruinClient
from config import testconfig as config
from pytest import raises


class TestBruinClient:

    def instance_test(self):
        logger = Mock()
        bruin_client = BruinClient(logger, config.BRUIN_CONFIG)
        assert bruin_client._logger is logger
        assert bruin_client._config is config.BRUIN_CONFIG

    def login_ok_test(self):
        logger = Mock()
        response = Mock()
        response.json = Mock(return_value={"access_token": "Someverysecretaccesstoken"})
        requests.post = Mock(return_value=response)
        bruin_client = BruinClient(logger, config.BRUIN_CONFIG)
        bruin_client.login()
        assert "Someverysecretaccesstoken" in bruin_client._bearer_token
        assert requests.post.called

    def login_ko_test(self):
        logger = Mock()
        response = Mock()
        response.json = Mock()
        requests.post = Mock(return_value=response)
        bruin_client = BruinClient(logger, config.BRUIN_CONFIG)
        bruin_client.login()
        assert bruin_client._bearer_token == ""
        assert requests.post.called

    def get_request_header_ok_test(self):
        logger = Mock()
        response = Mock()
        response.json = Mock(return_value={"access_token": "Someverysecretaccesstoken"})
        requests.post = Mock(return_value=response)
        bruin_client = BruinClient(logger, config.BRUIN_CONFIG)
        bruin_client.login()
        header = bruin_client._get_request_headers()
        assert header == {"authorization": f"Bearer Someverysecretaccesstoken",
                          "Content-Type": "application/json-patch+json"}

    def get_request_header_ko_test(self):
        logger = Mock()
        response = Mock()
        response.json = Mock()
        requests.post = Mock(return_value=response)
        bruin_client = BruinClient(logger, config.BRUIN_CONFIG)
        bruin_client.login()
        with raises(Exception) as error_info:
            header = bruin_client._get_request_headers()
            assert error_info == "Missing BEARER token"

    def get_all_filtered_bruin_tickets_test(self):
        logger = Mock()
        response = Mock()
        response.json = Mock(return_value={"responses": [{"category": "SD-WAN", "ticketStatus": "Unopened"}]})
        response.status_code = 200
        requests.get = Mock(return_value=response)
        bruin_client = BruinClient(logger, config.BRUIN_CONFIG)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        filtered_tickets = bruin_client.get_all_filtered_tickets(123, '')
        assert requests.get.called
        assert requests.get.call_args[1]['params']['ClientId'] == 123
        assert requests.get.call_args[1]['params']['TicketId'] == ''
        assert filtered_tickets == [{"category": "SD-WAN", "ticketStatus": "Unopened"}]

    def get_all_filtered_bruin_tickets_resolved_test(self):
        logger = Mock()
        response = Mock()
        response.json = Mock(return_value={"responses": [{"category": "SD-WAN", "ticketStatus": "Resolved"}]})
        response.status_code = 200
        requests.get = Mock(return_value=response)
        bruin_client = BruinClient(logger, config.BRUIN_CONFIG)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        filtered_tickets = bruin_client.get_all_filtered_tickets(123, 321)
        assert requests.get.called
        assert requests.get.call_args[1]['params']['ClientId'] == 123
        assert requests.get.call_args[1]['params']['TicketId'] == 321
        assert filtered_tickets == []
