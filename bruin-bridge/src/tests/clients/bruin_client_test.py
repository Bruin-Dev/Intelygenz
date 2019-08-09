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

    def get_all_bruin_tickets_ok_test(self):
        logger = Mock()
        response = Mock()
        response.json = Mock(side_effect=[{"responses": [{"category": "SD-WAN", "ticketStatus": "New"}]},
                                          {"responses": [{"category": "SD-WAN", "ticketStatus": "In-Progress"}]}])
        response.status_code = 200
        requests.get = Mock(return_value=response)
        bruin_client = BruinClient(logger, config.BRUIN_CONFIG)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        tickets = bruin_client.get_all_tickets(123, '', ['New', 'In-Progress'], 'SD-WAN')
        assert requests.get.called
        assert requests.get.call_args[1]['params']['ClientId'] == 123
        assert requests.get.call_args[1]['params']['TicketId'] == ''
        assert requests.get.call_args[1]['params']['TicketStatus'] == "In-Progress"
        assert requests.get.call_args[1]['params']['Category'] == 'SD-WAN'
        assert tickets == [{'category': 'SD-WAN', 'ticketStatus': 'New'},
                           {"category": "SD-WAN", "ticketStatus": "In-Progress"}]

    def get_all_bruin_tickets_ko_test(self):
        logger = Mock()
        response = Mock()
        response.json = Mock(return_value={"responses": [{"category": "SD-WAN", "ticketStatus": "New"}]})
        response.status_code = 500
        requests.get = Mock(return_value=response)
        bruin_client = BruinClient(logger, config.BRUIN_CONFIG)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        tickets = bruin_client.get_all_tickets(123, '', ["New"], 'SD-WAN')
        assert requests.get.called
        assert requests.get.call_args[1]['params']['ClientId'] == 123
        assert requests.get.call_args[1]['params']['TicketId'] == ''
        assert requests.get.call_args[1]['params']['TicketStatus'] == "New"
        assert requests.get.call_args[1]['params']['Category'] == 'SD-WAN'
        assert tickets is None

    def get_all_bruin_tickets_details_ok_test(self):
        logger = Mock()
        response = Mock()
        response.json = Mock(return_value='Some Ticket Details')
        response.status_code = 200
        requests.get = Mock(return_value=response)
        bruin_client = BruinClient(logger, config.BRUIN_CONFIG)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        ticket_details = bruin_client.get_ticket_details(123)
        assert requests.get.called
        assert ticket_details == 'Some Ticket Details'

    def get_all_bruin_tickets_details_ko_test(self):
        logger = Mock()
        response = Mock()
        response.json = Mock(return_value='Some Ticket Details')
        response.status_code = 500
        requests.get = Mock(return_value=response)
        bruin_client = BruinClient(logger, config.BRUIN_CONFIG)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        ticket_details = bruin_client.get_ticket_details(123)
        assert requests.get.called
        assert ticket_details is None

    def post_ticket_note_ok_test(self):
        logger = Mock()
        response = Mock()
        response.json = Mock(return_value='Note appended')
        response.status_code = 200
        requests.post = Mock(return_value=response)
        bruin_client = BruinClient(logger, config.BRUIN_CONFIG)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        ticket_details = bruin_client.post_ticket_note(123, 'Ticket Notes')
        assert requests.post.called
        assert requests.post.call_args[1]['json']['note'] == 'Ticket Notes'
        assert ticket_details == 'Note appended'

    def post_ticket_note_ko_test(self):
        logger = Mock()
        response = Mock()
        response.json = Mock(return_value='Note appended')
        response.status_code = 500
        requests.post = Mock(return_value=response)
        bruin_client = BruinClient(logger, config.BRUIN_CONFIG)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        ticket_details = bruin_client.post_ticket_note(123, 'Ticket Notes')
        assert requests.post.called
        assert requests.post.call_args[1]['json']['note'] == 'Ticket Notes'
        assert ticket_details is None
