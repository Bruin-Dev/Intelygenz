import json

from unittest.mock import call
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
        params = dict(client_id=123, ticket_id=321, ticket_status="New", category='SD-WAN', ticket_topic='VOO')

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

            tickets = bruin_client.get_all_tickets(params)

            mock_get.assert_called_once()
            assert mock_get.call_args[1]['params']['ClientId'] == params['client_id']
            assert mock_get.call_args[1]['params']['TicketId'] == params['ticket_id']
            assert mock_get.call_args[1]['params']['TicketStatus'] == params['ticket_status']
            assert mock_get.call_args[1]['params']['Category'] == params['category']
            assert mock_get.call_args[1]['params']['TicketTopic'] == params['ticket_topic']
            assert tickets['body'] == get_response['responses']
            assert tickets['status_code'] == 200

    def get_all_tickets_with_400_status_code_test(self):
        logger = Mock()
        logger.error = Mock()
        params = dict(client_id=123, ticket_id=321, ticket_status="New", category='SD-WAN', ticket_topic='VOO')
        error_response = {'error': "400 error"}
        response_mock = Mock()
        response_mock.json = Mock(return_value=error_response)
        response_mock.status_code = 400
        with patch.object(bruin_client_module.requests, 'get', return_value=response_mock):
            bruin_client = BruinClient(logger, config)
            bruin_client.login = Mock()
            bruin_client._bearer_token = "Someverysecretaccesstoken"

            tickets = bruin_client.get_all_tickets(params)

            logger.error.assert_called()

            assert tickets['body'] == error_response
            assert tickets['status_code'] == 400

    def get_all_tickets_with_401_status_code_test(self):
        logger = Mock()
        params = dict(client_id=123, ticket_id=321, ticket_status="New", category='SD-WAN', ticket_topic='VOO')

        response_mock = Mock()
        response_mock.json = Mock(return_value={})
        response_mock.status_code = 401
        with patch.object(bruin_client_module.requests, 'get', return_value=response_mock):
            bruin_client = BruinClient(logger, config)
            bruin_client.login = Mock()
            bruin_client._bearer_token = "Someverysecretaccesstoken"

            tickets = bruin_client.get_all_tickets(params)
            logger.error.assert_called()

            assert tickets['body'] == f"Maximum retries while relogin"
            assert tickets['status_code'] == 401

    def get_all_tickets_with_404_status_code_test(self):
        logger = Mock()
        logger.error = Mock()
        params = dict(client_id=123, ticket_id=321, ticket_status="New", category='SD-WAN', ticket_topic='VOO')
        error_response = {'error': "400 error"}
        response_mock = Mock()
        response_mock.json = Mock(return_value=error_response)
        response_mock.status_code = 404
        with patch.object(bruin_client_module.requests, 'get', return_value=response_mock):
            bruin_client = BruinClient(logger, config)
            bruin_client.login = Mock()
            bruin_client._bearer_token = "Someverysecretaccesstoken"

            tickets = bruin_client.get_all_tickets(params)

            logger.error.assert_called()

            assert tickets['body'] == "Resource not found"
            assert tickets['status_code'] == 404

    def get_all_tickets_with_500_status_code_test(self):
        logger = Mock()
        logger.error = Mock()
        params = dict(client_id=123, ticket_id=321, ticket_status="New", category='SD-WAN', ticket_topic='VOO')
        error_response = {'error': "400 error"}
        response_mock = Mock()
        response_mock.json = Mock(return_value=error_response)
        response_mock.status_code = 500
        with patch.object(bruin_client_module.requests, 'get', return_value=response_mock):
            bruin_client = BruinClient(logger, config)
            bruin_client.login = Mock()
            bruin_client._bearer_token = "Someverysecretaccesstoken"

            tickets = bruin_client.get_all_tickets(params)

            logger.error.assert_called()

            assert tickets['body'] == "Got internal error from Bruin"
            assert tickets['status_code'] == 500

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
            assert ticket_details["body"] == get_response
            assert ticket_details["status_code"] == 200

    def get_ticket_details_with_400_status_code_test(self):
        logger = Mock()
        logger.error = Mock()
        ticket_id = 321
        error_response = {'error': "400 error"}

        response_mock = Mock()
        response_mock.json = Mock(return_value=error_response)
        response_mock.status_code = 400
        with patch.object(bruin_client_module.requests, 'get', return_value=response_mock):
            bruin_client = BruinClient(logger, config)
            bruin_client.login = Mock()
            bruin_client._bearer_token = "Someverysecretaccesstoken"

            ticket_details = bruin_client.get_ticket_details(ticket_id)
            logger.error.assert_called()

            assert ticket_details['body'] == error_response
            assert ticket_details['status_code'] == 400

    def get_ticket_details_with_401_status_code_test(self):
        logger = Mock()
        logger.error = Mock()
        ticket_id = 321

        response_mock = Mock()
        response_mock.json = Mock(return_value={})
        response_mock.status_code = 401
        with patch.object(bruin_client_module.requests, 'get', return_value=response_mock):
            bruin_client = BruinClient(logger, config)
            bruin_client.login = Mock()
            bruin_client._bearer_token = "Someverysecretaccesstoken"

            ticket_details = bruin_client.get_ticket_details(ticket_id)
            bruin_client.login.assert_called()
            logger.error.assert_called()

            assert ticket_details['body'] == "Maximum retries while relogin"
            assert ticket_details['status_code'] == 401

    def get_ticket_details_with_404_status_code_test(self):
        logger = Mock()
        logger.error = Mock()
        ticket_id = 321

        response_mock = Mock()
        response_mock.json = Mock(return_value={})
        response_mock.status_code = 404
        with patch.object(bruin_client_module.requests, 'get', return_value=response_mock):
            bruin_client = BruinClient(logger, config)
            bruin_client.login = Mock()
            bruin_client._bearer_token = "Someverysecretaccesstoken"

            ticket_details = bruin_client.get_ticket_details(ticket_id)
            logger.error.assert_called()

            assert ticket_details['body'] == "Resource not found"
            assert ticket_details['status_code'] == 404

    def get_ticket_details_with_500_status_code_test(self):
        logger = Mock()
        logger.error = Mock()
        ticket_id = 321

        response_mock = Mock()
        response_mock.json = Mock(return_value={})
        response_mock.status_code = 500
        with patch.object(bruin_client_module.requests, 'get', return_value=response_mock):
            bruin_client = BruinClient(logger, config)
            bruin_client.login = Mock()
            bruin_client._bearer_token = "Someverysecretaccesstoken"

            ticket_details = bruin_client.get_ticket_details(ticket_id)
            logger.error.assert_called()

            assert ticket_details['body'] == "Got internal error from Bruin"
            assert ticket_details['status_code'] == 500

    def post_ticket_note_test(self):
        logger = Mock()
        logger.error = Mock()

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
            assert post_response["body"] == expected_post_response
            assert post_response["status_code"] == 200

    def post_ticket_note_with_400_status_code_test(self):
        logger = Mock()
        logger.error = Mock()
        ticket_id = 321
        note_contents = 'Ticket Notes'
        expected_post_response = {'response': 'Error 400'}

        response_mock = Mock()
        response_mock.json = Mock(return_value=expected_post_response)
        response_mock.status_code = 400
        with patch.object(bruin_client_module.requests, 'post', return_value=response_mock):
            bruin_client = BruinClient(logger, config)
            bruin_client.login = Mock()
            bruin_client._bearer_token = "Someverysecretaccesstoken"

            post_response = bruin_client.post_ticket_note(ticket_id, note_contents)
            logger.error.assert_called()

            assert post_response["body"] == expected_post_response
            assert post_response["status_code"] == 400

    def post_ticket_note_with_401_status_code_test(self):
        logger = Mock()
        ticket_id = 321
        note_contents = 'Ticket Notes'
        expected_post_response = {}

        response_mock = Mock()
        response_mock.json = Mock(return_value=expected_post_response)
        response_mock.status_code = 401
        with patch.object(bruin_client_module.requests, 'post', return_value=response_mock):
            bruin_client = BruinClient(logger, config)
            bruin_client.login = Mock()
            bruin_client._bearer_token = "Someverysecretaccesstoken"

            post_response = bruin_client.post_ticket_note(ticket_id, note_contents)

            bruin_client.login.assert_called()
            logger.error.assert_called()

            assert post_response["body"] == "Maximum retries while relogin"
            assert post_response["status_code"] == 401

    def post_ticket_note_with_404_status_code_test(self):
        logger = Mock()
        logger.error = Mock()

        ticket_id = 321
        note_contents = 'Ticket Notes'
        expected_post_response = {}

        response_mock = Mock()
        response_mock.json = Mock(return_value=expected_post_response)
        response_mock.status_code = 404
        with patch.object(bruin_client_module.requests, 'post', return_value=response_mock):
            bruin_client = BruinClient(logger, config)
            bruin_client.login = Mock()
            bruin_client._bearer_token = "Someverysecretaccesstoken"

            post_response = bruin_client.post_ticket_note(ticket_id, note_contents)
            logger.error.assert_called()

            assert post_response["body"] == "Resource not found"
            assert post_response["status_code"] == 404

    def post_ticket_note_with_500_status_code_test(self):
        logger = Mock()
        logger.error = Mock()
        ticket_id = 321
        note_contents = 'Ticket Notes'
        expected_post_response = {}

        response_mock = Mock()
        response_mock.json = Mock(return_value=expected_post_response)
        response_mock.status_code = 500
        with patch.object(bruin_client_module.requests, 'post', return_value=response_mock):
            bruin_client = BruinClient(logger, config)
            bruin_client.login = Mock()
            bruin_client._bearer_token = "Someverysecretaccesstoken"

            post_response = bruin_client.post_ticket_note(ticket_id, note_contents)
            logger.error.assert_called()

            assert post_response["body"] == "Got internal error from Bruin"
            assert post_response["status_code"] == 500

    def post_ticket_test(self):
        logger = Mock()
        payload = dict(clientId=321, category='Some Category', notes=['List of Notes'], services=['List of Services'],
                       contacts=['List of Contacts'])
        expected_post_response = 'Ticket Created'

        response_mock = Mock()
        response_mock.json = Mock(return_value=expected_post_response)
        response_mock.status_code = 200
        with patch.object(bruin_client_module.requests, 'post', return_value=response_mock) as mock_post:
            bruin_client = BruinClient(logger, config)
            bruin_client._bearer_token = "Someverysecretaccesstoken"
            post_ticket = bruin_client.post_ticket(payload)
            mock_post.assert_called_once()
            assert post_ticket['body'] == expected_post_response
            assert post_ticket['status_code'] == 200

    def post_ticket_400_status_test(self):
        logger = Mock()
        logger.error = Mock()
        payload = dict(clientId=321, category='Some Category', notes=['List of Notes'], services=['List of Services'],
                       contacts=['List of Contacts'])
        expected_post_response = 'Ticket failed to create'

        response_mock = Mock()
        response_mock.json = Mock(return_value=expected_post_response)
        response_mock.status_code = 400

        bruin_client = BruinClient(logger, config)
        bruin_client.login = Mock()
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(bruin_client_module.requests, 'post', return_value=response_mock):
            post_ticket = bruin_client.post_ticket(payload)
            logger.error.assert_called()

            assert post_ticket["body"] == expected_post_response
            assert post_ticket["status_code"] == 400

    def post_ticket_401_status_test(self):
        logger = Mock()
        logger.error = Mock()
        payload = dict(clientId=321, category='Some Category', notes=['List of Notes'], services=['List of Services'],
                       contacts=['List of Contacts'])
        expected_post_response = 'Ticket failed to create'

        response_mock = Mock()
        response_mock.json = Mock(return_value=expected_post_response)
        response_mock.status_code = 401

        bruin_client = BruinClient(logger, config)
        bruin_client.login = Mock()
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(bruin_client_module.requests, 'post', return_value=response_mock):
            post_ticket = bruin_client.post_ticket(payload)
            logger.error.assert_called()
            bruin_client.login.assert_called()
            assert post_ticket["body"] == "Maximum retries while relogin"
            assert post_ticket["status_code"] == 401

    def post_ticket_404_status_test(self):
        logger = Mock()
        logger.error = Mock()
        payload = dict(clientId=321, category='Some Category', notes=['List of Notes'], services=['List of Services'],
                       contacts=['List of Contacts'])
        expected_post_response = 'Ticket failed to create'

        response_mock = Mock()
        response_mock.json = Mock(return_value=expected_post_response)
        response_mock.status_code = 404

        bruin_client = BruinClient(logger, config)
        bruin_client.login = Mock()
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(bruin_client_module.requests, 'post', return_value=response_mock):
            post_ticket = bruin_client.post_ticket(payload)
            logger.error.assert_called()

            assert post_ticket["body"] == "Resource not found"
            assert post_ticket["status_code"] == 404

    def post_ticket_500_status_test(self):
        logger = Mock()
        logger.error = Mock()
        payload = dict(clientId=321, category='Some Category', notes=['List of Notes'], services=['List of Services'],
                       contacts=['List of Contacts'])
        expected_post_response = 'Ticket failed to create'

        response_mock = Mock()
        response_mock.json = Mock(return_value=expected_post_response)
        response_mock.status_code = 500

        bruin_client = BruinClient(logger, config)
        bruin_client.login = Mock()
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(bruin_client_module.requests, 'post', return_value=response_mock):
            post_ticket = bruin_client.post_ticket(payload)
            logger.error.assert_called()

            assert post_ticket["body"] == "Got internal error from Bruin"
            assert post_ticket["status_code"] == 500

    def update_ticket_status_test(self):
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
            assert update_ticket_status["body"] == successful_status_change
            assert update_ticket_status["status_code"] == 200

    def update_ticket_status_400_error_status_test(self):
        logger = Mock()
        logger.error = Mock()

        ticket_id = 123
        detail_id = 321
        ticket_status = 'X'
        failure_status_change = 'failed'

        response_mock = Mock()
        response_mock.json = Mock(return_value=failure_status_change)
        response_mock.status_code = 400

        bruin_client = BruinClient(logger, config)
        bruin_client.login = Mock()
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(bruin_client_module.requests, 'put', return_value=response_mock):
            update_ticket_status = bruin_client.update_ticket_status(ticket_id, detail_id, ticket_status)

            logger.error.assert_called()

            assert update_ticket_status["body"] == failure_status_change
            assert update_ticket_status["status_code"] == 400

    def update_ticket_status_401_error_status_test(self):
        logger = Mock()
        logger.error = Mock()

        ticket_id = 123
        detail_id = 321
        ticket_status = 'X'
        failure_status_change = 'failed'

        response_mock = Mock()
        response_mock.json = Mock(return_value=failure_status_change)
        response_mock.status_code = 401

        bruin_client = BruinClient(logger, config)
        bruin_client.login = Mock()
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(bruin_client_module.requests, 'put', return_value=response_mock):
            update_ticket_status = bruin_client.update_ticket_status(ticket_id, detail_id, ticket_status)

            logger.error.assert_called()
            bruin_client.login.assert_called()

            assert update_ticket_status["body"] == "Maximum retries while relogin"
            assert update_ticket_status["status_code"] == 401

    def update_ticket_status_404_error_status_test(self):
        logger = Mock()
        logger.error = Mock()

        ticket_id = 123
        detail_id = 321
        ticket_status = 'X'
        failure_status_change = 'failed'

        response_mock = Mock()
        response_mock.json = Mock(return_value=failure_status_change)
        response_mock.status_code = 404

        bruin_client = BruinClient(logger, config)
        bruin_client.login = Mock()
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(bruin_client_module.requests, 'put', return_value=response_mock):
            update_ticket_status = bruin_client.update_ticket_status(ticket_id, detail_id, ticket_status)

            logger.error.assert_called()

            assert update_ticket_status["body"] == "Resource not found"
            assert update_ticket_status["status_code"] == 404

    def update_ticket_status_500_error_status_test(self):
        logger = Mock()
        logger.error = Mock()

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
            update_ticket_status = bruin_client.update_ticket_status(ticket_id, detail_id, ticket_status)

            logger.error.assert_called()

            assert update_ticket_status["body"] == "Got internal error from Bruin"
            assert update_ticket_status["status_code"] == 500

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

    def get_management_status_with_ko_500_test(self):
        logger = Mock()

        filters = {
            "client_id": 9994,
            "service_number": "VC05400009999"
        }
        pascalized_filter = {
            "ClientId": 9994,
            "ServiceNumber": "VC05400009999"
        }

        response_500 = {
            "body": "Resource not found",
        }

        response_mock = Mock()
        response_mock.json = Mock(return_value=response_500)
        response_mock.status_code = 500

        with patch.object(bruin_client_module.requests, 'get', return_value=response_mock):
            bruin_client = BruinClient(logger, config)
            bruin_client.login = Mock()
            bruin_client._bearer_token = "Someverysecretaccesstoken"
            bruin_client.get_management_status(filters)
            bruin_client_module.requests.get.assert_called_with(
                f'{bruin_client._config.BRUIN_CONFIG["base_url"]}/api/Inventory/Attribute',
                headers=bruin_client._get_request_headers(),
                params=pascalized_filter,
                verify=False
            )

    def get_management_status_with_connection_error_test(self):
        logger = Mock()

        filters = {
            "client_id": 9994,
            "service_number": "VC05400009999"
        }
        pascalized_filter = {
            "ClientId": 9994,
            "ServiceNumber": "VC05400009999"
        }
        cause = "ERROR"

        message = {
            "body": f"Connection error in Bruin API. {cause}",
            "status_code": 500}

        with patch.object(bruin_client_module.requests, 'get', side_effect=ConnectionError(cause)):
            bruin_client = BruinClient(logger, config)
            bruin_client.login = Mock()
            bruin_client._bearer_token = "Someverysecretaccesstoken"
            result = bruin_client.get_management_status(filters)
            bruin_client_module.requests.get.assert_called_with(
                f'{bruin_client._config.BRUIN_CONFIG["base_url"]}/api/Inventory/Attribute',
                headers=bruin_client._get_request_headers(),
                params=pascalized_filter,
                verify=False
            )

            assert result == message


