from unittest.mock import Mock
from unittest.mock import patch

from application.clients.bruin_client import BruinClient
from pytest import raises

from application.clients import bruin_client as bruin_client_module
from config import testconfig as config


class TestBruinClient:

    def instance_test(self):
        logger = Mock()

        bruin_client = BruinClient(logger, config)

        assert bruin_client._logger is logger
        assert bruin_client._config is config

    def login_test(self):
        logger = Mock()
        access_token_str = "Someverysecretaccesstoken"

        response_mock = Mock()
        response_mock.json = Mock(return_value={"access_token": "Someverysecretaccesstoken"})
        with patch.object(bruin_client_module.requests, 'post', return_value=response_mock) as mock_post:
            bruin_client = BruinClient(logger, config)
            bruin_client.login()

            assert access_token_str in bruin_client._bearer_token
            mock_post.assert_called_once()

    def login_with_failure_test(self):
        logger = Mock()

        with patch.object(bruin_client_module.requests, 'post', side_effect=Exception) as mock_post:
            bruin_client = BruinClient(logger, config)
            bruin_client.login()

            assert bruin_client._bearer_token == ''
            mock_post.assert_called_once()

    def get_request_headers_test(self):
        logger = Mock()
        access_token_str = "Someverysecretaccesstoken"
        expected_headers = {
            "authorization": f"Bearer {access_token_str}",
            "Content-Type": "application/json-patch+json",
            "Cache-control": "no-cache, no-store, no-transform, max-age=0, only-if-cached",
        }

        response_mock = Mock()
        response_mock.json = Mock(return_value={"access_token": "Someverysecretaccesstoken"})
        with patch.object(bruin_client_module.requests, 'post', return_value=response_mock) as mock_post:
            bruin_client = BruinClient(logger, config)
            bruin_client.login()

            assert access_token_str in bruin_client._bearer_token
            mock_post.assert_called_once()

        headers = bruin_client._get_request_headers()
        assert headers == expected_headers

    def get_request_headers_with_no_bearer_token_test(self):
        logger = Mock()

        bruin_client = BruinClient(logger, config)
        with raises(Exception) as error_info:
            bruin_client._get_request_headers()
            assert error_info == "Missing BEARER token"

    def get_all_tickets_test(self):
        logger = Mock()
        client_id = 123
        ticket_id = 321
        ticket_status = "New"
        category = 'SD-WAN'
        ticket_topic = 'VOO'
        get_response = {
            "responses": [
                {"category": "SD-WAN", "ticketStatus": "New"}
            ]
        }

        response_mock = Mock()
        response_mock.json = Mock(return_value=get_response)
        response_mock.status_code = 200
        with patch.object(bruin_client_module.requests, 'get', return_value=response_mock) as mock_get:
            bruin_client = BruinClient(logger, config)
            bruin_client._bearer_token = "Someverysecretaccesstoken"

            tickets = bruin_client.get_all_tickets(client_id, ticket_id, ticket_status, category, ticket_topic)

            mock_get.assert_called_once()
            assert mock_get.call_args[1]['params']['ClientId'] == client_id
            assert mock_get.call_args[1]['params']['TicketId'] == ticket_id
            assert mock_get.call_args[1]['params']['TicketStatus'] == ticket_status
            assert mock_get.call_args[1]['params']['Category'] == category
            assert mock_get.call_args[1]['params']['TicketTopic'] == ticket_topic
            assert tickets == get_response['responses']

    def get_all_tickets_with_bad_status_code_test(self):
        logger = Mock()
        client_id = 123
        ticket_id = 321
        ticket_status = "New"
        category = 'SD-WAN'
        ticket_topic = 'VOO'

        response_mock = Mock()
        response_mock.json = Mock(return_value={})
        response_mock.status_code = 404
        with patch.object(bruin_client_module.requests, 'get', return_value=response_mock):
            bruin_client = BruinClient(logger, config)
            bruin_client.login = Mock()
            bruin_client._bearer_token = "Someverysecretaccesstoken"

            with raises(Exception):
                bruin_client.get_all_tickets(client_id, ticket_id, ticket_status, category, ticket_topic)

            bruin_client.login.assert_called()

    def get_ticket_details_test(self):
        logger = Mock()
        ticket_id = 321
        get_response = {'ticket_details': 'Some Ticket Details'}

        response_mock = Mock()
        response_mock.json = Mock(return_value=get_response)
        response_mock.status_code = 200
        with patch.object(bruin_client_module.requests, 'get', return_value=response_mock) as mock_get:
            bruin_client = BruinClient(logger, config)
            bruin_client._bearer_token = "Someverysecretaccesstoken"
            ticket_details = bruin_client.get_ticket_details(ticket_id)

            mock_get.assert_called_once()
            assert ticket_details == get_response

    def get_ticket_details_with_bad_status_code_test(self):
        logger = Mock()
        ticket_id = 321
        get_response = {'ticket_details': 'Some Ticket Details'}

        response_mock = Mock()
        response_mock.json = Mock(return_value=get_response)
        response_mock.status_code = 404
        with patch.object(bruin_client_module.requests, 'get', return_value=response_mock):
            bruin_client = BruinClient(logger, config)
            bruin_client.login = Mock()
            bruin_client._bearer_token = "Someverysecretaccesstoken"

            with raises(Exception):
                bruin_client.get_ticket_details(ticket_id)

            bruin_client.login.assert_called()

    def post_ticket_note_test(self):
        logger = Mock()
        ticket_id = 321
        note_contents = 'Ticket Notes'
        expected_post_response = {'response': 'Note Appended'}

        response_mock = Mock()
        response_mock.json = Mock(return_value=expected_post_response)
        response_mock.status_code = 200
        with patch.object(bruin_client_module.requests, 'post', return_value=response_mock) as mock_post:
            bruin_client = BruinClient(logger, config)
            bruin_client._bearer_token = "Someverysecretaccesstoken"
            post_response = bruin_client.post_ticket_note(ticket_id, note_contents)

            mock_post.assert_called_once()
            assert post_response == expected_post_response

    def post_ticket_note_with_bad_status_code_test(self):
        logger = Mock()
        ticket_id = 321
        note_contents = 'Ticket Notes'
        expected_post_response = {'response': 'Note Appended'}

        response_mock = Mock()
        response_mock.json = Mock(return_value=expected_post_response)
        response_mock.status_code = 404
        with patch.object(bruin_client_module.requests, 'post', return_value=response_mock):
            bruin_client = BruinClient(logger, config)
            bruin_client.login = Mock()
            bruin_client._bearer_token = "Someverysecretaccesstoken"

            with raises(Exception):
                bruin_client.post_ticket_note(ticket_id, note_contents)

            bruin_client.login.assert_called()

    def post_ticket_ok_test(self):
        logger = Mock()
        client_id = 321
        category = 'Some Category'
        notes = ['List of Notes']
        services = ['List of Services']
        contacts = ['List of Contacts']
        expected_post_response = 'Ticket Created'

        response_mock = Mock()
        response_mock.json = Mock(return_value=expected_post_response)
        response_mock.status_code = 200
        with patch.object(bruin_client_module.requests, 'post', return_value=response_mock) as mock_post:
            bruin_client = BruinClient(logger, config)
            bruin_client._bearer_token = "Someverysecretaccesstoken"
            post_ticket = bruin_client.post_ticket(client_id, category, services, notes, contacts)
            mock_post.assert_called_once()
            assert post_ticket == expected_post_response

    def post_ticket_ko_test(self):
        logger = Mock()
        client_id = 321
        category = 'Some Category'
        notes = ['List of Notes']
        services = ['List of Services']
        contacts = ['List of Contacts']
        expected_post_response = 'Ticket Created'

        response_mock = Mock()
        response_mock.json = Mock(return_value=expected_post_response)
        response_mock.status_code = 500

        bruin_client = BruinClient(logger, config)
        bruin_client.login = Mock()
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(bruin_client_module.requests, 'post', return_value=response_mock):
            with raises(Exception):
                post_ticket = bruin_client.post_ticket(client_id, category, services, notes, contacts)
                assert post_ticket is None
            bruin_client.login.assert_called()

    def update_ticket__status_ok_test(self):
        logger = Mock()

        ticket_id = 123
        detail_id = 321
        ticket_status = 'O'
        successful_status_change = 'Success'

        response_mock = Mock()
        response_mock.json = Mock(return_value=successful_status_change)
        response_mock.status_code = 200
        with patch.object(bruin_client_module.requests, 'put', return_value=response_mock) as mock_put:
            bruin_client = BruinClient(logger, config)
            bruin_client._bearer_token = "Someverysecretaccesstoken"
            update_ticket_status = bruin_client.update_ticket_status(ticket_id, detail_id, ticket_status)
            mock_put.assert_called_once()
            assert update_ticket_status == successful_status_change

    def update_ticket_status_ko_test(self):
        logger = Mock()

        ticket_id = 123
        detail_id = 321
        ticket_status = 'X'
        failure_status_change = 'failed'

        response_mock = Mock()
        response_mock.json = Mock(return_value=failure_status_change)
        response_mock.status_code = 500

        bruin_client = BruinClient(logger, config)
        bruin_client.login = Mock()
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(bruin_client_module.requests, 'put', return_value=response_mock):
            with raises(Exception):
                update_ticket_status = bruin_client.update_ticket_status(ticket_id, detail_id, ticket_status)
                assert update_ticket_status is None
            bruin_client.login.assert_called()

    def get_management_status_pascalize_with_ok_test(self):
        logger = Mock()

        filters = {
            "client_id": 9994,
            "status": "A",
            "service_number": "VC05400009999"
        }
        pascalized_filter = {
            "ClientId": 9994,
            "Status": "A",
            "ServiceNumber": "VC05400009999"
        }

        valid_management_status = {
            "inventoryId": "12796795",
            "serviceNumber": "VC05400002265",
            "attributes": [
                {
                    "key": "Management Status",
                    "value": "Active – Platinum Monitoring"
                }
            ]
        }

        response_mock = Mock()
        response_mock.json = Mock(return_value=valid_management_status)
        response_mock.status_code = 200

        with patch.object(bruin_client_module.requests, 'get', return_value=response_mock):
            bruin_client = BruinClient(logger, config)
            bruin_client.login = Mock()
            bruin_client._bearer_token = "Someverysecretaccesstoken"
            bruin_client.get_management_status(filters)
            bruin_client_module.requests.get.assert_called_once_with(
                f'{bruin_client._config.BRUIN_CONFIG["base_url"]}/api/Inventory/Attribute',
                headers=bruin_client._get_request_headers(),
                params=pascalized_filter,
                verify=False
            )
            response_mock.json.assert_called_once()

    def get_management_status_with_ko_401_test(self):
        logger = Mock()

        filters = {
            "client_id": 9994,
            "status": "A",
            "service_number": "VC05400009999"
        }
        pascalized_filter = {
            "ClientId": 9994,
            "Status": "A",
            "ServiceNumber": "VC05400009999"
        }

        empty_response = {}

        response_mock = Mock()
        response_mock.json = Mock(return_value=empty_response)
        response_mock.status_code = 401

        with patch.object(bruin_client_module.requests, 'get', return_value=response_mock):
            bruin_client = BruinClient(logger, config)
            bruin_client.login = Mock()
            bruin_client._bearer_token = "Someverysecretaccesstoken"
            with raises(Exception):
                bruin_client.get_management_status(filters)
                bruin_client_module.requests.get.assert_called_once_with(
                    f'{bruin_client._config.BRUIN_CONFIG["base_url"]}/api/Inventory/Attribute',
                    headers=bruin_client._get_request_headers(),
                    params=pascalized_filter,
                    verify=False
                )
                self.assertRaises(Exception, bruin_client.get_management_status)
                bruin_client.login.assert_called()

    def get_management_status_with_ko_400_test(self):
        logger = Mock()

        filters = {
            "client_id": 9994,
            "service_number": "VC05400009999"
        }
        pascalized_filter = {
            "ClientId": 9994,
            "ServiceNumber": "VC05400009999"
        }

        response_400 = {
            "message": "Please provide valid ClientId, Status and ServiceNumber.",
            "messageDetail": None,
            "data": None,
            "type": "ValidationException",
            "code": 400
        }

        response_mock = Mock()
        response_mock.json = Mock(return_value=response_400)
        response_mock.status_code = 400

        with patch.object(bruin_client_module.requests, 'get', return_value=response_mock):
            bruin_client = BruinClient(logger, config)
            bruin_client.login = Mock()
            bruin_client._bearer_token = "Someverysecretaccesstoken"
            bruin_client.get_management_status(filters)
            bruin_client_module.requests.get.assert_called_once_with(
                f'{bruin_client._config.BRUIN_CONFIG["base_url"]}/api/Inventory/Attribute',
                headers=bruin_client._get_request_headers(),
                params=pascalized_filter,
                verify=False
            )
