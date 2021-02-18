import json
from unittest.mock import Mock
from unittest.mock import call
from unittest.mock import patch

import humps
import pytest

from aiohttp import ClientConnectionError

from asynctest import CoroutineMock
from pytest import raises

from application.clients.bruin_client import BruinClient
from config import testconfig as config


class TestBruinClient:
    def instance_test(self):
        logger = Mock()

        bruin_client = BruinClient(logger, config)

        assert bruin_client._logger is logger
        assert bruin_client._config is config

    @pytest.mark.asyncio
    async def login_test(self):
        logger = Mock()
        access_token_str = "Someverysecretaccesstoken"

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value={"access_token": access_token_str})

        bruin_client = BruinClient(logger, config)
        with patch.object(bruin_client._session, 'post', new=CoroutineMock(return_value=response_mock)) as mock_post:
            await bruin_client.login()

            assert access_token_str == bruin_client._bearer_token
            mock_post.assert_called_once()

    @pytest.mark.asyncio
    async def login_with_failure_test(self):
        logger = Mock()

        bruin_client = BruinClient(logger, config)
        with patch.object(bruin_client._session, 'post', new=CoroutineMock(side_effect=Exception)) as mock_post:
            await bruin_client.login()

            assert bruin_client._bearer_token == ''
            mock_post.assert_called_once()

    @pytest.mark.asyncio
    async def get_request_headers_test(self):
        logger = Mock()
        access_token_str = "Someverysecretaccesstoken"
        expected_headers = {
            "authorization": f"Bearer {access_token_str}",
            "Content-Type": "application/json-patch+json",
            "Cache-control": "no-cache, no-store, no-transform, max-age=0, only-if-cached",
        }

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = access_token_str

        headers = bruin_client._get_request_headers()
        assert headers == expected_headers

    @pytest.mark.asyncio
    async def get_request_headers_with_no_bearer_token_test(self):
        logger = Mock()

        bruin_client = BruinClient(logger, config)
        with raises(Exception) as error_info:
            bruin_client._get_request_headers()
            assert error_info == "Missing BEARER token"

    @pytest.mark.asyncio
    async def get_all_tickets_test(self):
        logger = Mock()
        params = dict(client_id=123, ticket_id=321, ticket_status="New", category='SD-WAN', ticket_topic='VOO')

        get_response = {
            "responses": [
                {"category": "SD-WAN", "ticketStatus": "New"}
            ]
        }

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=get_response)
        response_mock.status = 200

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(bruin_client._session, 'get', new=CoroutineMock(return_value=response_mock)) as mock_get:
            tickets = await bruin_client.get_all_tickets(params)

        mock_get.assert_called_once()
        assert mock_get.call_args[1]['params']['ClientId'] == params['client_id']
        assert mock_get.call_args[1]['params']['TicketId'] == params['ticket_id']
        assert mock_get.call_args[1]['params']['TicketStatus'] == params['ticket_status']
        assert mock_get.call_args[1]['params']['ProductCategory'] == params['product_category']
        assert mock_get.call_args[1]['params']['TicketTopic'] == params['ticket_topic']
        assert tickets['body'] == get_response['responses']
        assert tickets['status'] == 200

    @pytest.mark.asyncio
    async def get_all_tickets_with_400_status_test(self):
        logger = Mock()
        logger.error = Mock()
        params = dict(client_id=123, ticket_id=321, ticket_status="New", category='SD-WAN', ticket_topic='VOO')
        error_response = {'error': "400 error"}
        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=error_response)
        response_mock.status = 400

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        bruin_client.login = CoroutineMock()

        with patch.object(bruin_client._session, 'get', new=CoroutineMock(return_value=response_mock)):
            tickets = await bruin_client.get_all_tickets(params)

            logger.error.assert_called()

            assert tickets['body'] == error_response
            assert tickets['status'] == 400

    @pytest.mark.asyncio
    async def get_all_tickets_with_401_status_test(self):
        logger = Mock()
        params = dict(client_id=123, ticket_id=321, ticket_status="New", category='SD-WAN', ticket_topic='VOO')

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value={})
        response_mock.status = 401

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        bruin_client.login = CoroutineMock()

        with patch.object(bruin_client._session, 'get', new=CoroutineMock(return_value=response_mock)):
            tickets = await bruin_client.get_all_tickets(params)
            logger.error.assert_called()

            assert tickets['body'] == "Got 401 from Bruin"
            assert tickets['status'] == 401

    @pytest.mark.asyncio
    async def get_all_tickets_with_403_status_test(self):
        logger = Mock()
        logger.error = Mock()
        params = dict(client_id=123, ticket_id=321, ticket_status="New", category='SD-WAN', ticket_topic='VOO')
        error_response = {'error': "403 error"}
        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=error_response)
        response_mock.status = 403

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        bruin_client.login = CoroutineMock()

        with patch.object(bruin_client._session, 'get', new=CoroutineMock(return_value=response_mock)):
            tickets = await bruin_client.get_all_tickets(params)

            logger.error.assert_called()

            assert tickets['body'] == error_response
            assert tickets['status'] == 403

    @pytest.mark.asyncio
    async def get_all_tickets_with_404_status_test(self):
        logger = Mock()
        logger.error = Mock()
        params = dict(client_id=123, ticket_id=321, ticket_status="New", category='SD-WAN', ticket_topic='VOO')
        error_response = {'error': "400 error"}
        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=error_response)
        response_mock.status = 404

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        bruin_client.login = CoroutineMock()

        with patch.object(bruin_client._session, 'get', new=CoroutineMock(return_value=response_mock)):
            tickets = await bruin_client.get_all_tickets(params)

            logger.error.assert_called()

            assert tickets['body'] == "Resource not found"
            assert tickets['status'] == 404

    @pytest.mark.asyncio
    async def get_all_tickets_with_500_status_test(self):
        logger = Mock()
        logger.error = Mock()
        params = dict(client_id=123, ticket_id=321, ticket_status="New", category='SD-WAN', ticket_topic='VOO')
        error_response = {'error': "400 error"}
        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=error_response)
        response_mock.status = 500

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        bruin_client.login = CoroutineMock()

        with patch.object(bruin_client._session, 'get', new=CoroutineMock(return_value=response_mock)):
            tickets = await bruin_client.get_all_tickets(params)

            logger.error.assert_called()

            assert tickets['body'] == "Got internal error from Bruin"
            assert tickets['status'] == 500

    @pytest.mark.asyncio
    async def get_ticket_details_test(self):
        logger = Mock()
        ticket_id = 321
        get_response = {'ticket_details': 'Some Ticket Details'}

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=get_response)
        response_mock.status = 200

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(bruin_client._session, 'get', new=CoroutineMock(return_value=response_mock)) as mock_get:
            ticket_details = await bruin_client.get_ticket_details(ticket_id)

            mock_get.assert_called_once()
            assert ticket_details["body"] == get_response
            assert ticket_details["status"] == 200

    @pytest.mark.asyncio
    async def get_ticket_details_with_400_status_test(self):
        logger = Mock()
        logger.error = Mock()
        ticket_id = 321
        error_response = {'error': "400 error"}

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=error_response)
        response_mock.status = 400

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        bruin_client.login = CoroutineMock()

        with patch.object(bruin_client._session, 'get', new=CoroutineMock(return_value=response_mock)):
            ticket_details = await bruin_client.get_ticket_details(ticket_id)
            logger.error.assert_called()

            assert ticket_details['body'] == error_response
            assert ticket_details['status'] == 400

    @pytest.mark.asyncio
    async def get_ticket_details_with_401_status_test(self):
        logger = Mock()
        logger.error = Mock()
        ticket_id = 321

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value={})
        response_mock.status = 401

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        bruin_client.login = CoroutineMock()

        with patch.object(bruin_client._session, 'get', new=CoroutineMock(return_value=response_mock)):
            ticket_details = await bruin_client.get_ticket_details(ticket_id)
            bruin_client.login.assert_awaited()
            logger.error.assert_called()

            assert ticket_details['body'] == "Got 401 from Bruin"
            assert ticket_details['status'] == 401

    @pytest.mark.asyncio
    async def get_ticket_details_with_403_status_test(self):
        logger = Mock()
        logger.error = Mock()
        ticket_id = 321
        error_response = {'error': "403 error"}

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=error_response)
        response_mock.status = 403

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        bruin_client.login = CoroutineMock()

        with patch.object(bruin_client._session, 'get', new=CoroutineMock(return_value=response_mock)):
            ticket_details = await bruin_client.get_ticket_details(ticket_id)
            logger.error.assert_called()

            assert ticket_details['body'] == error_response
            assert ticket_details['status'] == 403

    @pytest.mark.asyncio
    async def get_ticket_details_with_404_status_test(self):
        logger = Mock()
        logger.error = Mock()
        ticket_id = 321

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value={})
        response_mock.status = 404

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        bruin_client.login = CoroutineMock()

        with patch.object(bruin_client._session, 'get', new=CoroutineMock(return_value=response_mock)):
            ticket_details = await bruin_client.get_ticket_details(ticket_id)
            logger.error.assert_called()

            assert ticket_details['body'] == "Resource not found"
            assert ticket_details['status'] == 404

    @pytest.mark.asyncio
    async def get_ticket_details_with_500_status_test(self):
        logger = Mock()
        logger.error = Mock()
        ticket_id = 321

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value={})
        response_mock.status = 500

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        bruin_client.login = CoroutineMock()

        with patch.object(bruin_client._session, 'get', new=CoroutineMock(return_value=response_mock)):
            ticket_details = await bruin_client.get_ticket_details(ticket_id)
            logger.error.assert_called()

            assert ticket_details['body'] == "Got internal error from Bruin"
            assert ticket_details['status'] == 500

    @pytest.mark.asyncio
    async def post_ticket_note_test(self):
        logger = Mock()
        logger.error = Mock()

        ticket_id = 321
        note_contents = 'Ticket Notes'
        expected_post_response = {'response': 'Note Appended'}

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=expected_post_response)
        response_mock.status = 200

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(bruin_client._session, 'post', new=CoroutineMock(return_value=response_mock)) as mock_post:
            post_response = await bruin_client.post_ticket_note(ticket_id, note_contents)

            mock_post.assert_called_once()
            assert post_response["body"] == expected_post_response
            assert post_response["status"] == 200

    @pytest.mark.asyncio
    async def post_ticket_note_with_400_status_test(self):
        logger = Mock()
        logger.error = Mock()
        ticket_id = 321
        note_contents = 'Ticket Notes'
        expected_post_response = {'response': 'Error 400'}

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=expected_post_response)
        response_mock.status = 400

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        bruin_client.login = CoroutineMock()

        with patch.object(bruin_client._session, 'post', new=CoroutineMock(return_value=response_mock)):
            post_response = await bruin_client.post_ticket_note(ticket_id, note_contents)
            logger.error.assert_called()

            assert post_response["body"] == expected_post_response
            assert post_response["status"] == 400

    @pytest.mark.asyncio
    async def post_ticket_note_with_401_status_test(self):
        logger = Mock()
        ticket_id = 321
        note_contents = 'Ticket Notes'
        expected_post_response = {}

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=expected_post_response)
        response_mock.status = 401

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        bruin_client.login = CoroutineMock()

        with patch.object(bruin_client._session, 'post', new=CoroutineMock(return_value=response_mock)):
            post_response = await bruin_client.post_ticket_note(ticket_id, note_contents)

            bruin_client.login.assert_awaited()
            logger.error.assert_called()

            assert post_response["body"] == "Got 401 from Bruin"
            assert post_response["status"] == 401

    @pytest.mark.asyncio
    async def post_ticket_note_with_403_status_test(self):
        logger = Mock()
        logger.error = Mock()
        ticket_id = 321
        note_contents = 'Ticket Notes'
        expected_post_response = {'response': 'Error 403'}

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=expected_post_response)
        response_mock.status = 403

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        bruin_client.login = CoroutineMock()

        with patch.object(bruin_client._session, 'post', new=CoroutineMock(return_value=response_mock)):
            post_response = await bruin_client.post_ticket_note(ticket_id, note_contents)
            logger.error.assert_called()

            assert post_response["body"] == expected_post_response
            assert post_response["status"] == 403

    @pytest.mark.asyncio
    async def post_ticket_note_with_404_status_test(self):
        logger = Mock()
        logger.error = Mock()

        ticket_id = 321
        note_contents = 'Ticket Notes'
        expected_post_response = {}

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=expected_post_response)
        response_mock.status = 404

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        bruin_client.login = CoroutineMock()

        with patch.object(bruin_client._session, 'post', new=CoroutineMock(return_value=response_mock)):
            post_response = await bruin_client.post_ticket_note(ticket_id, note_contents)
            logger.error.assert_called()

            assert post_response["body"] == "Resource not found"
            assert post_response["status"] == 404

    @pytest.mark.asyncio
    async def post_ticket_note_with_500_status_test(self):
        logger = Mock()
        logger.error = Mock()
        ticket_id = 321
        note_contents = 'Ticket Notes'
        expected_post_response = {}

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=expected_post_response)
        response_mock.status = 500

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        bruin_client.login = CoroutineMock()

        with patch.object(bruin_client._session, 'post', new=CoroutineMock(return_value=response_mock)):
            post_response = await bruin_client.post_ticket_note(ticket_id, note_contents)
            logger.error.assert_called()

            assert post_response["body"] == "Got internal error from Bruin"
            assert post_response["status"] == 500

    @pytest.mark.asyncio
    async def post_ticket_test(self):
        logger = Mock()
        payload = dict(clientId=321, category='Some Category', notes=['List of Notes'], services=['List of Services'],
                       contacts=['List of Contacts'])
        expected_post_response = 'Ticket Created'

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=expected_post_response)
        response_mock.status = 200

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(bruin_client._session, 'post', new=CoroutineMock(return_value=response_mock)) as mock_post:
            post_ticket = await bruin_client.post_ticket(payload)
            mock_post.assert_called_once()
            assert post_ticket['body'] == expected_post_response
            assert post_ticket['status'] == 200

    @pytest.mark.asyncio
    async def post_ticket_400_status_test(self):
        logger = Mock()
        logger.error = Mock()
        payload = dict(clientId=321, category='Some Category', notes=['List of Notes'], services=['List of Services'],
                       contacts=['List of Contacts'])
        expected_post_response = 'Ticket failed to create'

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=expected_post_response)
        response_mock.status = 400

        bruin_client = BruinClient(logger, config)
        bruin_client.login = CoroutineMock()
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(bruin_client._session, 'post', new=CoroutineMock(return_value=response_mock)):
            post_ticket = await bruin_client.post_ticket(payload)
            logger.error.assert_called()

            assert post_ticket["body"] == expected_post_response
            assert post_ticket["status"] == 400

    @pytest.mark.asyncio
    async def post_ticket_401_status_test(self):
        logger = Mock()
        logger.error = Mock()
        payload = dict(clientId=321, category='Some Category', notes=['List of Notes'], services=['List of Services'],
                       contacts=['List of Contacts'])
        expected_post_response = 'Ticket failed to create'

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=expected_post_response)
        response_mock.status = 401

        bruin_client = BruinClient(logger, config)
        bruin_client.login = CoroutineMock()
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(bruin_client._session, 'post', new=CoroutineMock(return_value=response_mock)):
            post_ticket = await bruin_client.post_ticket(payload)
            logger.error.assert_called()
            bruin_client.login.assert_awaited()
            assert post_ticket["body"] == "Got 401 from Bruin"
            assert post_ticket["status"] == 401

    @pytest.mark.asyncio
    async def post_ticket_403_status_test(self):
        logger = Mock()
        logger.error = Mock()
        payload = dict(clientId=321, category='Some Category', notes=['List of Notes'], services=['List of Services'],
                       contacts=['List of Contacts'])
        expected_post_response = 'Ticket failed to create'

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=expected_post_response)
        response_mock.status = 403

        bruin_client = BruinClient(logger, config)
        bruin_client.login = CoroutineMock()
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(bruin_client._session, 'post', new=CoroutineMock(return_value=response_mock)):
            post_ticket = await bruin_client.post_ticket(payload)
            logger.error.assert_called()

            assert post_ticket["body"] == expected_post_response
            assert post_ticket["status"] == 403

    @pytest.mark.asyncio
    async def post_ticket_404_status_test(self):
        logger = Mock()
        logger.error = Mock()
        payload = dict(clientId=321, category='Some Category', notes=['List of Notes'], services=['List of Services'],
                       contacts=['List of Contacts'])
        expected_post_response = 'Ticket failed to create'

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=expected_post_response)
        response_mock.status = 404

        bruin_client = BruinClient(logger, config)
        bruin_client.login = CoroutineMock()
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(bruin_client._session, 'post', new=CoroutineMock(return_value=response_mock)):
            post_ticket = await bruin_client.post_ticket(payload)
            logger.error.assert_called()

            assert post_ticket["body"] == "Resource not found"
            assert post_ticket["status"] == 404

    @pytest.mark.asyncio
    async def post_ticket_500_status_test(self):
        logger = Mock()
        logger.error = Mock()
        payload = dict(clientId=321, category='Some Category', notes=['List of Notes'], services=['List of Services'],
                       contacts=['List of Contacts'])
        expected_post_response = 'Ticket failed to create'

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=expected_post_response)
        response_mock.status = 500

        bruin_client = BruinClient(logger, config)
        bruin_client.login = CoroutineMock()
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(bruin_client._session, 'post', new=CoroutineMock(return_value=response_mock)):
            post_ticket = await bruin_client.post_ticket(payload)
            logger.error.assert_called()

            assert post_ticket["body"] == "Got internal error from Bruin"
            assert post_ticket["status"] == 500

    @pytest.mark.asyncio
    async def update_ticket_status_test(self):
        logger = Mock()

        ticket_id = 123
        detail_id = 321
        ticket_status = 'O'
        successful_status_change = 'Success'

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=successful_status_change)
        response_mock.status = 200

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(bruin_client._session, 'put', new=CoroutineMock(return_value=response_mock)) as mock_put:
            update_ticket_status = await bruin_client.update_ticket_status(ticket_id, detail_id, ticket_status)
            mock_put.assert_called_once()
            assert update_ticket_status["body"] == successful_status_change
            assert update_ticket_status["status"] == 200

    @pytest.mark.asyncio
    async def update_ticket_status_400_error_status_test(self):
        logger = Mock()
        logger.error = Mock()

        ticket_id = 123
        detail_id = 321
        ticket_status = 'X'
        failure_status_change = 'failed'

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=failure_status_change)
        response_mock.status = 400

        bruin_client = BruinClient(logger, config)
        bruin_client.login = CoroutineMock()
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(bruin_client._session, 'put', new=CoroutineMock(return_value=response_mock)):
            update_ticket_status = await bruin_client.update_ticket_status(ticket_id, detail_id, ticket_status)

            logger.error.assert_called()

            assert update_ticket_status["body"] == failure_status_change
            assert update_ticket_status["status"] == 400

    @pytest.mark.asyncio
    async def update_ticket_status_401_error_status_test(self):
        logger = Mock()
        logger.error = Mock()

        ticket_id = 123
        detail_id = 321
        ticket_status = 'X'
        failure_status_change = 'failed'

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=failure_status_change)
        response_mock.status = 401

        bruin_client = BruinClient(logger, config)
        bruin_client.login = CoroutineMock()
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(bruin_client._session, 'put', new=CoroutineMock(return_value=response_mock)):
            update_ticket_status = await bruin_client.update_ticket_status(ticket_id, detail_id, ticket_status)

            logger.error.assert_called()
            bruin_client.login.assert_awaited()

            assert update_ticket_status["body"] == "Got 401 from Bruin"
            assert update_ticket_status["status"] == 401

    @pytest.mark.asyncio
    async def update_ticket_status_403_error_status_test(self):
        logger = Mock()
        logger.error = Mock()

        ticket_id = 123
        detail_id = 321
        ticket_status = 'X'
        failure_status_change = 'failed'

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=failure_status_change)
        response_mock.status = 403

        bruin_client = BruinClient(logger, config)
        bruin_client.login = CoroutineMock()
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(bruin_client._session, 'put', new=CoroutineMock(return_value=response_mock)):
            update_ticket_status = await bruin_client.update_ticket_status(ticket_id, detail_id, ticket_status)

            logger.error.assert_called()

            assert update_ticket_status["body"] == failure_status_change
            assert update_ticket_status["status"] == 403

    @pytest.mark.asyncio
    async def update_ticket_status_404_error_status_test(self):
        logger = Mock()
        logger.error = Mock()

        ticket_id = 123
        detail_id = 321
        ticket_status = 'X'
        failure_status_change = 'failed'

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=failure_status_change)
        response_mock.status = 404

        bruin_client = BruinClient(logger, config)
        bruin_client.login = CoroutineMock()
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(bruin_client._session, 'put', new=CoroutineMock(return_value=response_mock)):
            update_ticket_status = await bruin_client.update_ticket_status(ticket_id, detail_id, ticket_status)

            logger.error.assert_called()

            assert update_ticket_status["body"] == "Resource not found"
            assert update_ticket_status["status"] == 404

    @pytest.mark.asyncio
    async def update_ticket_status_500_error_status_test(self):
        logger = Mock()
        logger.error = Mock()

        ticket_id = 123
        detail_id = 321
        ticket_status = 'X'
        failure_status_change = 'failed'

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=failure_status_change)
        response_mock.status = 500

        bruin_client = BruinClient(logger, config)
        bruin_client.login = CoroutineMock()
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(bruin_client._session, 'put', new=CoroutineMock(return_value=response_mock)):
            update_ticket_status = await bruin_client.update_ticket_status(ticket_id, detail_id, ticket_status)

            logger.error.assert_called()

            assert update_ticket_status["body"] == "Got internal error from Bruin"
            assert update_ticket_status["status"] == 500

    @pytest.mark.asyncio
    async def get_management_status_pascalize_with_ok_test(self):
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

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=valid_management_status)
        response_mock.status = 200

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        bruin_client.login = CoroutineMock()

        with patch.object(bruin_client._session, 'get', new=CoroutineMock(return_value=response_mock)):
            await bruin_client.get_management_status(filters)
            bruin_client._session.get.assert_awaited_once_with(
                f'{bruin_client._config.BRUIN_CONFIG["base_url"]}/api/Inventory/Attribute',
                headers=bruin_client._get_request_headers(),
                params=pascalized_filter,
                ssl=False
            )
            response_mock.json.assert_awaited_once()

    @pytest.mark.asyncio
    async def get_management_status_with_ko_401_test(self):
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

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=empty_response)
        response_mock.status = 401

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        bruin_client.login = CoroutineMock()

        with patch.object(bruin_client._session, 'get', new=CoroutineMock(return_value=response_mock)):
            with raises(Exception):
                await bruin_client.get_management_status(filters)
                bruin_client._session.get.assert_awaited_once_with(
                    f'{bruin_client._config.BRUIN_CONFIG["base_url"]}/api/Inventory/Attribute',
                    headers=bruin_client._get_request_headers(),
                    params=pascalized_filter,
                    ssl=False
                )
                self.assertRaises(Exception, await bruin_client.get_management_status)
                bruin_client.login.assert_awaited()

    @pytest.mark.asyncio
    async def get_management_status_with_ko_400_test(self):
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

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=response_400)
        response_mock.status = 400

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        bruin_client.login = CoroutineMock()

        with patch.object(bruin_client._session, 'get', new=CoroutineMock(return_value=response_mock)):
            await bruin_client.get_management_status(filters)
            bruin_client._session.get.assert_awaited_once_with(
                f'{bruin_client._config.BRUIN_CONFIG["base_url"]}/api/Inventory/Attribute',
                headers=bruin_client._get_request_headers(),
                params=pascalized_filter,
                ssl=False
            )

    @pytest.mark.asyncio
    async def get_management_status_with_ko_403_test(self):
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

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=response_403)
        response_mock.status = 403

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        bruin_client.login = CoroutineMock()

        with patch.object(bruin_client._session, 'get', new=CoroutineMock(return_value=response_mock)):
            await bruin_client.get_management_status(filters)
            bruin_client._session.get.assert_awaited_once_with(
                f'{bruin_client._config.BRUIN_CONFIG["base_url"]}/api/Inventory/Attribute',
                headers=bruin_client._get_request_headers(),
                params=pascalized_filter,
                ssl=False
            )

    @pytest.mark.asyncio
    async def get_management_status_with_ko_500_test(self):
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

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=response_500)
        response_mock.status = 500

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        bruin_client.login = CoroutineMock()

        with patch.object(bruin_client._session, 'get', new=CoroutineMock(return_value=response_mock)):
            await bruin_client.get_management_status(filters)
            bruin_client._session.get.assert_called_with(
                f'{bruin_client._config.BRUIN_CONFIG["base_url"]}/api/Inventory/Attribute',
                headers=bruin_client._get_request_headers(),
                params=pascalized_filter,
                ssl=False
            )

    @pytest.mark.asyncio
    async def get_management_status_with_connection_error_test(self):
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

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        bruin_client.login = CoroutineMock()

        with patch.object(bruin_client._session, 'get', new=CoroutineMock(side_effect=ClientConnectionError(cause))):
            result = await bruin_client.get_management_status(filters)
            bruin_client._session.get.assert_awaited_with(
                f'{bruin_client._config.BRUIN_CONFIG["base_url"]}/api/Inventory/Attribute',
                headers=bruin_client._get_request_headers(),
                params=pascalized_filter,
                ssl=False
            )

            assert result == message

    @pytest.mark.asyncio
    async def get_possible_detail_next_result_200_test(self):
        logger = Mock()

        ticket_id = 99
        filters = {
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
            "status": 200
        }

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=valid_next_result)
        response_mock.status = 200

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        bruin_client.login = CoroutineMock()

        with patch.object(bruin_client._session, 'get', new=CoroutineMock(return_value=response_mock)):
            next_result = await bruin_client.get_possible_detail_next_result(ticket_id, filters)
            bruin_client._session.get.assert_awaited_once_with(
                f'{bruin_client._config.BRUIN_CONFIG["base_url"]}/api/Ticket/{ticket_id}/nextresult',
                headers=bruin_client._get_request_headers(),
                params=filters,
                ssl=False
            )
            response_mock.json.assert_awaited_once()
            assert next_result == expected_result

    @pytest.mark.asyncio
    async def get_possible_detail_next_result_400_test(self):
        logger = Mock()
        logger.error = Mock()

        ticket_id = 99
        filters = {
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
            "status": 400
        }

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=response_400)
        response_mock.status = 400

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        bruin_client.login = CoroutineMock()

        with patch.object(bruin_client._session, 'get', new=CoroutineMock(return_value=response_mock)):
            next_result = await bruin_client.get_possible_detail_next_result(ticket_id, filters)
            bruin_client._session.get.assert_awaited_once_with(
                f'{bruin_client._config.BRUIN_CONFIG["base_url"]}/api/Ticket/{ticket_id}/nextresult',
                headers=bruin_client._get_request_headers(),
                params=filters,
                ssl=False
            )
            response_mock.json.assert_called()
            logger.error.assert_called_once()
            assert next_result == expected_result

    @pytest.mark.asyncio
    async def get_possible_detail_next_result_401_test(self):
        logger = Mock()
        logger.error = Mock()

        ticket_id = 99
        filters = {
            "ServiceNumber": "VCO10199919",
            "DetailId": 191919
        }

        response_401 = {}

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=response_401)
        response_mock.status = 401

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        bruin_client.login = CoroutineMock()

        with patch.object(bruin_client._session, 'get', new=CoroutineMock(return_value=response_mock)):
            with raises(Exception):
                bruin_client.get_possible_detail_next_result(ticket_id, filters)
                bruin_client._session.get.assert_awaited_once_with(
                    f'{bruin_client._config.BRUIN_CONFIG["base_url"]}/api/Ticket/{ticket_id}/nextresult',
                    headers=bruin_client._get_request_headers(),
                    params=filters,
                    ssl=False
                )
                self.assertRaises(Exception, bruin_client.get_possible_detail_next_result)
                bruin_client.login.assert_awaited()

    @pytest.mark.asyncio
    async def get_possible_detail_next_result_500_test(self):
        logger = Mock()
        logger.error = Mock()

        ticket_id = 99
        filters = {
            "ServiceNumber": "VCO10199919",
            "DetailId": 191919
        }

        response_500 = {
            "Internal server error"
        }

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=response_500)
        response_mock.status = 500

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        bruin_client.login = CoroutineMock()

        with patch.object(bruin_client._session, 'get', new=CoroutineMock(return_value=response_mock)):
            with raises(Exception):
                bruin_client.get_possible_detail_next_result(ticket_id, filters)
                bruin_client._session.get.assert_awaited_once_with(
                    f'{bruin_client._config.BRUIN_CONFIG["base_url"]}/api/Ticket/{ticket_id}/nextresult',
                    headers=bruin_client._get_request_headers(),
                    params=filters,
                    ssl=False
                )
                self.assertRaises(Exception, bruin_client.get_possible_detail_next_result)
                bruin_client.login.assert_awaited()

    @pytest.mark.asyncio
    async def change_work_queue_200_test(self):
        logger = Mock()

        ticket_id = 99
        filters = {
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
            "status": 200
        }

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=valid_put_response)
        response_mock.status = 200

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        bruin_client.login = CoroutineMock()

        with patch.object(bruin_client._session, 'put', new=CoroutineMock(return_value=response_mock)):
            put_result = await bruin_client.change_detail_work_queue(ticket_id, filters)
            bruin_client._session.put.assert_awaited_once_with(
                f'{bruin_client._config.BRUIN_CONFIG["base_url"]}/api/Ticket/{ticket_id}/details/work',
                headers=bruin_client._get_request_headers(),
                json=filters,
                ssl=False
            )
            response_mock.json.assert_awaited_once()
            assert put_result == expected_result

    @pytest.mark.asyncio
    async def change_work_queue_400_test(self):
        logger = Mock()
        logger.error = Mock()

        ticket_id = 99
        filters = {
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
            "status": 400
        }

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=put_response_400)
        response_mock.status = 400

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        bruin_client.login = CoroutineMock()

        with patch.object(bruin_client._session, 'put', new=CoroutineMock(return_value=response_mock)):
            put_result = await bruin_client.change_detail_work_queue(ticket_id, filters)
            bruin_client._session.put.assert_awaited_once_with(
                f'{bruin_client._config.BRUIN_CONFIG["base_url"]}/api/Ticket/{ticket_id}/details/work',
                headers=bruin_client._get_request_headers(),
                json=filters,
                ssl=False
            )
            response_mock.json.assert_called()
            logger.error.assert_called_once()
            assert put_result == expected_result

    @pytest.mark.asyncio
    async def change_work_queue_401_test(self):
        logger = Mock()

        ticket_id = 99
        filters = {
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

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=response_401)
        response_mock.status = 401

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        bruin_client.login = CoroutineMock()

        with patch.object(bruin_client._session, 'put', new=CoroutineMock(return_value=response_mock)):
            with raises(Exception):
                bruin_client.change_detail_work_queue(ticket_id, filters)
                bruin_client._session.put.assert_awaited_once_with(
                    f'{bruin_client._config.BRUIN_CONFIG["base_url"]}/api/Ticket/{ticket_id}/details/work',
                    headers=bruin_client._get_request_headers(),
                    json=filters,
                    ssl=False
                )
                self.assertRaises(Exception, bruin_client.change_detail_work_queue)
                bruin_client.login.assert_awaited()

    @pytest.mark.asyncio
    async def change_work_queue_500_test(self):
        logger = Mock()

        ticket_id = 99
        filters = {
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

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=response_500)
        response_mock.status = 500

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        bruin_client.login = CoroutineMock()

        with patch.object(bruin_client._session, 'put', new=CoroutineMock(return_value=response_mock)):
            with raises(Exception):
                bruin_client.change_detail_work_queue(ticket_id, filters)
                bruin_client._session.put.assert_awaited_once_with(
                    f'{bruin_client._config.BRUIN_CONFIG["base_url"]}/api/Ticket/{ticket_id}/details/work',
                    headers=bruin_client._get_request_headers(),
                    json=filters,
                    ssl=False
                )
                self.assertRaises(Exception, bruin_client.change_detail_work_queue)
                bruin_client.login.assert_awaited()