class TestPostOutageTicket:
    def post_outage_ticket_with_connection_error_test(self):
        client_id = 9994,
        service_number = "VC05400002265"
        connection_error_cause = 'Connection timed out'

        request_params = {
            'ClientID': client_id,
            'WTNs': [service_number],
            'RequestDescription': 'Automation Engine -- Service Outage Trouble'
        }

        logger = Mock()

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(bruin_client_module.requests, 'post', side_effect=ConnectionError(connection_error_cause)):
            result = bruin_client.post_outage_ticket(client_id, service_number)

            bruin_client_module.requests.post.assert_called_with(
                f'{config.BRUIN_CONFIG["base_url"]}/api/Ticket/repair',
                headers=bruin_client._get_request_headers(),
                json=request_params,
                verify=False
            )

        expected = {
            "body": f"Connection error in Bruin API. Cause: {connection_error_cause}",
            "status_code": 500
        }
        assert result == expected

    def post_outage_ticket_with_http_2XX_response_test(self):
        client_id = 9994,
        service_number = "VC05400002265"

        request_params = {
            'ClientID': client_id,
            'WTNs': [service_number],
            'RequestDescription': 'Automation Engine -- Service Outage Trouble'
        }

        ticket_data = {
            "ticketId": 4503440,
            "inventoryId": 12796795,
            "wtn": service_number,
            "errorMessage": None,
            "errorCode": 0,
        }
        bruin_response_body = {
            "assets": [ticket_data]
        }
        bruin_response_status_code = 200

        bruin_response = Mock()
        bruin_response.status_code = bruin_response_status_code
        bruin_response.json = Mock(return_value=bruin_response_body)

        logger = Mock()

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(bruin_client_module.requests, 'post', return_value=bruin_response):
            result = bruin_client.post_outage_ticket(client_id, service_number)

            bruin_client_module.requests.post.assert_called_with(
                f'{config.BRUIN_CONFIG["base_url"]}/api/Ticket/repair',
                headers=bruin_client._get_request_headers(),
                json=request_params,
                verify=False
            )

        expected = {
            "body": ticket_data,
            "status_code": bruin_response_status_code,
        }
        assert result == expected

    def post_outage_ticket_with_http_409_response_test(self):
        client_id = 9994,
        service_number = "VC05400002265"

        request_params = {
            'ClientID': client_id,
            'WTNs': [service_number],
            'RequestDescription': 'Automation Engine -- Service Outage Trouble'
        }

        ticket_data = {
            "ticketId": 4503440,
            "inventoryId": 12796795,
            "wtn": service_number,
            "errorMessage": "Ticket is in progress.",
            "errorCode": 409,
        }
        bruin_response_body = {
            "items": [ticket_data]
        }
        bruin_response_status_code = 200
        bruin_custom_status_code = 409

        bruin_response = Mock()
        bruin_response.status_code = bruin_response_status_code
        bruin_response.json = Mock(return_value=bruin_response_body)

        logger = Mock()

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(bruin_client_module.requests, 'post', return_value=bruin_response):
            result = bruin_client.post_outage_ticket(client_id, service_number)

            bruin_client_module.requests.post.assert_called_with(
                f'{config.BRUIN_CONFIG["base_url"]}/api/Ticket/repair',
                headers=bruin_client._get_request_headers(),
                json=request_params,
                verify=False
            )

        expected = {
            "body": ticket_data,
            "status_code": bruin_custom_status_code,
        }
        assert result == expected

    def post_outage_ticket_with_http_471_response_test(self):
        client_id = 9994,
        service_number = "VC05400002265"

        request_params = {
            'ClientID': client_id,
            'WTNs': [service_number],
            'RequestDescription': 'Automation Engine -- Service Outage Trouble'
        }

        ticket_data = {
            "ticketId": 4503440,
            "inventoryId": 12796795,
            "wtn": service_number,
            "errorMessage": "Ticket is resolved. Please unresolve it first.",
            "errorCode": 471,
        }
        bruin_response_body = {
            "assets": [ticket_data]
        }
        bruin_response_status_code = 200
        bruin_custom_status_code = 471

        bruin_response = Mock()
        bruin_response.status_code = bruin_response_status_code
        bruin_response.json = Mock(return_value=bruin_response_body)

        logger = Mock()

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(bruin_client_module.requests, 'post', return_value=bruin_response):
            result = bruin_client.post_outage_ticket(client_id, service_number)

            bruin_client_module.requests.post.assert_called_with(
                f'{config.BRUIN_CONFIG["base_url"]}/api/Ticket/repair',
                headers=bruin_client._get_request_headers(),
                json=request_params,
                verify=False
            )

        expected = {
            "body": ticket_data,
            "status_code": bruin_custom_status_code,
        }
        assert result == expected

    def post_outage_ticket_with_http_400_response_test(self):
        client_id = 9994,
        service_number = "VC05400002265"

        request_params = {
            'ClientID': client_id,
            'WTNs': [service_number],
            'RequestDescription': 'Automation Engine -- Service Outage Trouble'
        }

        bruin_response_body = {
            "errors": {
                "clientId": ["The value is not valid."]
            },
            "type": None,
            "title": "Invalid arguments to the API",
            "status": 400,
            "detail": "The inputs supplied to the API are invalid",
            "instance": "/api/Ticket/repair",
            "extensions": {}
        }
        bruin_response_status_code = 400

        bruin_response = Mock()
        bruin_response.status_code = bruin_response_status_code
        bruin_response.json = Mock(return_value=bruin_response_body)

        logger = Mock()

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(bruin_client_module.requests, 'post', return_value=bruin_response):
            result = bruin_client.post_outage_ticket(client_id, service_number)

            bruin_client_module.requests.post.assert_called_with(
                f'{config.BRUIN_CONFIG["base_url"]}/api/Ticket/repair',
                headers=bruin_client._get_request_headers(),
                json=request_params,
                verify=False
            )

        expected = {
            "body": bruin_response_body,
            "status_code": bruin_response_status_code,
        }
        assert result == expected

    def post_outage_ticket_with_http_401_response_test(self):
        client_id = 9994,
        service_number = "VC05400002265"

        request_params = {
            'ClientID': client_id,
            'WTNs': [service_number],
            'RequestDescription': 'Automation Engine -- Service Outage Trouble'
        }

        bruin_response_status_code = 401

        bruin_response = Mock()
        bruin_response.status_code = bruin_response_status_code

        logger = Mock()

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        bruin_client.login = Mock()

        with patch.object(bruin_client_module.requests, 'post', return_value=bruin_response):
            result = bruin_client.post_outage_ticket(client_id, service_number)

            post_outage_ticket_call = call(
                f'{config.BRUIN_CONFIG["base_url"]}/api/Ticket/repair',
                headers=bruin_client._get_request_headers(),
                json=request_params,
                verify=False
            )
            assert post_outage_ticket_call in bruin_client_module.requests.post.mock_calls

        bruin_client.login.assert_called()

        expected = {
            "body": "Maximum retries reached while re-login",
            "status_code": bruin_response_status_code,
        }
        assert result == expected

    def post_outage_ticket_with_http_403_response_test(self):
        client_id = 9994,
        service_number = "VC05400002265"

        request_params = {
            'ClientID': client_id,
            'WTNs': [service_number],
            'RequestDescription': 'Automation Engine -- Service Outage Trouble'
        }

        bruin_response_status_code = 403

        bruin_response = Mock()
        bruin_response.status_code = bruin_response_status_code

        logger = Mock()

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        bruin_client.login = Mock()

        with patch.object(bruin_client_module.requests, 'post', return_value=bruin_response):
            result = bruin_client.post_outage_ticket(client_id, service_number)

            bruin_client_module.requests.post.assert_called_once_with(
                f'{config.BRUIN_CONFIG["base_url"]}/api/Ticket/repair',
                headers=bruin_client._get_request_headers(),
                json=request_params,
                verify=False
            )

        expected = {
            "body": ("Permissions to create a new outage ticket with payload "
                     f"{json.dumps(request_params)} were not granted"),
            "status_code": bruin_response_status_code,
        }
        assert result == expected

    def post_outage_ticket_with_http_404_response_test(self):
        client_id = 9994,
        service_number = "VC05400002265"

        url = f'{config.BRUIN_CONFIG["base_url"]}/api/Ticket/repair'
        request_params = {
            'ClientID': client_id,
            'WTNs': [service_number],
            'RequestDescription': 'Automation Engine -- Service Outage Trouble'
        }

        bruin_response_status_code = 404

        bruin_response = Mock()
        bruin_response.status_code = bruin_response_status_code

        logger = Mock()

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        bruin_client.login = Mock()

        with patch.object(bruin_client_module.requests, 'post', return_value=bruin_response):
            result = bruin_client.post_outage_ticket(client_id, service_number)

            bruin_client_module.requests.post.assert_called_once_with(
                url,
                headers=bruin_client._get_request_headers(),
                json=request_params,
                verify=False
            )

        expected = {
            "body": f"Check mistypings in URL: {url}",
            "status_code": bruin_response_status_code,
        }
        assert result == expected

    def post_outage_ticket_with_http_5XX_response_test(self):
        client_id = 9994,
        service_number = "VC05400002265"

        request_params = {
            'ClientID': client_id,
            'WTNs': [service_number],
            'RequestDescription': 'Automation Engine -- Service Outage Trouble'
        }

        bruin_response_status_code = 500

        bruin_response = Mock()
        bruin_response.status_code = bruin_response_status_code

        logger = Mock()

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        bruin_client.login = Mock()

        with patch.object(bruin_client_module.requests, 'post', return_value=bruin_response):
            result = bruin_client.post_outage_ticket(client_id, service_number)

            post_outage_ticket_call = call(
                f'{config.BRUIN_CONFIG["base_url"]}/api/Ticket/repair',
                headers=bruin_client._get_request_headers(),
                json=request_params,
                verify=False
            )
            assert post_outage_ticket_call in bruin_client_module.requests.post.mock_calls

        expected = {
            "body": "Got internal error from Bruin",
            "status_code": bruin_response_status_code,
        }
        assert result == expected
