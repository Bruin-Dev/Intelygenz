from unittest.mock import Mock
import requests

from application.clients.bruin_client import BruinClient
from config import testconfig as config
from pytest import raises
from tenacity import RetryError


class TestBruinClient:

    def instance_test(self):
        logger = Mock()
        bruin_client = BruinClient(logger, config)
        assert bruin_client._logger is logger
        assert bruin_client._config is config

    def login_ok_test(self):
        logger = Mock()
        response = Mock()
        response.json = Mock(return_value={"access_token": "Someverysecretaccesstoken"})
        requests.post = Mock(return_value=response)
        bruin_client = BruinClient(logger, config)
        bruin_client.login()
        assert "Someverysecretaccesstoken" in bruin_client._bearer_token
        assert requests.post.called

    def login_ko_test(self):
        logger = Mock()
        response = Mock()
        response.json = Mock()
        requests.post = Mock(return_value=response)
        bruin_client = BruinClient(logger, config)
        bruin_client.login()
        assert bruin_client._bearer_token == ""
        assert requests.post.called

    def get_request_header_ok_test(self):
        logger = Mock()
        response = Mock()
        response.json = Mock(return_value={"access_token": "Someverysecretaccesstoken"})
        requests.post = Mock(return_value=response)
        bruin_client = BruinClient(logger, config)
        bruin_client.login()
        header = bruin_client._get_request_headers()
        assert header == {"authorization": f"Bearer Someverysecretaccesstoken",
                          "Content-Type": "application/json-patch+json",
                          "Cache-control": "no-cache, no-store, no-transform, max-age=0, only-if-cached",
                          }

    def get_request_header_ko_test(self):
        logger = Mock()
        response = Mock()
        response.json = Mock()
        requests.post = Mock(return_value=response)
        bruin_client = BruinClient(logger, config)
        bruin_client.login()
        with raises(Exception) as error_info:
            header = bruin_client._get_request_headers()
            assert error_info == "Missing BEARER token"

    def get_all_bruin_tickets_ok_test(self):
        logger = Mock()
        response = Mock()
        response.json = Mock(return_value={"responses": [{"category": "SD-WAN", "ticketStatus": "New"}]})
        response.status_code = 200
        requests.get = Mock(return_value=response)
        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        tickets = bruin_client.get_all_tickets(123, '', 'New', 'SD-WAN')
        assert requests.get.called
        assert requests.get.call_args[1]['params']['ClientId'] == 123
        assert requests.get.call_args[1]['params']['TicketId'] == ''
        assert requests.get.call_args[1]['params']['TicketStatus'] == "New"
        assert requests.get.call_args[1]['params']['Category'] == 'SD-WAN'
        assert tickets == [{'category': 'SD-WAN', 'ticketStatus': 'New'}]

    def get_all_bruin_tickets_ko_test(self):
        logger = Mock()
        response = Mock()
        response.json = Mock(return_value={"responses": [{"category": "SD-WAN", "ticketStatus": "New"}]})
        response.status_code = 500
        requests.get = Mock(return_value=response)
        bruin_client = BruinClient(logger, config)
        bruin_client.login = Mock()
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        tickets = None
        try:
            tickets = bruin_client.get_all_tickets(123, '', "New", 'SD-WAN')
        except Exception as e:
            error = e
        assert isinstance(error, RetryError)
        assert bruin_client.login.called
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
        bruin_client = BruinClient(logger, config)
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
        bruin_client = BruinClient(logger, config)
        bruin_client.login = Mock()
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        ticket_details = None
        try:
            ticket_details = bruin_client.get_ticket_details(123)
        except Exception as e:
            error = e
        assert isinstance(error, RetryError)
        assert bruin_client.login.called
        assert requests.get.called
        assert ticket_details is None

    def post_ticket_note_ok_test(self):
        logger = Mock()
        response = Mock()
        response.json = Mock(return_value='Note appended')
        response.status_code = 200
        requests.post = Mock(return_value=response)
        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        post_ticket = bruin_client.post_ticket_note(123, 'Ticket Notes')
        assert requests.post.called
        assert requests.post.call_args[1]['json']['note'] == 'Ticket Notes'
        assert post_ticket == 'Note appended'

    def post_ticket_note_ko_test(self):
        logger = Mock()
        response = Mock()
        response.json = Mock(return_value='Note appended')
        response.status_code = 500
        requests.post = Mock(return_value=response)
        bruin_client = BruinClient(logger, config)
        bruin_client.login = Mock()
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        post_ticket = None
        try:
            post_ticket = bruin_client.post_ticket_note(123, 'Ticket Notes')
        except Exception as e:
            error = e
        assert isinstance(error, RetryError)
        assert requests.post.called
        assert requests.post.call_args[1]['json']['note'] == 'Ticket Notes'
        assert post_ticket is None

    def post_ticket_ok_test(self):
        logger = Mock()
        response = Mock()
        response.json = Mock(return_value='Ticket Created')
        response.status_code = 200
        requests.post = Mock(return_value=response)
        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        post_ticket = bruin_client.post_ticket(123, 'Some Category', ['Services'], ['Notes'], ['Contacts'])
        assert requests.post.called
        assert requests.post.call_args[1]['json']['clientId'] == 123
        assert requests.post.call_args[1]['json']['category'] == 'Some Category'
        assert requests.post.call_args[1]['json']['services'] == ['Services']
        assert requests.post.call_args[1]['json']['notes'] == ['Notes']
        assert requests.post.call_args[1]['json']['contacts'] == ['Contacts']
        assert post_ticket == 'Ticket Created'

    def post_ticket_ko_test(self):
        logger = Mock()
        response = Mock()
        response.json = Mock(return_value='Ticket Created')
        response.status_code = 500
        requests.post = Mock(return_value=response)
        bruin_client = BruinClient(logger, config)
        bruin_client.login = Mock()
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        post_ticket = None
        try:
            post_ticket = bruin_client.post_ticket(123, 'Some Category', ['Services'], ['Notes'], ['Contacts'])
        except Exception as e:
            error = e
        assert isinstance(error, RetryError)
        assert requests.post.called
        assert requests.post.call_args[1]['json']['clientId'] == 123
        assert requests.post.call_args[1]['json']['category'] == 'Some Category'
        assert requests.post.call_args[1]['json']['services'] == ['Services']
        assert requests.post.call_args[1]['json']['notes'] == ['Notes']
        assert requests.post.call_args[1]['json']['contacts'] == ['Contacts']
        assert post_ticket is None