class TestPostOutageTicket:
    @pytest.mark.asyncio
    async def post_outage_ticket_with_connection_error_test(self):
        client_id = 9994,
        service_number = "VC05400002265"
        connection_error_cause = 'Connection timed out'

        request_params = {
            'ClientID': client_id,
            'WTNs': [service_number],
            'RequestDescription': "MetTel's IPA -- Service Outage Trouble"
        }

        logger = Mock()

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(
            bruin_client._session,
            'post',
            new=CoroutineMock(side_effect=ClientConnectionError(connection_error_cause))
        ):
            result = await bruin_client.post_outage_ticket(client_id, service_number)

            bruin_client._session.post.assert_awaited_with(
                f'{config.BRUIN_CONFIG["base_url"]}/api/Ticket/repair',
                headers=bruin_client._get_request_headers(),
                json=request_params,
                ssl=False
            )

        expected = {
            "body": f"Connection error in Bruin API. Cause: {connection_error_cause}",
            "status": 500
        }
        assert result == expected

    @pytest.mark.asyncio
    async def post_outage_ticket_with_http_2XX_response_test(self):
        client_id = 9994,
        service_number = "VC05400002265"

        request_params = {
            'ClientID': client_id,
            'WTNs': [service_number],
            'RequestDescription': "MetTel's IPA -- Service Outage Trouble"
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
        bruin_response_status = 200

        bruin_response = CoroutineMock()
        bruin_response.status = bruin_response_status
        bruin_response.json = CoroutineMock(return_value=bruin_response_body)

        logger = Mock()

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(bruin_client._session, 'post', new=CoroutineMock(return_value=bruin_response)):
            result = await bruin_client.post_outage_ticket(client_id, service_number)

            bruin_client._session.post.assert_awaited_with(
                f'{config.BRUIN_CONFIG["base_url"]}/api/Ticket/repair',
                headers=bruin_client._get_request_headers(),
                json=request_params,
                ssl=False
            )

        expected = {
            "body": ticket_data,
            "status": bruin_response_status,
        }
        assert result == expected

    @pytest.mark.asyncio
    async def post_outage_ticket_with_http_409_response_test(self):
        client_id = 9994,
        service_number = "VC05400002265"

        request_params = {
            'ClientID': client_id,
            'WTNs': [service_number],
            'RequestDescription': "MetTel's IPA -- Service Outage Trouble"
        }

        ticket_data = {
            "ticketId": 4503440,
            "inventoryId": 12796795,
            "wtn": service_number,
            "errorMessage": (
                "Warning: Ticket already exists. We'll add an additional line.\n Failed to add additional line: The "
                "item already exists in 4503440, could not add another dulplicate one"
            ),
            "errorCode": 409,
        }
        bruin_response_body = {
            "items": [ticket_data]
        }
        bruin_response_status = 200
        bruin_custom_status = 409

        bruin_response = Mock()
        bruin_response.status = bruin_response_status
        bruin_response.json = CoroutineMock(return_value=bruin_response_body)

        logger = Mock()

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(bruin_client._session, 'post', new=CoroutineMock(return_value=bruin_response)):
            result = await bruin_client.post_outage_ticket(client_id, service_number)

            bruin_client._session.post.assert_awaited_with(
                f'{config.BRUIN_CONFIG["base_url"]}/api/Ticket/repair',
                headers=bruin_client._get_request_headers(),
                json=request_params,
                ssl=False
            )

        expected = {
            "body": ticket_data,
            "status": bruin_custom_status,
        }
        assert result == expected

    @pytest.mark.asyncio
    async def post_outage_ticket_with_http_471_response_test(self):
        client_id = 9994,
        service_number = "VC05400002265"

        request_params = {
            'ClientID': client_id,
            'WTNs': [service_number],
            'RequestDescription': "MetTel's IPA -- Service Outage Trouble"
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
        bruin_response_status = 200
        bruin_custom_status = 471

        bruin_response = Mock()
        bruin_response.status = bruin_response_status
        bruin_response.json = CoroutineMock(return_value=bruin_response_body)

        logger = Mock()

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(bruin_client._session, 'post', new=CoroutineMock(return_value=bruin_response)):
            result = await bruin_client.post_outage_ticket(client_id, service_number)

            bruin_client._session.post.assert_awaited_with(
                f'{config.BRUIN_CONFIG["base_url"]}/api/Ticket/repair',
                headers=bruin_client._get_request_headers(),
                json=request_params,
                ssl=False
            )

        expected = {
            "body": ticket_data,
            "status": bruin_custom_status,
        }
        assert result == expected

    @pytest.mark.asyncio
    async def post_outage_ticket_with_http_472_response_test(self):
        client_id = 9994,
        service_number = "VC05400002265"

        request_params = {
            'ClientID': client_id,
            'WTNs': [service_number],
            'RequestDescription': "MetTel's IPA -- Service Outage Trouble"
        }

        ticket_data = {
            "ticketId": 4503440,
            "inventoryId": 12796795,
            "wtn": service_number,
            "errorMessage": "Warning: We unresolved this line (detailId[5506458]) as well as its ticket[4503440].\n",
            "errorCode": 472,
        }
        bruin_response_body = {
            "assets": [ticket_data]
        }
        bruin_response_status = 200
        bruin_custom_status = 472

        bruin_response = Mock()
        bruin_response.status = bruin_response_status
        bruin_response.json = CoroutineMock(return_value=bruin_response_body)

        logger = Mock()

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(bruin_client._session, 'post', new=CoroutineMock(return_value=bruin_response)):
            result = await bruin_client.post_outage_ticket(client_id, service_number)

            bruin_client._session.post.assert_awaited_with(
                f'{config.BRUIN_CONFIG["base_url"]}/api/Ticket/repair',
                headers=bruin_client._get_request_headers(),
                json=request_params,
                ssl=False
            )

        expected = {
            "body": ticket_data,
            "status": bruin_custom_status,
        }
        assert result == expected

    @pytest.mark.asyncio
    async def post_outage_ticket_with_http_473_response_test(self):
        client_id = 9994,
        service_number = "VC05400002265"

        request_params = {
            'ClientID': client_id,
            'WTNs': [service_number],
            'RequestDescription': "MetTel's IPA -- Service Outage Trouble"
        }

        ticket_data = {
            "ticketId": 4503440,
            "inventoryId": 12796795,
            "wtn": service_number,
            "errorMessage": "Warning: We unresolved this line (detailId[5506458]) as well as its ticket[4503440].\n",
            "errorCode": 473,
        }
        bruin_response_body = {
            "assets": [ticket_data]
        }
        bruin_response_status = 200
        bruin_custom_status = 473

        bruin_response = Mock()
        bruin_response.status = bruin_response_status
        bruin_response.json = CoroutineMock(return_value=bruin_response_body)

        logger = Mock()

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(bruin_client._session, 'post', new=CoroutineMock(return_value=bruin_response)):
            result = await bruin_client.post_outage_ticket(client_id, service_number)

            bruin_client._session.post.assert_awaited_with(
                f'{config.BRUIN_CONFIG["base_url"]}/api/Ticket/repair',
                headers=bruin_client._get_request_headers(),
                json=request_params,
                ssl=False
            )

        expected = {
            "body": ticket_data,
            "status": bruin_custom_status,
        }
        assert result == expected

    @pytest.mark.asyncio
    async def post_outage_ticket_with_http_400_response_test(self):
        client_id = 9994,
        service_number = "VC05400002265"

        request_params = {
            'ClientID': client_id,
            'WTNs': [service_number],
            'RequestDescription': "MetTel's IPA -- Service Outage Trouble"
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
        bruin_response_status = 400

        bruin_response = Mock()
        bruin_response.status = bruin_response_status
        bruin_response.json = CoroutineMock(return_value=bruin_response_body)

        logger = Mock()

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(bruin_client._session, 'post', new=CoroutineMock(return_value=bruin_response)):
            result = await bruin_client.post_outage_ticket(client_id, service_number)

            bruin_client._session.post.assert_awaited_with(
                f'{config.BRUIN_CONFIG["base_url"]}/api/Ticket/repair',
                headers=bruin_client._get_request_headers(),
                json=request_params,
                ssl=False
            )

        expected = {
            "body": bruin_response_body,
            "status": bruin_response_status,
        }
        assert result == expected

    @pytest.mark.asyncio
    async def post_outage_ticket_with_http_401_response_test(self):
        client_id = 9994,
        service_number = "VC05400002265"

        request_params = {
            'ClientID': client_id,
            'WTNs': [service_number],
            'RequestDescription': "MetTel's IPA -- Service Outage Trouble"
        }

        bruin_response_status = 401

        bruin_response = Mock()
        bruin_response.status = bruin_response_status

        logger = Mock()

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        bruin_client.login = CoroutineMock()

        with patch.object(bruin_client._session, 'post', new=CoroutineMock(return_value=bruin_response)):
            result = await bruin_client.post_outage_ticket(client_id, service_number)

            post_outage_ticket_call = call(
                f'{config.BRUIN_CONFIG["base_url"]}/api/Ticket/repair',
                headers=bruin_client._get_request_headers(),
                json=request_params,
                ssl=False
            )
            assert post_outage_ticket_call in bruin_client._session.post.mock_calls

        bruin_client.login.assert_awaited()

        expected = {
            "body": "Got 401 from Bruin",
            "status": bruin_response_status,
        }
        assert result == expected

    @pytest.mark.asyncio
    async def post_outage_ticket_with_http_403_response_test(self):
        client_id = 9994,
        service_number = "VC05400002265"

        request_params = {
            'ClientID': client_id,
            'WTNs': [service_number],
            'RequestDescription': "MetTel's IPA -- Service Outage Trouble"
        }

        bruin_response_status = 403

        bruin_response = Mock()
        bruin_response.status = bruin_response_status

        logger = Mock()

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        bruin_client.login = CoroutineMock()

        with patch.object(bruin_client._session, 'post', new=CoroutineMock(return_value=bruin_response)):
            result = await bruin_client.post_outage_ticket(client_id, service_number)

            bruin_client._session.post.assert_awaited_once_with(
                f'{config.BRUIN_CONFIG["base_url"]}/api/Ticket/repair',
                headers=bruin_client._get_request_headers(),
                json=request_params,
                ssl=False
            )

        expected = {
            "body": ("Permissions to create a new outage ticket with payload "
                     f"{json.dumps(request_params)} were not granted"),
            "status": bruin_response_status,
        }
        assert result == expected

    @pytest.mark.asyncio
    async def post_outage_ticket_with_http_404_response_test(self):
        client_id = 9994,
        service_number = "VC05400002265"

        url = f'{config.BRUIN_CONFIG["base_url"]}/api/Ticket/repair'
        request_params = {
            'ClientID': client_id,
            'WTNs': [service_number],
            'RequestDescription': "MetTel's IPA -- Service Outage Trouble"
        }

        bruin_response_status = 404

        bruin_response = Mock()
        bruin_response.status = bruin_response_status

        logger = Mock()

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        bruin_client.login = CoroutineMock()

        with patch.object(bruin_client._session, 'post', new=CoroutineMock(return_value=bruin_response)):
            result = await bruin_client.post_outage_ticket(client_id, service_number)

            bruin_client._session.post.assert_awaited_once_with(
                url,
                headers=bruin_client._get_request_headers(),
                json=request_params,
                ssl=False
            )

        expected = {
            "body": f"Check mistypings in URL: {url}",
            "status": bruin_response_status,
        }
        assert result == expected

    @pytest.mark.asyncio
    async def post_outage_ticket_with_http_5XX_response_test(self):
        client_id = 9994,
        service_number = "VC05400002265"

        request_params = {
            'ClientID': client_id,
            'WTNs': [service_number],
            'RequestDescription': "MetTel's IPA -- Service Outage Trouble"
        }

        bruin_response_status = 500

        bruin_response = Mock()
        bruin_response.status = bruin_response_status

        logger = Mock()

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        bruin_client.login = CoroutineMock()

        with patch.object(bruin_client._session, 'post', new=CoroutineMock(return_value=bruin_response)):
            result = await bruin_client.post_outage_ticket(client_id, service_number)

            post_outage_ticket_call = call(
                f'{config.BRUIN_CONFIG["base_url"]}/api/Ticket/repair',
                headers=bruin_client._get_request_headers(),
                json=request_params,
                ssl=False
            )
            assert post_outage_ticket_call in bruin_client._session.post.mock_calls

        expected = {
            "body": "Got internal error from Bruin",
            "status": bruin_response_status,
        }
        assert result == expected


class TestGetClientInfo:
    @pytest.mark.asyncio
    async def get_client_info_200_test(self):
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

        bruin_response_status = 200

        bruin_response = Mock()
        bruin_response.json = CoroutineMock(return_value=bruin_response_message)
        bruin_response.status = bruin_response_status

        logger = Mock()

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        bruin_client.login = CoroutineMock()

        with patch.object(bruin_client._session, 'get', new=CoroutineMock(return_value=bruin_response)):
            result = await bruin_client.get_client_info(filters)

            get_client_info_call = call(
                f'{config.BRUIN_CONFIG["base_url"]}/api/Inventory',
                headers=bruin_client._get_request_headers(),
                params=humps.pascalize(filters),
                ssl=False
            )
            assert get_client_info_call in bruin_client._session.get.mock_calls

        expected = {
            "body": bruin_response_message,
            "status": bruin_response_status,
        }
        assert result == expected

    @pytest.mark.asyncio
    async def get_client_info_test_empty_result_200(self):
        service_number = "VC01919"

        filters = {
            'service_number': service_number,
        }

        bruin_response_message = {
            "documents": []
        }

        bruin_response_status = 200

        bruin_response = Mock()
        bruin_response.json = CoroutineMock(return_value=bruin_response_message)
        bruin_response.status = bruin_response_status

        logger = Mock()

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        bruin_client.login = CoroutineMock()

        with patch.object(bruin_client._session, 'get', new=CoroutineMock(return_value=bruin_response)):
            result = await bruin_client.get_client_info(filters)

            get_client_info_call = call(
                f'{config.BRUIN_CONFIG["base_url"]}/api/Inventory',
                headers=bruin_client._get_request_headers(),
                params=humps.pascalize(filters),
                ssl=False
            )
            assert get_client_info_call in bruin_client._session.get.mock_calls

        expected = {
            "body": bruin_response_message,
            "status": bruin_response_status,
        }
        assert result == expected

    @pytest.mark.asyncio
    async def get_client_info_400_test(self):
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

        bruin_response_status = 400

        bruin_response = Mock()
        bruin_response.json = CoroutineMock(return_value=bruin_response_message)
        bruin_response.status = bruin_response_status

        logger = Mock()

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        bruin_client.login = CoroutineMock()

        with patch.object(bruin_client._session, 'get', new=CoroutineMock(return_value=bruin_response)):
            result = await bruin_client.get_client_info(filters)

            get_client_info_call = call(
                f'{config.BRUIN_CONFIG["base_url"]}/api/Inventory',
                headers=bruin_client._get_request_headers(),
                params=humps.pascalize(filters),
                ssl=False
            )
            assert get_client_info_call in bruin_client._session.get.mock_calls

        expected = {
            "body": bruin_response_message,
            "status": bruin_response_status,
        }
        assert result == expected

    @pytest.mark.asyncio
    async def get_client_info_with_ko_401_test(self):
        logger = Mock()

        filters = {
            "client_id": 9994,
            "status": "A",
            "service_number": "VC05400009999"
        }

        empty_response = {}

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=empty_response)
        response_mock.status = 401

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        bruin_client.login = CoroutineMock()

        with patch.object(bruin_client._session, 'get', new=CoroutineMock(return_value=response_mock)):
            with raises(Exception):
                bruin_client.get_client_info(filters)
                bruin_client._session.get.assert_awaited_once_with(
                    f'{bruin_client._config.BRUIN_CONFIG["base_url"]}/api/Inventory',
                    params=humps.pascalize(filters),
                    headers=bruin_client._get_request_headers(),
                    ssl=False
                )
                self.assertRaises(Exception, bruin_client.get_client_info)
                bruin_client.login.assert_awaited()

    @pytest.mark.asyncio
    async def get_client_info_with_ko_5XX_test(self):
        logger = Mock()

        filters = {
            "client_id": 9994,
            "service_number": "VC05400009999",
            "status": "A"
        }

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock()
        response_mock.status = 500

        expected_result = {"body": "Got internal error from Bruin", "status": 500}

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        bruin_client.login = CoroutineMock()

        with patch.object(bruin_client._session, 'get', new=CoroutineMock(return_value=response_mock)):
            result = await bruin_client.get_client_info(filters)
            bruin_client._session.get.assert_called_with(
                f'{bruin_client._config.BRUIN_CONFIG["base_url"]}/api/Inventory',
                params=humps.pascalize(filters),
                headers=bruin_client._get_request_headers(),
                ssl=False
            )
            assert result == expected_result

    @pytest.mark.asyncio
    async def get_client_info_with_connection_error_test(self):
        logger = Mock()

        filters = {
            "client_id": 9994,
            "service_number": "VC05400009999",
            "status": "A"
        }
        cause = "ERROR"

        message = {
            "body": f"Connection error in Bruin API. {cause}",
            "status": 500}

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        bruin_client.login = CoroutineMock()

        with patch.object(bruin_client._session, 'get', new=CoroutineMock(side_effect=ClientConnectionError(cause))):
            result = await bruin_client.get_client_info(filters)
            bruin_client._session.get.assert_called_with(
                f'{bruin_client._config.BRUIN_CONFIG["base_url"]}/api/Inventory',
                headers=bruin_client._get_request_headers(),
                params=humps.pascalize(filters),
                ssl=False
            )

            assert result == message


class TestPostMultipleTicketNotes:
    @pytest.mark.asyncio
    async def post_multiple_ticket_notes_with_connection_error_test(self):
        ticket_id = 12345
        payload = {
            "notes": [
                {
                    'noteType': 'ADN',
                    'noteValue': 'Test note 1',
                    'serviceNumber': 'VC1234567',
                },
            ],
        }
        connection_error_cause = 'Connection timed out'

        logger = Mock()

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(
            bruin_client._session,
            'post',
            new=CoroutineMock(side_effect=ClientConnectionError(connection_error_cause))
        ):
            result = await bruin_client.post_multiple_ticket_notes(ticket_id, payload)

            bruin_client._session.post.assert_awaited_with(
                f'{config.BRUIN_CONFIG["base_url"]}/api/Ticket/{ticket_id}/notes/advanced',
                headers=bruin_client._get_request_headers(),
                json=payload,
                ssl=False
            )

        expected = {
            "body": f"Connection error in Bruin API. Cause: {connection_error_cause}",
            "status": 500
        }
        assert result == expected

    @pytest.mark.asyncio
    async def post_multiple_ticket_notes_with_http_2xx_response_test(self):
        ticket_id = 12345
        payload = {
            "notes": [
                {
                    'noteType': 'ADN',
                    'noteValue': 'Test note 1',
                    'serviceNumber': 'VC1234567',
                },
            ],
        }

        bruin_response_body = {
            "ticketNotes": [
                {
                    "noteID": 70646090,
                    "noteType": "ADN",
                    "noteValue": "Test note 1",
                    "actionID": None,
                    "detailID": 5002307,
                    "enteredBy": 442301,
                    "enteredDate": "2020-05-20T06:00:38.803-04:00",
                    "lastViewedBy": None,
                    "lastViewedDate": None,
                    "refNoteID": None,
                    "noteStatus": None,
                    "noteText": None,
                    "childNotes": None,
                    "documents": None,
                    "alerts": None,
                    "taggedUserDirIDs": None,
                },
            ],
        }
        bruin_response_status = 200

        bruin_response = Mock()
        bruin_response.status = bruin_response_status
        bruin_response.json = CoroutineMock(return_value=bruin_response_body)

        logger = Mock()

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(bruin_client._session, 'post', new=CoroutineMock(return_value=bruin_response)):
            result = await bruin_client.post_multiple_ticket_notes(ticket_id, payload)

            bruin_client._session.post.assert_awaited_with(
                f'{config.BRUIN_CONFIG["base_url"]}/api/Ticket/{ticket_id}/notes/advanced',
                headers=bruin_client._get_request_headers(),
                json=payload,
                ssl=False
            )

        expected = {
            "body": bruin_response_body,
            "status": bruin_response_status,
        }
        assert result == expected

    @pytest.mark.asyncio
    async def post_multiple_ticket_notes_with_http_400_response_test(self):
        ticket_id = 12345
        payload = {
            "notes": [
                {
                    'noteType': 'ADN',
                    'noteValue': 'Test note 1',
                    'serviceNumber': 'VC1234567',
                },
            ],
        }

        bruin_response_body = 'Error in request'
        bruin_response_status = 400

        bruin_response = Mock()
        bruin_response.status = bruin_response_status
        bruin_response.json = CoroutineMock(return_value=bruin_response_body)

        logger = Mock()

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(bruin_client._session, 'post', new=CoroutineMock(return_value=bruin_response)):
            result = await bruin_client.post_multiple_ticket_notes(ticket_id, payload)

            bruin_client._session.post.assert_awaited_with(
                f'{config.BRUIN_CONFIG["base_url"]}/api/Ticket/{ticket_id}/notes/advanced',
                headers=bruin_client._get_request_headers(),
                json=payload,
                ssl=False
            )

        expected = {
            "body": bruin_response_body,
            "status": bruin_response_status,
        }
        assert result == expected

    @pytest.mark.asyncio
    async def post_multiple_ticket_notes_with_http_401_response_test(self):
        ticket_id = 12345
        payload = {
            "notes": [
                {
                    'noteType': 'ADN',
                    'noteValue': 'Test note 1',
                    'serviceNumber': 'VC1234567',
                },
            ],
        }

        bruin_response_body = "Got 401 from Bruin"
        bruin_response_status = 401

        bruin_response = Mock()
        bruin_response.status = bruin_response_status
        bruin_response.json = CoroutineMock(return_value=bruin_response_body)

        logger = Mock()

        bruin_client = BruinClient(logger, config)
        bruin_client.login = CoroutineMock()
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(bruin_client._session, 'post', new=CoroutineMock(return_value=bruin_response)):
            result = await bruin_client.post_multiple_ticket_notes(ticket_id, payload)

            bruin_client._session.post.assert_awaited_with(
                f'{config.BRUIN_CONFIG["base_url"]}/api/Ticket/{ticket_id}/notes/advanced',
                headers=bruin_client._get_request_headers(),
                json=payload,
                ssl=False
            )

        expected = {
            "body": bruin_response_body,
            "status": bruin_response_status,
        }
        assert result == expected

    @pytest.mark.asyncio
    async def post_multiple_ticket_notes_with_http_403_response_test(self):
        ticket_id = 12345
        payload = {
            "notes": [
                {
                    'noteType': 'ADN',
                    'noteValue': 'Test note 1',
                    'serviceNumber': 'VC1234567',
                },
            ],
        }

        bruin_response_body = 'Forbidden'
        bruin_response_status = 403

        bruin_response = Mock()
        bruin_response.status = bruin_response_status
        bruin_response.json = CoroutineMock(return_value=bruin_response_body)

        logger = Mock()

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(bruin_client._session, 'post', new=CoroutineMock(return_value=bruin_response)):
            result = await bruin_client.post_multiple_ticket_notes(ticket_id, payload)

            bruin_client._session.post.assert_awaited_with(
                f'{config.BRUIN_CONFIG["base_url"]}/api/Ticket/{ticket_id}/notes/advanced',
                headers=bruin_client._get_request_headers(),
                json=payload,
                ssl=False
            )

        expected = {
            "body": bruin_response_body,
            "status": bruin_response_status,
        }
        assert result == expected

    @pytest.mark.asyncio
    async def post_multiple_ticket_notes_with_http_404_response_test(self):
        ticket_id = 12345
        payload = {
            "notes": [
                {
                    'noteType': 'ADN',
                    'noteValue': 'Test note 1',
                    'serviceNumber': 'VC1234567',
                },
            ],
        }

        bruin_response_body = 'Resource not found'
        bruin_response_status = 404

        bruin_response = Mock()
        bruin_response.status = bruin_response_status
        bruin_response.json = CoroutineMock(return_value=bruin_response_body)

        logger = Mock()

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(bruin_client._session, 'post', new=CoroutineMock(return_value=bruin_response)):
            result = await bruin_client.post_multiple_ticket_notes(ticket_id, payload)

            bruin_client._session.post.assert_awaited_with(
                f'{config.BRUIN_CONFIG["base_url"]}/api/Ticket/{ticket_id}/notes/advanced',
                headers=bruin_client._get_request_headers(),
                json=payload,
                ssl=False
            )

        expected = {
            "body": bruin_response_body,
            "status": bruin_response_status,
        }
        assert result == expected

    @pytest.mark.asyncio
    async def post_multiple_ticket_notes_with_http_5xx_response_test(self):
        ticket_id = 12345
        payload = {
            "notes": [
                {
                    'noteType': 'ADN',
                    'noteValue': 'Test note 1',
                    'serviceNumber': 'VC1234567',
                },
            ],
        }

        bruin_response_body = 'Error in request'
        bruin_response_status = 400

        bruin_response = Mock()
        bruin_response.status = bruin_response_status
        bruin_response.json = CoroutineMock(return_value=bruin_response_body)

        logger = Mock()

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(bruin_client._session, 'post', new=CoroutineMock(return_value=bruin_response)):
            result = await bruin_client.post_multiple_ticket_notes(ticket_id, payload)

            bruin_client._session.post.assert_awaited_with(
                f'{config.BRUIN_CONFIG["base_url"]}/api/Ticket/{ticket_id}/notes/advanced',
                headers=bruin_client._get_request_headers(),
                json=payload,
                ssl=False
            )

        expected = {
            "body": bruin_response_body,
            "status": bruin_response_status,
        }
        assert result == expected

    @pytest.mark.asyncio
    async def get_ticket_task_history_2xx_response_test(self):
        ticket_id = 12345
        filter = {'ticket_id': ticket_id}

        results = ['List of task history']
        bruin_response_body = {'result': results}
        bruin_response_status = 200

        bruin_response = Mock()
        bruin_response.status = bruin_response_status
        bruin_response.json = CoroutineMock(return_value=bruin_response_body)

        logger = Mock()

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(bruin_client._session, 'get', new=CoroutineMock(return_value=bruin_response)):
            result = await bruin_client.get_ticket_task_history(filter)

            bruin_client._session.get.assert_called_with(
                f'{config.BRUIN_CONFIG["base_url"]}/api/Ticket/AITicketData?ticketId={filter["ticket_id"]}',
                headers=bruin_client._get_request_headers(),
                ssl=False
            )

        expected = {
            "body": bruin_response_body,
            "status": bruin_response_status,
        }
        assert result == expected

    @pytest.mark.asyncio
    async def get_ticket_task_history_400_response_test(self):
        ticket_id = 12345
        filter = {'ticket_id': ticket_id}

        bruin_response_body = {'result': 'Failure'}
        bruin_response_status = 400

        bruin_response = Mock()
        bruin_response.status = bruin_response_status
        bruin_response.json = CoroutineMock(return_value=bruin_response_body)

        logger = Mock()

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(bruin_client._session, 'get', new=CoroutineMock(return_value=bruin_response)):
            result = await bruin_client.get_ticket_task_history(filter)

            bruin_client._session.get.assert_called_with(
                f'{config.BRUIN_CONFIG["base_url"]}/api/Ticket/AITicketData?ticketId={filter["ticket_id"]}',
                headers=bruin_client._get_request_headers(),
                ssl=False
            )

        expected = {
            "body": bruin_response_body,
            "status": bruin_response_status,
        }
        assert result == expected

    @pytest.mark.asyncio
    async def get_ticket_task_history_401_response_test(self):
        ticket_id = 12345
        filter = {'ticket_id': ticket_id}

        bruin_response_body = "Got 401 from Bruin"
        bruin_response_status = 401

        bruin_response = Mock()
        bruin_response.status = bruin_response_status
        bruin_response.json = CoroutineMock(return_value=bruin_response_body)

        logger = Mock()

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(bruin_client._session, 'get', new=CoroutineMock(return_value=bruin_response)):
            result = await bruin_client.get_ticket_task_history(filter)

            bruin_client._session.get.assert_called_with(
                f'{config.BRUIN_CONFIG["base_url"]}/api/Ticket/AITicketData?ticketId={filter["ticket_id"]}',
                headers=bruin_client._get_request_headers(),
                ssl=False
            )

        expected = {
            "body": bruin_response_body,
            "status": bruin_response_status,
        }
        assert result == expected

    @pytest.mark.asyncio
    async def get_ticket_task_history_5xx_response_test(self):
        ticket_id = 12345
        filter = {'ticket_id': ticket_id}

        bruin_response_body = "Got internal error from Bruin"
        bruin_response_status = 500

        bruin_response = Mock()
        bruin_response.status = bruin_response_status
        bruin_response.json = CoroutineMock(return_value=bruin_response_body)

        logger = Mock()

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(bruin_client._session, 'get', new=CoroutineMock(return_value=bruin_response)):
            result = await bruin_client.get_ticket_task_history(filter)

            bruin_client._session.get.assert_called_with(
                f'{config.BRUIN_CONFIG["base_url"]}/api/Ticket/AITicketData?ticketId={filter["ticket_id"]}',
                headers=bruin_client._get_request_headers(),
                ssl=False
            )

        expected = {
            "body": bruin_response_body,
            "status": bruin_response_status,
        }
        assert result == expected

    @pytest.mark.asyncio
    async def get_ticket_task_history_connection_error_test(self):
        ticket_id = 12345
        filter = {'ticket_id': ticket_id}

        bruin_response_status = 500

        logger = Mock()

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        error_message = 'Failed'
        with patch.object(
            bruin_client._session,
            'get',
            new=CoroutineMock(side_effect=ClientConnectionError(error_message))
        ):
            result = await bruin_client.get_ticket_task_history(filter)

            bruin_client._session.get.assert_called_with(
                f'{config.BRUIN_CONFIG["base_url"]}/api/Ticket/AITicketData?ticketId={filter["ticket_id"]}',
                headers=bruin_client._get_request_headers(),
                ssl=False
            )

        expected = {
            "body": f"Connection error in Bruin API. {error_message}",
            "status": bruin_response_status,
        }
        assert result == expected
