import json
from unittest.mock import Mock
from unittest.mock import call
from unittest.mock import patch

import humps
from pytest import raises

from application.clients import bruin_client as bruin_client_module
from application.clients.bruin_client import BruinClient
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
            assert tickets['status'] == 200

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
            assert tickets['status'] == 400

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
            assert tickets['status'] == 401

    def get_all_tickets_with_403_status_code_test(self):
        logger = Mock()
        logger.error = Mock()
        params = dict(client_id=123, ticket_id=321, ticket_status="New", category='SD-WAN', ticket_topic='VOO')
        error_response = {'error': "403 error"}
        response_mock = Mock()
        response_mock.json = Mock(return_value=error_response)
        response_mock.status_code = 403
        with patch.object(bruin_client_module.requests, 'get', return_value=response_mock):
            bruin_client = BruinClient(logger, config)
            bruin_client.login = Mock()
            bruin_client._bearer_token = "Someverysecretaccesstoken"

            tickets = bruin_client.get_all_tickets(params)

            logger.error.assert_called()

            assert tickets['body'] == error_response
            assert tickets['status'] == 403

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
            assert tickets['status'] == 404

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
            assert tickets['status'] == 500

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
            assert ticket_details["status"] == 200

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
            assert ticket_details['status'] == 400

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
            assert ticket_details['status'] == 401

    def get_ticket_details_with_403_status_code_test(self):
        logger = Mock()
        logger.error = Mock()
        ticket_id = 321
        error_response = {'error': "403 error"}

        response_mock = Mock()
        response_mock.json = Mock(return_value=error_response)
        response_mock.status_code = 403
        with patch.object(bruin_client_module.requests, 'get', return_value=response_mock):
            bruin_client = BruinClient(logger, config)
            bruin_client.login = Mock()
            bruin_client._bearer_token = "Someverysecretaccesstoken"

            ticket_details = bruin_client.get_ticket_details(ticket_id)
            logger.error.assert_called()

            assert ticket_details['body'] == error_response
            assert ticket_details['status'] == 403

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
            assert ticket_details['status'] == 404

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
            assert ticket_details['status'] == 500

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
            assert post_response["status"] == 200

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
            assert post_response["status"] == 400

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
            assert post_response["status"] == 401

    def post_ticket_note_with_403_status_code_test(self):
        logger = Mock()
        logger.error = Mock()
        ticket_id = 321
        note_contents = 'Ticket Notes'
        expected_post_response = {'response': 'Error 403'}

        response_mock = Mock()
        response_mock.json = Mock(return_value=expected_post_response)
        response_mock.status_code = 403
        with patch.object(bruin_client_module.requests, 'post', return_value=response_mock):
            bruin_client = BruinClient(logger, config)
            bruin_client.login = Mock()
            bruin_client._bearer_token = "Someverysecretaccesstoken"

            post_response = bruin_client.post_ticket_note(ticket_id, note_contents)
            logger.error.assert_called()

            assert post_response["body"] == expected_post_response
            assert post_response["status"] == 403

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
            assert post_response["status"] == 404

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
            assert post_response["status"] == 500

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
            assert post_ticket['status'] == 200

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
            assert post_ticket["status"] == 400

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
            assert post_ticket["status"] == 401

    def post_ticket_403_status_test(self):
        logger = Mock()
        logger.error = Mock()
        payload = dict(clientId=321, category='Some Category', notes=['List of Notes'], services=['List of Services'],
                       contacts=['List of Contacts'])
        expected_post_response = 'Ticket failed to create'

        response_mock = Mock()
        response_mock.json = Mock(return_value=expected_post_response)
        response_mock.status_code = 403

        bruin_client = BruinClient(logger, config)
        bruin_client.login = Mock()
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(bruin_client_module.requests, 'post', return_value=response_mock):
            post_ticket = bruin_client.post_ticket(payload)
            logger.error.assert_called()

            assert post_ticket["body"] == expected_post_response
            assert post_ticket["status"] == 403

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
            assert post_ticket["status"] == 404

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
            assert post_ticket["status"] == 500

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
            assert update_ticket_status["status"] == 200

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
            assert update_ticket_status["status"] == 400

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
            assert update_ticket_status["status"] == 401

    def update_ticket_status_403_error_status_test(self):
        logger = Mock()
        logger.error = Mock()

        ticket_id = 123
        detail_id = 321
        ticket_status = 'X'
        failure_status_change = 'failed'

        response_mock = Mock()
        response_mock.json = Mock(return_value=failure_status_change)
        response_mock.status_code = 403

        bruin_client = BruinClient(logger, config)
        bruin_client.login = Mock()
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(bruin_client_module.requests, 'put', return_value=response_mock):
            update_ticket_status = bruin_client.update_ticket_status(ticket_id, detail_id, ticket_status)

            logger.error.assert_called()

            assert update_ticket_status["body"] == failure_status_change
            assert update_ticket_status["status"] == 403

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
            assert update_ticket_status["status"] == 404

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
            assert update_ticket_status["status"] == 500

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

    def get_management_status_with_ko_403_test(self):
        logger = Mock()

        filters = {
            "client_id": 9994,
            "service_number": "VC05400009999"
        }
        pascalized_filter = {
            "ClientId": 9994,
            "ServiceNumber": "VC05400009999"
        }

        response_403 = {
            "message": "Please provide valid ClientId, Status and ServiceNumber.",
            "messageDetail": None,
            "data": None,
            "type": "ValidationException",
            "code": 403
        }

        response_mock = Mock()
        response_mock.json = Mock(return_value=response_403)
        response_mock.status_code = 403

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
            "status": 500}

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

    def get_possible_detail_next_result_200_test(self):
        logger = Mock()

        ticket_id = 99
        filters = {
            "ticket_id": ticket_id,
            "ServiceNumber": "VCO10199919",
            "DetailId": 191919
        }

        valid_next_result = {
            "currentTaskId": 10398903,
            "currentTaskKey": "344",
            "currentTaskName": "Holmdel NOC Investigate ",
            "nextResults": [
                {
                    "resultTypeId": 139,
                    "resultName": "Repair Completed",
                    "notes": [
                        {
                            "noteType": "RFO",
                            "noteDescription": "Reason for Outage",
                            "availableValueOptions": [
                                {
                                    "text": "Area Wide Outage",
                                    "value": "Area Wide Outage"
                                },
                            ]
                        }
                    ]
                }
            ]
        }

        expected_result = {
            "body": valid_next_result,
            "status_code": 200
        }

        response_mock = Mock()
        response_mock.json = Mock(return_value=valid_next_result)
        response_mock.status_code = 200

        with patch.object(bruin_client_module.requests, 'get', return_value=response_mock):
            bruin_client = BruinClient(logger, config)
            bruin_client.login = Mock()
            bruin_client._bearer_token = "Someverysecretaccesstoken"
            next_result = bruin_client.get_possible_detail_next_result(filters)
            bruin_client_module.requests.get.assert_called_once_with(
                f'{bruin_client._config.BRUIN_CONFIG["base_url"]}/api/Ticket/{ticket_id}/nextresult',
                headers=bruin_client._get_request_headers(),
                params=filters,
                verify=False
            )
            response_mock.json.assert_called_once()
            assert next_result == expected_result

    def get_possible_detail_next_result_400_test(self):
        logger = Mock()
        logger.error = Mock()

        ticket_id = 99
        filters = {
            "ticket_id": ticket_id,
            "ServiceNumber": "",
            "DetailId": None
        }

        response_400 = {
            "message": "Ticket Detail not found",
            "messageDetail": None,
            "data": None,
            "type": "ValidationException",
            "code": 400
        }

        expected_result = {
            "body": response_400,
            "status_code": 400
        }

        response_mock = Mock()
        response_mock.json = Mock(return_value=response_400)
        response_mock.status_code = 400

        with patch.object(bruin_client_module.requests, 'get', return_value=response_mock):
            bruin_client = BruinClient(logger, config)
            bruin_client.login = Mock()
            bruin_client._bearer_token = "Someverysecretaccesstoken"
            next_result = bruin_client.get_possible_detail_next_result(filters)
            bruin_client_module.requests.get.assert_called_once_with(
                f'{bruin_client._config.BRUIN_CONFIG["base_url"]}/api/Ticket/{ticket_id}/nextresult',
                headers=bruin_client._get_request_headers(),
                params=filters,
                verify=False
            )
            response_mock.json.assert_called()
            logger.error.assert_called_once()
            assert next_result == expected_result

    def get_possible_detail_next_result_401_test(self):
        logger = Mock()
        logger.error = Mock()

        ticket_id = 99
        filters = {
            "ticket_id": ticket_id,
            "ServiceNumber": "VCO10199919",
            "DetailId": 191919
        }

        response_401 = {}

        response_mock = Mock()
        response_mock.json = Mock(return_value=response_401)
        response_mock.status_code = 401

        with patch.object(bruin_client_module.requests, 'get', return_value=response_mock):
            bruin_client = BruinClient(logger, config)
            bruin_client.login = Mock()
            bruin_client._bearer_token = "Someverysecretaccesstoken"
            with raises(Exception):
                bruin_client.get_possible_detail_next_result(filters)
                bruin_client_module.requests.get.assert_called_once_with(
                    f'{bruin_client._config.BRUIN_CONFIG["base_url"]}/api/Ticket/{ticket_id}/nextresult',
                    headers=bruin_client._get_request_headers(),
                    params=filters,
                    verify=False
                )
                self.assertRaises(Exception, bruin_client.get_possible_detail_next_result)
                bruin_client.login.assert_called()

    def get_possible_detail_next_result_500_test(self):
        logger = Mock()
        logger.error = Mock()

        ticket_id = 99
        filters = {
            "ticket_id": ticket_id,
            "ServiceNumber": "VCO10199919",
            "DetailId": 191919
        }

        response_500 = {
            "Internal server error"
        }

        response_mock = Mock()
        response_mock.json = Mock(return_value=response_500)
        response_mock.status_code = 500

        with patch.object(bruin_client_module.requests, 'get', return_value=response_mock):
            bruin_client = BruinClient(logger, config)
            bruin_client.login = Mock()
            bruin_client._bearer_token = "Someverysecretaccesstoken"
            with raises(Exception):
                bruin_client.get_possible_detail_next_result(filters)
                bruin_client_module.requests.get.assert_called_once_with(
                    f'{bruin_client._config.BRUIN_CONFIG["base_url"]}/api/Ticket/{ticket_id}/nextresult',
                    headers=bruin_client._get_request_headers(),
                    params=filters,
                    verify=False
                )
                self.assertRaises(Exception, bruin_client.get_possible_detail_next_result)
                bruin_client.login.assert_called()

    def change_work_queue_200_test(self):
        logger = Mock()

        ticket_id = 99
        filters = {
            "ticket_id": ticket_id,
            "details": [
                {
                    "detailId": 123,
                    "serviceNumber": "VCO1919191",
                }
            ],
            "notes": [],
            "resultTypeId": 19
        }

        valid_put_response = {
            "message": "success"
        }

        expected_result = {
            "body": valid_put_response,
            "status_code": 200
        }

        response_mock = Mock()
        response_mock.json = Mock(return_value=valid_put_response)
        response_mock.status_code = 200

        with patch.object(bruin_client_module.requests, 'put', return_value=response_mock):
            bruin_client = BruinClient(logger, config)
            bruin_client.login = Mock()
            bruin_client._bearer_token = "Someverysecretaccesstoken"
            put_result = bruin_client.change_detail_work_queue(filters)
            bruin_client_module.requests.put.assert_called_once_with(
                f'{bruin_client._config.BRUIN_CONFIG["base_url"]}/api/Ticket/{ticket_id}/details/work',
                headers=bruin_client._get_request_headers(),
                json=filters,
                verify=False
            )
            response_mock.json.assert_called_once()
            assert put_result == expected_result

    def change_work_queue_400_test(self):
        logger = Mock()
        logger.error = Mock()

        ticket_id = 99
        filters = {
            "ticket_id": ticket_id,
            "details": [
                {
                    "detailId": None,
                    "serviceNumber": "VCO1919191",
                }
            ],
            "notes": [],
            "resultTypeId": 19
        }

        put_response_400 = {
            "errors": {
                "details[0].detailId": [
                    "The value is not valid."
                ]
            },
            "type": None,
            "title": "Invalid arguments to the API",
            "status": 400,
            "detail": "The inputs supplied to the API are invalid",
            "instance": "/api/Ticket/4503440/details/work",
            "extensions": {}
        }

        expected_result = {
            "body": put_response_400,
            "status_code": 400
        }

        response_mock = Mock()
        response_mock.json = Mock(return_value=put_response_400)
        response_mock.status_code = 400

        with patch.object(bruin_client_module.requests, 'put', return_value=response_mock):
            bruin_client = BruinClient(logger, config)
            bruin_client.login = Mock()
            bruin_client._bearer_token = "Someverysecretaccesstoken"
            put_result = bruin_client.change_detail_work_queue(filters)
            bruin_client_module.requests.put.assert_called_once_with(
                f'{bruin_client._config.BRUIN_CONFIG["base_url"]}/api/Ticket/{ticket_id}/details/work',
                headers=bruin_client._get_request_headers(),
                json=filters,
                verify=False
            )
            response_mock.json.assert_called()
            logger.error.assert_called_once()
            assert put_result == expected_result

    def change_work_queue_401_test(self):
        logger = Mock()

        ticket_id = 99
        filters = {
            "ticket_id": ticket_id,
            "details": [
                {
                    "detailId": 123,
                    "serviceNumber": "VCO1919191",
                }
            ],
            "notes": [],
            "resultTypeId": 19
        }

        response_401 = {}

        response_mock = Mock()
        response_mock.json = Mock(return_value=response_401)
        response_mock.status_code = 401

        with patch.object(bruin_client_module.requests, 'put', return_value=response_mock):
            bruin_client = BruinClient(logger, config)
            bruin_client.login = Mock()
            bruin_client._bearer_token = "Someverysecretaccesstoken"
            with raises(Exception):
                bruin_client.change_detail_work_queue(filters)
                bruin_client_module.requests.put.assert_called_once_with(
                    f'{bruin_client._config.BRUIN_CONFIG["base_url"]}/api/Ticket/{ticket_id}/details/work',
                    headers=bruin_client._get_request_headers(),
                    json=filters,
                    verify=False
                )
                self.assertRaises(Exception, bruin_client.change_detail_work_queue)
                bruin_client.login.assert_called()

    def change_work_queue_500_test(self):
        logger = Mock()

        ticket_id = 99
        filters = {
            "ticket_id": ticket_id,
            "details": [
                {
                    "detailId": 123,
                    "serviceNumber": "VCO1919191",
                }
            ],
            "notes": [],
            "resultTypeId": 19
        }

        response_500 = {}

        response_mock = Mock()
        response_mock.json = Mock(return_value=response_500)
        response_mock.status_code = 500

        with patch.object(bruin_client_module.requests, 'put', return_value=response_mock):
            bruin_client = BruinClient(logger, config)
            bruin_client.login = Mock()
            bruin_client._bearer_token = "Someverysecretaccesstoken"
            with raises(Exception):
                bruin_client.change_detail_work_queue(filters)
                bruin_client_module.requests.put.assert_called_once_with(
                    f'{bruin_client._config.BRUIN_CONFIG["base_url"]}/api/Ticket/{ticket_id}/details/work',
                    headers=bruin_client._get_request_headers(),
                    json=filters,
                    verify=False
                )
                self.assertRaises(Exception, bruin_client.change_detail_work_queue)
                bruin_client.login.assert_called()

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

    def get_client_info_200_test(self):
        service_number = "VC01919"

        filters = {
            'service_number': service_number,
            'status': 'A'
        }

        bruin_response_message = {
            "documents": [
                {
                    "clientID": 9919,
                    "clientName": "Tet Corp",
                    "vendor": "Central Positronics",
                    "accountNumber": "59864",
                    "subAccountNumber": "4554",
                    "inventoryID": "12295777",
                    "serviceNumber": "VC01919",
                    "siteId": 16199,
                    "siteLabel": "Turtle Square",
                    "address": {
                        "address": "2125 Fake Street",
                        "city": "River Crossing",
                        "state": "ST",
                        "zip": "1999556",
                        "country": "MEJIS"
                    },
                    "hierarchy": "|Tet Corp|River Crossing|SomeSite|",
                    "costCenter": "15830",
                    "assignee": None,
                    "description": "",
                    "installDate": "2018-04-03T17:58:51Z",
                    "disconnectDate": None,
                    "status": "A",
                    "verified": "Y",
                    "productCategory": "SD-WAN",
                    "productType": "SD-WAN",
                    "items": [
                        {
                            "itemName": "Licensed Software - SD-WAN 30M",
                            "primaryIndicator": "SD-WAN"
                        }
                    ],
                    "contractIdentifier": None,
                    "rateCardIdentifier": None,
                    "lastInvoiceUsageDate": "2020-02-23T05:00:00Z",
                    "lastUsageDate": None,
                    "longitude": -76.265384,
                    "latitude": 36.843456
                }
            ]
        }

        bruin_response_status_code = 200

        bruin_response = Mock()
        bruin_response.json = Mock(return_value=bruin_response_message)
        bruin_response.status_code = bruin_response_status_code

        logger = Mock()

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        bruin_client.login = Mock()

        with patch.object(bruin_client_module.requests, 'get', return_value=bruin_response):
            result = bruin_client.get_client_info(filters)

            get_client_info_call = call(
                f'{config.BRUIN_CONFIG["base_url"]}/api/Inventory',
                headers=bruin_client._get_request_headers(),
                params=humps.pascalize(filters),
                verify=False
            )
            assert get_client_info_call in bruin_client_module.requests.get.mock_calls

        expected = {
            "body": bruin_response_message,
            "status_code": bruin_response_status_code,
        }
        assert result == expected

    def get_client_info_test_empty_result_200(self):
        service_number = "VC01919"

        filters = {
            'service_number': service_number,
        }

        bruin_response_message = {
            "documents": []
        }

        bruin_response_status_code = 200

        bruin_response = Mock()
        bruin_response.json = Mock(return_value=bruin_response_message)
        bruin_response.status_code = bruin_response_status_code

        logger = Mock()

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        bruin_client.login = Mock()

        with patch.object(bruin_client_module.requests, 'get', return_value=bruin_response):
            result = bruin_client.get_client_info(filters)

            get_client_info_call = call(
                f'{config.BRUIN_CONFIG["base_url"]}/api/Inventory',
                headers=bruin_client._get_request_headers(),
                params=humps.pascalize(filters),
                verify=False
            )
            assert get_client_info_call in bruin_client_module.requests.get.mock_calls

        expected = {
            "body": bruin_response_message,
            "status_code": bruin_response_status_code,
        }
        assert result == expected

    def get_client_info_400_test(self):
        service_number = "VC01919"
        # Client ID that doesn't belong to their database.
        # If serial doesn't belong there will be a 200 empty response
        client_id = 1328974321874231078946876

        filters = {
            'service_number': service_number,
            'client_id': client_id
        }

        bruin_response_message = {
            "errors": {
                "clientId": [
                    "The value is not valid."
                ]
            },
            "type": None,
            "title": "Invalid arguments to the API",
            "status": 400,
            "detail": "The inputs supplied to the API are invalid",
            "instance": "/api/Inventory",
            "extensions": {}
        }

        bruin_response_status_code = 400

        bruin_response = Mock()
        bruin_response.json = Mock(return_value=bruin_response_message)
        bruin_response.status_code = bruin_response_status_code

        logger = Mock()

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        bruin_client.login = Mock()

        with patch.object(bruin_client_module.requests, 'get', return_value=bruin_response):
            result = bruin_client.get_client_info(filters)

            get_client_info_call = call(
                f'{config.BRUIN_CONFIG["base_url"]}/api/Inventory',
                headers=bruin_client._get_request_headers(),
                params=humps.pascalize(filters),
                verify=False
            )
            assert get_client_info_call in bruin_client_module.requests.get.mock_calls

        expected = {
            "body": bruin_response_message,
            "status_code": bruin_response_status_code,
        }
        assert result == expected

    def get_client_info_with_ko_401_test(self):
        logger = Mock()

        filters = {
            "client_id": 9994,
            "status": "A",
            "service_number": "VC05400009999"
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
                bruin_client.get_client_info(filters)
                bruin_client_module.requests.get.assert_called_once_with(
                    f'{bruin_client._config.BRUIN_CONFIG["base_url"]}/api/Inventory',
                    headers=bruin_client._get_request_headers(),
                    params=humps.pascalize(filters),
                    verify=False
                )
                self.assertRaises(Exception, bruin_client.get_client_info)
                bruin_client.login.assert_called()

    def get_client_info_with_ko_5XX_test(self):
        logger = Mock()

        filters = {
            "client_id": 9994,
            "service_number": "VC05400009999",
            "status": "A"
        }

        response_mock = Mock()
        response_mock.json = Mock()
        response_mock.status_code = 500

        expected_result = {"body": "Got internal error from Bruin", "status_code": 500}

        with patch.object(bruin_client_module.requests, 'get', return_value=response_mock):
            bruin_client = BruinClient(logger, config)
            bruin_client.login = Mock()
            bruin_client._bearer_token = "Someverysecretaccesstoken"
            result = bruin_client.get_client_info(filters)
            bruin_client_module.requests.get.assert_called_with(
                f'{bruin_client._config.BRUIN_CONFIG["base_url"]}/api/Inventory',
                headers=bruin_client._get_request_headers(),
                params=humps.pascalize(filters),
                verify=False
            )
            assert result == expected_result

    def get_client_info_with_connection_error_test(self):
        logger = Mock()

        filters = {
            "client_id": 9994,
            "service_number": "VC05400009999",
            "status": "A"
        }
        cause = "ERROR"

        message = {
            "body": f"Connection error in Bruin API. {cause}",
            "status_code": 500}

        with patch.object(bruin_client_module.requests, 'get', side_effect=ConnectionError(cause)):
            bruin_client = BruinClient(logger, config)
            bruin_client.login = Mock()
            bruin_client._bearer_token = "Someverysecretaccesstoken"
            result = bruin_client.get_client_info(filters)
            bruin_client_module.requests.get.assert_called_with(
                f'{bruin_client._config.BRUIN_CONFIG["base_url"]}/api/Inventory',
                headers=bruin_client._get_request_headers(),
                params=humps.pascalize(filters),
                verify=False
            )

            assert result == message
