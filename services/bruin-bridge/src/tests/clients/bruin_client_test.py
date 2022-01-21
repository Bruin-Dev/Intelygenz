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
        params = dict(client_id=123, ticket_id=321, ticket_status="New", product_category='SD-WAN', ticket_topic='VOO')

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
    async def get_inventory_attributes_pascalize_with_ok_test(self):
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

        valid_inventory_attributes_status = {
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
        response_mock.json = CoroutineMock(return_value=valid_inventory_attributes_status)
        response_mock.status = 200

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        bruin_client.login = CoroutineMock()

        with patch.object(bruin_client._session, 'get', new=CoroutineMock(return_value=response_mock)):
            await bruin_client.get_inventory_attributes(filters)
            bruin_client._session.get.assert_awaited_once_with(
                f'{bruin_client._config.BRUIN_CONFIG["base_url"]}/api/Inventory/Attribute',
                headers=bruin_client._get_request_headers(),
                params=pascalized_filter,
                ssl=False
            )
            response_mock.json.assert_awaited_once()

    @pytest.mark.asyncio
    async def get_inventory_attributes_with_ko_401_test(self):
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
                await bruin_client.get_inventory_attributes(filters)
                bruin_client._session.get.assert_awaited_once_with(
                    f'{bruin_client._config.BRUIN_CONFIG["base_url"]}/api/Inventory/Attribute',
                    headers=bruin_client._get_request_headers(),
                    params=pascalized_filter,
                    ssl=False
                )
                self.assertRaises(Exception, await bruin_client.get_inventory_attributes)
                bruin_client.login.assert_awaited()

    @pytest.mark.asyncio
    async def get_inventory_attributes_with_ko_400_test(self):
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
            await bruin_client.get_inventory_attributes(filters)
            bruin_client._session.get.assert_awaited_once_with(
                f'{bruin_client._config.BRUIN_CONFIG["base_url"]}/api/Inventory/Attribute',
                headers=bruin_client._get_request_headers(),
                params=pascalized_filter,
                ssl=False
            )

    @pytest.mark.asyncio
    async def get_inventory_attributes_with_ko_403_test(self):
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
            await bruin_client.get_inventory_attributes(filters)
            bruin_client._session.get.assert_awaited_once_with(
                f'{bruin_client._config.BRUIN_CONFIG["base_url"]}/api/Inventory/Attribute',
                headers=bruin_client._get_request_headers(),
                params=pascalized_filter,
                ssl=False
            )

    @pytest.mark.asyncio
    async def get_inventory_attributes_with_ko_500_test(self):
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
            await bruin_client.get_inventory_attributes(filters)
            bruin_client._session.get.assert_called_with(
                f'{bruin_client._config.BRUIN_CONFIG["base_url"]}/api/Inventory/Attribute',
                headers=bruin_client._get_request_headers(),
                params=pascalized_filter,
                ssl=False
            )

    @pytest.mark.asyncio
    async def get_inventory_attributes_with_connection_error_test(self):
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
            result = await bruin_client.get_inventory_attributes(filters)
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
        service_number = ["VC05400002265"]
        connection_error_cause = 'Connection timed out'

        request_params = {
            'ClientID': client_id,
            'WTNs': service_number,
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
        service_number = ["VC05400002265"]

        request_params = {
            'ClientID': client_id,
            'WTNs': service_number,
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
    async def post_outage_ticket_with_string_service_number_test(self):
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
        service_number = ["VC05400002265"]

        request_params = {
            'ClientID': client_id,
            'WTNs': service_number,
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
        service_number = ["VC05400002265"]

        request_params = {
            'ClientID': client_id,
            'WTNs': service_number,
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
        service_number = ["VC05400002265"]

        request_params = {
            'ClientID': client_id,
            'WTNs': service_number,
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
        service_number = ["VC05400002265"]

        request_params = {
            'ClientID': client_id,
            'WTNs': service_number,
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
        service_number = ["VC05400002265"]

        request_params = {
            'ClientID': client_id,
            'WTNs': service_number,
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
        service_number = ["VC05400002265"]

        request_params = {
            'ClientID': client_id,
            'WTNs': service_number,
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
        service_number = ["VC05400002265"]

        request_params = {
            'ClientID': client_id,
            'WTNs': service_number,
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
        service_number = ["VC05400002265"]

        url = f'{config.BRUIN_CONFIG["base_url"]}/api/Ticket/repair'
        request_params = {
            'ClientID': client_id,
            'WTNs': service_number,
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
        service_number = ["VC05400002265"]

        request_params = {
            'ClientID': client_id,
            'WTNs': service_number,
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


class TestGetClientInfoByDID:
    @pytest.mark.asyncio
    async def get_client_info_by_did_2xx_status_test(self):
        did = '+14159999999'
        request_payload = {'phoneNumber': did, 'phoneNumberType': 'DID'}

        bruin_response_body = {"inventoryId": 12345678, "clientId": 87654, "clientName": "Test Client",
                               "btn": "9876543210"}
        bruin_response_status = 200
        bruin_response = Mock()
        bruin_response.status = bruin_response_status
        bruin_response.json = CoroutineMock(return_value=bruin_response_body)

        logger = Mock()

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(bruin_client._session, 'get', new=CoroutineMock(return_value=bruin_response)):
            result = await bruin_client.get_client_info_by_did(did)

            bruin_client._session.get.assert_called_with(
                f'{config.BRUIN_CONFIG["base_url"]}/api/Inventory/phoneNumber/Lines',
                params=request_payload,
                headers=bruin_client._get_request_headers(),
                ssl=False,
            )
        expected = {
            "body": bruin_response_body,
            "status": bruin_response_status,
        }
        assert result == expected

    @pytest.mark.asyncio
    async def get_client_info_by_did_400_status_test(self):
        did = '+14159999999'
        request_payload = {'phoneNumber': did, 'phoneNumberType': 'DID'}

        bruin_response_body = 'Invalid'
        bruin_response_status = 400
        bruin_response = Mock()
        bruin_response.status = bruin_response_status
        bruin_response.json = CoroutineMock(return_value=bruin_response_body)

        logger = Mock()
        logger.error = Mock()

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(bruin_client._session, 'get', new=CoroutineMock(return_value=bruin_response)):
            result = await bruin_client.get_client_info_by_did(did)

            bruin_client._session.get.assert_called_with(
                f'{config.BRUIN_CONFIG["base_url"]}/api/Inventory/phoneNumber/Lines',
                params=request_payload,
                headers=bruin_client._get_request_headers(),
                ssl=False,
            )
        expected = {
            "body": bruin_response_body,
            "status": bruin_response_status,
        }
        logger.error.assert_called_once()
        assert result == expected

    @pytest.mark.asyncio
    async def get_client_info_by_did_401_status_test(self):
        did = '+14159999999'
        request_payload = {'phoneNumber': did, 'phoneNumberType': 'DID'}

        bruin_response_body = '401 error'
        bruin_response_status = 401
        bruin_response = Mock()
        bruin_response.status = bruin_response_status
        bruin_response.json = CoroutineMock(return_value=bruin_response_body)

        logger = Mock()
        logger.error = Mock()

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        bruin_client.login = CoroutineMock()

        with patch.object(bruin_client._session, 'get', new=CoroutineMock(return_value=bruin_response)):
            result = await bruin_client.get_client_info_by_did(did)

            bruin_client._session.get.assert_called_with(
                f'{config.BRUIN_CONFIG["base_url"]}/api/Inventory/phoneNumber/Lines',
                params=request_payload,
                headers=bruin_client._get_request_headers(),
                ssl=False,
            )
            bruin_client.login.assert_awaited_once()
        expected = {
            "body": "Got 401 from Bruin",
            "status": bruin_response_status,
        }
        logger.error.assert_called_once()
        assert result == expected

    @pytest.mark.asyncio
    async def get_client_info_by_did_5xx_status_test(self):
        did = '+14159999999'
        request_payload = {'phoneNumber': did, 'phoneNumberType': 'DID'}

        bruin_response_body = 'Internal Error'
        bruin_response_status = 500
        bruin_response = Mock()
        bruin_response.status = bruin_response_status
        bruin_response.json = CoroutineMock(return_value=bruin_response_body)

        logger = Mock()
        logger.error = Mock()

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(bruin_client._session, 'get', new=CoroutineMock(return_value=bruin_response)):
            result = await bruin_client.get_client_info_by_did(did)

            bruin_client._session.get.assert_called_with(
                f'{config.BRUIN_CONFIG["base_url"]}/api/Inventory/phoneNumber/Lines',
                params=request_payload,
                headers=bruin_client._get_request_headers(),
                ssl=False,
            )

        expected = {
            "body": "Got internal error from Bruin",
            "status": bruin_response_status,
        }
        assert result == expected

    @pytest.mark.asyncio
    async def get_client_info_by_did_connection_error_test(self):
        did = '+14159999999'
        request_payload = {'phoneNumber': did, 'phoneNumberType': 'DID'}

        bruin_response_body = 'Internal Error'
        bruin_response_status = 500
        bruin_response = Mock()
        bruin_response.status = bruin_response_status
        bruin_response.json = CoroutineMock(return_value=bruin_response_body)

        logger = Mock()
        logger.error = Mock()

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        cause = "ERROR"

        with patch.object(bruin_client._session, 'get', new=CoroutineMock(side_effect=ClientConnectionError(cause))):
            result = await bruin_client.get_client_info_by_did(did)

            bruin_client._session.get.assert_called_with(
                f'{config.BRUIN_CONFIG["base_url"]}/api/Inventory/phoneNumber/Lines',
                params=request_payload,
                headers=bruin_client._get_request_headers(),
                ssl=False,
            )

        expected = {
            "body": f"Connection error in Bruin API. {cause}",
            "status": bruin_response_status,
        }
        logger.error.assert_called()
        assert result == expected


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

    @pytest.mark.asyncio
    async def get_tickets_basic_info_ok_test(self):
        service_number = 'VC1234567'
        product_category = 'SD-WAN'
        ticket_status = 'Resolved'

        input_payload = {
            'service_number': service_number,
            'product_category': product_category,
            'ticket_status': ticket_status,
        }

        request_payload = {
            'ServiceNumber': service_number,
            'ProductCategory': product_category,
            'TicketStatus': ticket_status,
        }

        tickets = [
            {
                "clientID": 30000,
                "ticketID": 5262293,
                "ticketStatus": "In-Progress",
                "address": {
                    "address": "1090 Vermont Ave NW",
                    "city": "Washington",
                    "state": "DC",
                    "zip": "20005-4905",
                    "country": "USA"
                },
                "createDate": "3/13/2021 12:59:36 PM",
            }
        ]
        bruin_response_body = {
            'responses': tickets,
        }
        bruin_response_status = 200

        logger = Mock()

        bruin_response = Mock()
        bruin_response.status = bruin_response_status
        bruin_response.json = CoroutineMock(return_value=bruin_response_body)

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(bruin_client._session, 'get', new=CoroutineMock(return_value=bruin_response)):
            result = await bruin_client.get_tickets_basic_info(input_payload)

            bruin_client._session.get.assert_called_with(
                f'{config.BRUIN_CONFIG["base_url"]}/api/Ticket/basic',
                params=request_payload,
                headers=bruin_client._get_request_headers(),
                ssl=False,
            )

        expected = {
            "body": bruin_response_body,
            "status": bruin_response_status,
        }
        assert result == expected

    @pytest.mark.asyncio
    async def get_tickets_basic_info_with_400_status_test(self):
        input_payload = {
            'unknown_field': 'Fake value',
        }

        request_payload = {
            'UnknownField': 'Fake value',
        }

        bruin_response_body = 'No valid query parameters were sent'
        bruin_response_status = 400

        logger = Mock()

        bruin_response = Mock()
        bruin_response.status = bruin_response_status
        bruin_response.json = CoroutineMock(return_value=bruin_response_body)

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(bruin_client._session, 'get', new=CoroutineMock(return_value=bruin_response)):
            result = await bruin_client.get_tickets_basic_info(input_payload)

            bruin_client._session.get.assert_called_with(
                f'{config.BRUIN_CONFIG["base_url"]}/api/Ticket/basic',
                params=request_payload,
                headers=bruin_client._get_request_headers(),
                ssl=False,
            )

        expected = {
            "body": bruin_response_body,
            "status": bruin_response_status,
        }
        assert result == expected

    @pytest.mark.asyncio
    async def get_tickets_basic_info_with_401_status_test(self):
        service_number = 'VC1234567'
        product_category = 'SD-WAN'
        ticket_status = 'Resolved'

        input_payload = {
            'service_number': service_number,
            'product_category': product_category,
            'ticket_status': ticket_status,
        }

        request_payload = {
            'ServiceNumber': service_number,
            'ProductCategory': product_category,
            'TicketStatus': ticket_status,
        }

        bruin_response_body = 'Got 401 from Bruin'
        bruin_response_status = 401

        logger = Mock()

        bruin_response = Mock()
        bruin_response.status = bruin_response_status
        bruin_response.json = CoroutineMock(return_value=bruin_response_body)

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        bruin_client.login = CoroutineMock()

        with patch.object(bruin_client._session, 'get', new=CoroutineMock(return_value=bruin_response)):
            result = await bruin_client.get_tickets_basic_info(input_payload)

            bruin_client._session.get.assert_called_with(
                f'{config.BRUIN_CONFIG["base_url"]}/api/Ticket/basic',
                params=request_payload,
                headers=bruin_client._get_request_headers(),
                ssl=False,
            )
            bruin_client.login.assert_awaited_once()

        expected = {
            "body": bruin_response_body,
            "status": bruin_response_status,
        }
        assert result == expected

    @pytest.mark.asyncio
    async def get_tickets_basic_info_with_403_status_test(self):
        service_number = 'VC1234567'
        product_category = 'SD-WAN'
        ticket_status = 'Resolved'

        input_payload = {
            'service_number': service_number,
            'product_category': product_category,
            'ticket_status': ticket_status,
        }

        request_payload = {
            'ServiceNumber': service_number,
            'ProductCategory': product_category,
            'TicketStatus': ticket_status,
        }

        bruin_response_body = 'Access to requested resources is forbidden'
        bruin_response_status = 403

        logger = Mock()

        bruin_response = Mock()
        bruin_response.status = bruin_response_status
        bruin_response.json = CoroutineMock(return_value=bruin_response_body)

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(bruin_client._session, 'get', new=CoroutineMock(return_value=bruin_response)):
            result = await bruin_client.get_tickets_basic_info(input_payload)

            bruin_client._session.get.assert_called_with(
                f'{config.BRUIN_CONFIG["base_url"]}/api/Ticket/basic',
                params=request_payload,
                headers=bruin_client._get_request_headers(),
                ssl=False,
            )

        expected = {
            "body": bruin_response_body,
            "status": bruin_response_status,
        }
        assert result == expected

    @pytest.mark.asyncio
    async def get_tickets_basic_info_with_404_status_test(self):
        service_number = 'VC1234567'
        product_category = 'SD-WAN'
        ticket_status = 'Resolved'

        input_payload = {
            'service_number': service_number,
            'product_category': product_category,
            'ticket_status': ticket_status,
        }

        request_payload = {
            'ServiceNumber': service_number,
            'ProductCategory': product_category,
            'TicketStatus': ticket_status,
        }

        bruin_response_body = 'Resource not found'
        bruin_response_status = 404

        logger = Mock()

        bruin_response = Mock()
        bruin_response.status = bruin_response_status
        bruin_response.json = CoroutineMock(return_value=bruin_response_body)

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(bruin_client._session, 'get', new=CoroutineMock(return_value=bruin_response)):
            result = await bruin_client.get_tickets_basic_info(input_payload)

            bruin_client._session.get.assert_called_with(
                f'{config.BRUIN_CONFIG["base_url"]}/api/Ticket/basic',
                params=request_payload,
                headers=bruin_client._get_request_headers(),
                ssl=False,
            )

        expected = {
            "body": bruin_response_body,
            "status": bruin_response_status,
        }
        assert result == expected

    @pytest.mark.asyncio
    async def get_tickets_basic_info_with_5xx_status_test(self):
        service_number = 'VC1234567'
        product_category = 'SD-WAN'
        ticket_status = 'Resolved'

        input_payload = {
            'service_number': service_number,
            'product_category': product_category,
            'ticket_status': ticket_status,
        }

        request_payload = {
            'ServiceNumber': service_number,
            'ProductCategory': product_category,
            'TicketStatus': ticket_status,
        }

        bruin_response_body = 'Got internal error from Bruin'
        bruin_response_status = 500

        logger = Mock()

        bruin_response = Mock()
        bruin_response.status = bruin_response_status
        bruin_response.json = CoroutineMock(return_value=bruin_response_body)

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(bruin_client._session, 'get', new=CoroutineMock(return_value=bruin_response)):
            result = await bruin_client.get_tickets_basic_info(input_payload)

            bruin_client._session.get.assert_called_with(
                f'{config.BRUIN_CONFIG["base_url"]}/api/Ticket/basic',
                params=request_payload,
                headers=bruin_client._get_request_headers(),
                ssl=False,
            )

        expected = {
            "body": bruin_response_body,
            "status": bruin_response_status,
        }
        assert result == expected

    @pytest.mark.asyncio
    async def get_tickets_basic_info_with_connection_error_test(self):
        service_number = 'VC1234567'
        product_category = 'SD-WAN'
        ticket_status = 'Resolved'

        input_payload = {
            'service_number': service_number,
            'product_category': product_category,
            'ticket_status': ticket_status,
        }

        request_payload = {
            'ServiceNumber': service_number,
            'ProductCategory': product_category,
            'TicketStatus': ticket_status,
        }

        logger = Mock()

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        err_msg = 'Failed'
        get_mock = CoroutineMock(side_effect=ClientConnectionError(err_msg))
        with patch.object(bruin_client._session, 'get', new=get_mock):
            result = await bruin_client.get_tickets_basic_info(input_payload)

            bruin_client._session.get.assert_called_with(
                f'{config.BRUIN_CONFIG["base_url"]}/api/Ticket/basic',
                params=request_payload,
                headers=bruin_client._get_request_headers(),
                ssl=False,
            )

        expected = {
            "body": f"Connection error in Bruin API. Cause: {err_msg}",
            "status": 500,
        }
        assert result == expected

    @pytest.mark.asyncio
    async def get_circuit_id_2xx_status_test(self):
        circuit_id = '123'
        client_id = '321'

        input_payload = {
            'circuit_id': circuit_id,
            'client_id': client_id,
        }

        request_payload = {
            'CircuitId': circuit_id,
            'ClientId': client_id,
        }

        bruin_response_body = {"clientID": client_id, "subAccount": "string", "wtn": circuit_id,
                               "inventoryID": 0, "addressID": 0}
        bruin_response_status = 200
        bruin_response = Mock()
        bruin_response.status = bruin_response_status
        bruin_response.json = CoroutineMock(return_value=bruin_response_body)

        logger = Mock()

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(bruin_client._session, 'get', new=CoroutineMock(return_value=bruin_response)):
            result = await bruin_client.get_circuit_id(input_payload)

            bruin_client._session.get.assert_called_with(
                f'{config.BRUIN_CONFIG["base_url"]}/api/Inventory/circuit',
                params=request_payload,
                headers=bruin_client._get_request_headers(),
                ssl=False,
            )
        expected = {
            "body": bruin_response_body,
            "status": bruin_response_status,
        }
        assert result == expected

    @pytest.mark.asyncio
    async def get_circuit_id_204_status_test(self):
        circuit_id = '123'
        client_id = '321'

        input_payload = {
            'circuit_id': circuit_id,
            'client_id': client_id,
        }

        request_payload = {
            'CircuitId': circuit_id,
            'ClientId': client_id,
        }

        bruin_response_body = ''
        bruin_response_status = 204
        bruin_response = Mock()
        bruin_response.status = bruin_response_status
        bruin_response.json = CoroutineMock(return_value=bruin_response_body)

        logger = Mock()

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(bruin_client._session, 'get', new=CoroutineMock(return_value=bruin_response)):
            result = await bruin_client.get_circuit_id(input_payload)

            bruin_client._session.get.assert_called_with(
                f'{config.BRUIN_CONFIG["base_url"]}/api/Inventory/circuit',
                params=request_payload,
                headers=bruin_client._get_request_headers(),
                ssl=False,
            )
        expected = {
            "body": '204 No Content',
            "status": bruin_response_status,
        }
        assert result == expected

    @pytest.mark.asyncio
    async def get_circuit_id_400_status_test(self):
        circuit_id = '123'
        client_id = '321'

        input_payload = {
            'circuit_id': circuit_id,
            'client_id': client_id,
        }

        request_payload = {
            'CircuitId': circuit_id,
            'ClientId': client_id,
        }

        bruin_response_body = 'Invalid'
        bruin_response_status = 400
        bruin_response = Mock()
        bruin_response.status = bruin_response_status
        bruin_response.json = CoroutineMock(return_value=bruin_response_body)

        logger = Mock()
        logger.error = Mock()

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(bruin_client._session, 'get', new=CoroutineMock(return_value=bruin_response)):
            result = await bruin_client.get_circuit_id(input_payload)

            bruin_client._session.get.assert_called_with(
                f'{config.BRUIN_CONFIG["base_url"]}/api/Inventory/circuit',
                params=request_payload,
                headers=bruin_client._get_request_headers(),
                ssl=False,
            )
        expected = {
            "body": bruin_response_body,
            "status": bruin_response_status,
        }
        logger.error.assert_called_once()
        assert result == expected

    @pytest.mark.asyncio
    async def get_circuit_id_401_status_test(self):
        circuit_id = '123'
        client_id = '321'

        input_payload = {
            'circuit_id': circuit_id,
            'client_id': client_id,
        }

        request_payload = {
            'CircuitId': circuit_id,
            'ClientId': client_id,
        }

        bruin_response_body = '401 error'
        bruin_response_status = 401
        bruin_response = Mock()
        bruin_response.status = bruin_response_status
        bruin_response.json = CoroutineMock(return_value=bruin_response_body)

        logger = Mock()
        logger.error = Mock()

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        bruin_client.login = CoroutineMock()

        with patch.object(bruin_client._session, 'get', new=CoroutineMock(return_value=bruin_response)):
            result = await bruin_client.get_circuit_id(input_payload)

            bruin_client._session.get.assert_called_with(
                f'{config.BRUIN_CONFIG["base_url"]}/api/Inventory/circuit',
                params=request_payload,
                headers=bruin_client._get_request_headers(),
                ssl=False,
            )
            bruin_client.login.assert_awaited_once()
        expected = {
            "body": "Got 401 from Bruin",
            "status": bruin_response_status,
        }
        logger.error.assert_called_once()
        assert result == expected

    @pytest.mark.asyncio
    async def get_circuit_id_403_status_test(self):
        circuit_id = '123'
        client_id = '321'

        input_payload = {
            'circuit_id': circuit_id,
            'client_id': client_id,
        }

        request_payload = {
            'CircuitId': circuit_id,
            'ClientId': client_id,
        }

        bruin_response_body = 'Forbidden error'
        bruin_response_status = 403
        bruin_response = Mock()
        bruin_response.status = bruin_response_status
        bruin_response.json = CoroutineMock(return_value=bruin_response_body)

        logger = Mock()
        logger.error = Mock()

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(bruin_client._session, 'get', new=CoroutineMock(return_value=bruin_response)):
            result = await bruin_client.get_circuit_id(input_payload)

            bruin_client._session.get.assert_called_with(
                f'{config.BRUIN_CONFIG["base_url"]}/api/Inventory/circuit',
                params=request_payload,
                headers=bruin_client._get_request_headers(),
                ssl=False,
            )

        expected = {
            "body": bruin_response_body,
            "status": bruin_response_status,
        }
        logger.error.assert_called()
        assert result == expected

    @pytest.mark.asyncio
    async def get_circuit_id_5xx_status_test(self):
        circuit_id = '123'
        client_id = '321'

        input_payload = {
            'circuit_id': circuit_id,
            'client_id': client_id,
        }

        request_payload = {
            'CircuitId': circuit_id,
            'ClientId': client_id,
        }

        bruin_response_body = 'Internal Error'
        bruin_response_status = 500
        bruin_response = Mock()
        bruin_response.status = bruin_response_status
        bruin_response.json = CoroutineMock(return_value=bruin_response_body)

        logger = Mock()
        logger.error = Mock()

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(bruin_client._session, 'get', new=CoroutineMock(return_value=bruin_response)):
            result = await bruin_client.get_circuit_id(input_payload)

            bruin_client._session.get.assert_called_with(
                f'{config.BRUIN_CONFIG["base_url"]}/api/Inventory/circuit',
                params=request_payload,
                headers=bruin_client._get_request_headers(),
                ssl=False,
            )

        expected = {
            "body": "Got internal error from Bruin",
            "status": bruin_response_status,
        }
        logger.error.assert_called()
        assert result == expected

    @pytest.mark.asyncio
    async def get_circuit_id_connection_error_test(self):
        circuit_id = '123'
        client_id = '321'

        input_payload = {
            'circuit_id': circuit_id,
            'client_id': client_id,
        }

        request_payload = {
            'CircuitId': circuit_id,
            'ClientId': client_id,
        }

        bruin_response_body = 'Internal Error'
        bruin_response_status = 500
        bruin_response = Mock()
        bruin_response.status = bruin_response_status
        bruin_response.json = CoroutineMock(return_value=bruin_response_body)

        logger = Mock()
        logger.error = Mock()

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        cause = "ERROR"

        with patch.object(bruin_client._session, 'get', new=CoroutineMock(side_effect=ClientConnectionError(cause))):
            result = await bruin_client.get_circuit_id(input_payload)

            bruin_client._session.get.assert_called_with(
                f'{config.BRUIN_CONFIG["base_url"]}/api/Inventory/circuit',
                params=request_payload,
                headers=bruin_client._get_request_headers(),
                ssl=False,
            )

        expected = {
            "body": f"Connection error in Bruin API. {cause}",
            "status": bruin_response_status,
        }
        logger.error.assert_called()
        assert result == expected

    @pytest.mark.asyncio
    async def post_email_tag_test(self):
        logger = Mock()
        logger.error = Mock()

        email_id = "A1234576"
        tag_id = '1001'
        expected_post_response = None

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=expected_post_response)
        response_mock.status = 204

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(bruin_client._session, 'post', new=CoroutineMock(return_value=response_mock)) as mock_post:
            post_response = await bruin_client.post_email_tag(email_id, tag_id)

            mock_post.assert_called_once()
            assert post_response["body"] == ""
            assert post_response["status"] == 204

    @pytest.mark.asyncio
    async def post_email_tag_400_status_test(self):
        logger = Mock()
        logger.error = Mock()
        email_id = "A1234576"
        tag_id = '1001'
        expected_post_response = {'response': 'Error 400'}

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=expected_post_response)
        response_mock.status = 400

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        bruin_client.login = CoroutineMock()

        with patch.object(bruin_client._session, 'post', new=CoroutineMock(return_value=response_mock)):
            post_response = await bruin_client.post_email_tag(email_id, tag_id)
            logger.error.assert_called()

            assert post_response["body"] == expected_post_response
            assert post_response["status"] == 400

    @pytest.mark.asyncio
    async def post_email_tag_401_status_test(self):
        logger = Mock()
        logger.error = Mock()
        email_id = "A1234576"
        tag_id = '1001'
        expected_post_response = {'response': 'Error 401'}

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=expected_post_response)
        response_mock.status = 401

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        bruin_client.login = CoroutineMock()

        with patch.object(bruin_client._session, 'post', new=CoroutineMock(return_value=response_mock)):
            post_response = await bruin_client.post_email_tag(email_id, tag_id)
            logger.error.assert_called()

            assert post_response["body"] == "Got 401 from Bruin"
            assert post_response["status"] == 401

    @pytest.mark.asyncio
    async def post_email_tag_403_status_test(self):
        logger = Mock()
        logger.error = Mock()
        email_id = "A1234576"
        tag_id = '1001'
        expected_post_response = {'response': 'Error 403'}

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=expected_post_response)
        response_mock.status = 403

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        bruin_client.login = CoroutineMock()

        with patch.object(bruin_client._session, 'post', new=CoroutineMock(return_value=response_mock)):
            post_response = await bruin_client.post_email_tag(email_id, tag_id)
            logger.error.assert_called()

            assert post_response["body"] == expected_post_response
            assert post_response["status"] == 403

    @pytest.mark.asyncio
    async def post_email_tag_404_status_test(self):
        logger = Mock()
        logger.error = Mock()
        email_id = "A1234576"
        tag_id = '1001'
        expected_post_response = {'response': 'Error 400'}

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=expected_post_response)
        response_mock.status = 404

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        bruin_client.login = CoroutineMock()

        with patch.object(bruin_client._session, 'post', new=CoroutineMock(return_value=response_mock)):
            post_response = await bruin_client.post_email_tag(email_id, tag_id)
            logger.error.assert_called()

            assert post_response["body"] == "Resource not found"
            assert post_response["status"] == 404

    @pytest.mark.asyncio
    async def post_email_tag_409_status_test(self):
        logger = Mock()
        logger.error = Mock()
        email_id = "A1234576"
        tag_id = '1001'
        expected_post_response = {}

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=expected_post_response)
        response_mock.status = 409

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        bruin_client.login = CoroutineMock()

        with patch.object(bruin_client._session, 'post', new=CoroutineMock(return_value=response_mock)):
            post_response = await bruin_client.post_email_tag(email_id, tag_id)
            logger.error.assert_called()

            assert post_response["body"] == f"Tag with ID {tag_id} already present in e-mail with ID {email_id}"
            assert post_response["status"] == 409

    @pytest.mark.asyncio
    async def post_email_tag_500_status_test(self):
        logger = Mock()
        logger.error = Mock()
        email_id = "A1234576"
        tag_id = '1001'
        expected_post_response = {}

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=expected_post_response)
        response_mock.status = 500

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        bruin_client.login = CoroutineMock()

        with patch.object(bruin_client._session, 'post', new=CoroutineMock(return_value=response_mock)):
            post_response = await bruin_client.post_email_tag(email_id, tag_id)
            logger.error.assert_called()

            assert post_response["body"] == "Got internal error from Bruin"
            assert post_response["status"] == 500


class TestChangeTicketSeverity:
    @pytest.mark.asyncio
    async def change_ticket_severity_ok_test(self):
        logger = Mock()

        ticket_id = 123
        severity_level = 2
        reason_for_change = 'WTN has been under troubles for a long time'

        payload = {
            'Severity': severity_level,
            'Reason': reason_for_change,
        }

        response_json = {
            'TicketId': ticket_id,
            'Result': True,
        }
        response_status = 200

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=response_json)
        response_mock.status = response_status

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(bruin_client._session, 'put', new=CoroutineMock(return_value=response_mock)) as mock_put:
            result = await bruin_client.change_ticket_severity(ticket_id, payload)

        mock_put.assert_called_once()
        assert result["body"] == response_json
        assert result["status"] == response_status

    @pytest.mark.asyncio
    async def change_ticket_severity_with_400_status_test(self):
        logger = Mock()

        ticket_id = 123
        reason_for_change = 'WTN has been under troubles for a long time'

        payload = {
            # "Severity" field missing on purpose
            'Reason': reason_for_change,
        }

        response_status = 400
        response_json = {
            "message": "Invalid Severity",
            "messageDetail": None,
            "data": None,
            "type": "ApiValidationException",
            "code": response_status,
        }

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=response_json)
        response_mock.status = response_status

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(bruin_client._session, 'put', new=CoroutineMock(return_value=response_mock)) as mock_put:
            result = await bruin_client.change_ticket_severity(ticket_id, payload)

        mock_put.assert_called_once()
        assert result["body"] == response_json
        assert result["status"] == response_status

    @pytest.mark.asyncio
    async def change_ticket_severity_with_401_status_test(self):
        logger = Mock()

        ticket_id = 123
        severity_level = 2
        reason_for_change = 'WTN has been under troubles for a long time'

        payload = {
            'Severity': severity_level,
            'Reason': reason_for_change,
        }

        response_status = 401

        response_mock = CoroutineMock()
        response_mock.status = response_status

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(bruin_client._session, 'put', new=CoroutineMock(return_value=response_mock)) as mock_put:
            result = await bruin_client.change_ticket_severity(ticket_id, payload)

        mock_put.assert_called_once()
        assert result["body"] == 'Got 401 from Bruin'
        assert result["status"] == response_status

    @pytest.mark.asyncio
    async def change_ticket_severity_with_403_status_test(self):
        logger = Mock()

        ticket_id = 123
        severity_level = 2
        reason_for_change = 'WTN has been under troubles for a long time'

        payload = {
            'Severity': severity_level,
            'Reason': reason_for_change,
        }

        response_status = 403

        response_mock = CoroutineMock()
        response_mock.status = response_status

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(bruin_client._session, 'put', new=CoroutineMock(return_value=response_mock)) as mock_put:
            result = await bruin_client.change_ticket_severity(ticket_id, payload)

        mock_put.assert_called_once()
        assert result["body"] == (
            f'Permissions to change the severity level of ticket {ticket_id} were not granted'
        )
        assert result["status"] == response_status

    @pytest.mark.asyncio
    async def change_ticket_severity_with_404_status_test(self):
        logger = Mock()

        ticket_id = 123
        severity_level = 2
        reason_for_change = 'WTN has been under troubles for a long time'

        payload = {
            'Severity': severity_level,
            'Reason': reason_for_change,
        }

        response_status = 404

        response_mock = CoroutineMock()
        response_mock.status = response_status

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(bruin_client._session, 'put', new=CoroutineMock(return_value=response_mock)) as mock_put:
            result = await bruin_client.change_ticket_severity(ticket_id, payload)

        mock_put.assert_called_once()
        assert result["body"] == 'Resource not found'
        assert result["status"] == response_status

    @pytest.mark.asyncio
    async def change_ticket_severity_with_500_status_test(self):
        logger = Mock()

        ticket_id = 123
        severity_level = 2
        reason_for_change = 'WTN has been under troubles for a long time'

        payload = {
            'Severity': severity_level,
            'Reason': reason_for_change,
        }

        response_status = 500

        response_mock = CoroutineMock()
        response_mock.status = response_status

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(bruin_client._session, 'put', new=CoroutineMock(return_value=response_mock)) as mock_put:
            result = await bruin_client.change_ticket_severity(ticket_id, payload)

        mock_put.assert_called_once()
        assert result["body"] == 'Got internal error from Bruin'
        assert result["status"] == response_status

    @pytest.mark.asyncio
    async def change_ticket_severity_with_connection_error_test(self):
        logger = Mock()

        ticket_id = 123
        severity_level = 2
        reason_for_change = 'WTN has been under troubles for a long time'

        payload = {
            'Severity': severity_level,
            'Reason': reason_for_change,
        }

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        error = 'Connection was closed by Bruin server'
        with patch.object(bruin_client._session, 'put', new=CoroutineMock(side_effect=ClientConnectionError(error))):
            result = await bruin_client.change_ticket_severity(ticket_id, payload)

        expected = {
            "body": f"Connection error in Bruin API: {error}",
            "status": 500,
        }
        assert result == expected

    @pytest.mark.asyncio
    async def get_site_test(self):
        logger = Mock()
        client_id = 72959
        site_id = 343443
        params = {
            "client_id": client_id,
            "site_id": site_id
        }
        get_site_response = {
          "documents": [
            {
              "clientID": client_id,
              "clientName": "TENET",
              "siteID": f"{site_id}",
              "siteLabel": "TENET",
              "siteAddDate": "2018-07-05T06:18:20.723Z",
              "address": {
                "addressID": 311716,
                "address": "8200 Perrin Beitel Rd",
                "city": "San Antonio",
                "state": "TX",
                "zip": "78218-1547",
                "country": "USA"
              },
              "longitude": -98.4096658,
              "latitude": 29.5125306,
              "businessHours": None,
              "timeZone": None,
              "primaryContactName": "primaryContactName string",
              "primaryContactPhone": "primaryContactPhone string",
              "primaryContactEmail": "some@email.com"
            }
          ]
        }

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=get_site_response)
        response_mock.status = 200

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"

        with patch.object(bruin_client._session, 'get', new=CoroutineMock(return_value=response_mock)) as mock_get:
            ticket_details = await bruin_client.get_site(params)

            mock_get.assert_called_once()
            assert ticket_details["body"] == get_site_response
            assert ticket_details["status"] == 200

    @pytest.mark.asyncio
    async def get_site_with_400_status_test(self):
        logger = Mock()
        logger.error = Mock()
        client_id = 72959
        site_id = 343443
        params = {
            "client_id": client_id,
            "site_id": site_id
        }
        error_response = {'error': "400 error"}

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=error_response)
        response_mock.status = 400

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        bruin_client.login = CoroutineMock()

        with patch.object(bruin_client._session, 'get', new=CoroutineMock(return_value=response_mock)):
            ticket_details = await bruin_client.get_site(params)
            logger.error.assert_called()

            assert ticket_details['body'] == error_response
            assert ticket_details['status'] == 400

    @pytest.mark.asyncio
    async def get_site_with_401_status_test(self):
        logger = Mock()
        logger.error = Mock()
        client_id = 72959
        site_id = 343443
        params = {
            "client_id": client_id,
            "site_id": site_id
        }

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value={})
        response_mock.status = 401

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        bruin_client.login = CoroutineMock()

        with patch.object(bruin_client._session, 'get', new=CoroutineMock(return_value=response_mock)):
            ticket_details = await bruin_client.get_site(params)
            bruin_client.login.assert_awaited()
            logger.error.assert_called()

            assert ticket_details['body'] == "Got 401 from Bruin"
            assert ticket_details['status'] == 401

    @pytest.mark.asyncio
    async def get_site_with_403_status_test(self):
        logger = Mock()
        logger.error = Mock()
        client_id = 72959
        site_id = 343443
        params = {
            "client_id": client_id,
            "site_id": site_id
        }
        error_response = {'error': "403 error"}

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=error_response)
        response_mock.status = 403

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        bruin_client.login = CoroutineMock()

        with patch.object(bruin_client._session, 'get', new=CoroutineMock(return_value=response_mock)):
            ticket_details = await bruin_client.get_site(params)
            logger.error.assert_called()

            assert ticket_details['body'] == error_response
            assert ticket_details['status'] == 403

    @pytest.mark.asyncio
    async def get_site_with_404_status_test(self):
        logger = Mock()
        logger.error = Mock()
        client_id = 72959
        site_id = 343443
        params = {
            "client_id": client_id,
            "site_id": site_id
        }

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value={})
        response_mock.status = 404

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        bruin_client.login = CoroutineMock()

        with patch.object(bruin_client._session, 'get', new=CoroutineMock(return_value=response_mock)):
            ticket_details = await bruin_client.get_site(params)
            logger.error.assert_called()

            assert ticket_details['body'] == "Resource not found"
            assert ticket_details['status'] == 404

    @pytest.mark.asyncio
    async def get_site_with_500_status_test(self):
        logger = Mock()
        logger.error = Mock()
        client_id = 72959
        site_id = 343443
        params = {
            "client_id": client_id,
            "site_id": site_id
        }

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value={})
        response_mock.status = 500

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        bruin_client.login = CoroutineMock()

        with patch.object(bruin_client._session, 'get', new=CoroutineMock(return_value=response_mock)):
            ticket_details = await bruin_client.get_site(params)
            logger.error.assert_called()

            assert ticket_details['body'] == "Got internal error from Bruin"
            assert ticket_details['status'] == 500

    @pytest.mark.asyncio
    async def mark_email_as_done_test(self):
        email_id = 1234

        logger = Mock()

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value={"success": True, "email_id": email_id})
        response_mock.status = 200

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        bruin_client.login = CoroutineMock()

        with patch.object(bruin_client._session, 'post', new=CoroutineMock(return_value=response_mock)):
            response = await bruin_client.mark_email_as_done(email_id)

        assert response['status'] == 200
        assert response['body']['success'] is True
        assert response['body']['email_id'] == email_id

    @pytest.mark.asyncio
    async def mark_email_as_done_400_test(self):
        email_id = 1234

        logger = Mock()

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value="Error 400")
        response_mock.status = 400

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        bruin_client.login = CoroutineMock()

        with patch.object(bruin_client._session, 'post', new=CoroutineMock(return_value=response_mock)):
            response = await bruin_client.mark_email_as_done(email_id)

        assert response['status'] == 400
        assert response['body'] == "Error 400"

    @pytest.mark.asyncio
    async def mark_email_as_done_401_test(self):
        email_id = 1234

        logger = Mock()

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value="Error 400")
        response_mock.status = 401

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        bruin_client.login = CoroutineMock()

        with patch.object(bruin_client._session, 'post', new=CoroutineMock(return_value=response_mock)):
            response = await bruin_client.mark_email_as_done(email_id)

        logger.error.assert_called_once_with("Got 401 from Bruin. Re-logging in...")
        assert response['status'] == 401
        assert response['body'] == "Got 401 from Bruin"

    @pytest.mark.asyncio
    async def mark_email_as_done_5xx_test(self):
        email_id = 1234

        logger = Mock()

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value="Error 400")
        response_mock.status = 505

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        bruin_client.login = CoroutineMock()

        with patch.object(bruin_client._session, 'post', new=CoroutineMock(return_value=response_mock)):
            response = await bruin_client.mark_email_as_done(email_id)

        logger.error.assert_called_once_with("Got HTTP 505 from Bruin")
        assert response['status'] == 500
        assert response['body'] == "Got internal error from Bruin"

    @pytest.mark.asyncio
    async def link_ticket_to_email_200_test(self):
        email_id = 1234
        ticket_id = 5678
        response_dict = {
            "success": True,
            "emailId": 3842493,
            "ticketId": 6112476,
            "totalEmailAffected": 1,
            "warnings": []
        }

        logger = Mock()

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=response_dict)
        response_mock.status = 200

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        bruin_client.login = CoroutineMock()

        with patch.object(bruin_client._session, 'post', new=CoroutineMock(return_value=response_mock)):
            response = await bruin_client.link_ticket_to_email(ticket_id, email_id)

        assert response['status'] == 200
        assert response['body']['success'] is True

    @pytest.mark.asyncio
    async def link_ticket_to_email_401_test(self):
        email_id = 1234
        ticket_id = 5678

        logger = Mock()

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value={})
        response_mock.status = 401

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        bruin_client.login = CoroutineMock()

        with patch.object(bruin_client._session, 'post', new=CoroutineMock(return_value=response_mock)):
            response = await bruin_client.link_ticket_to_email(ticket_id, email_id)

        logger.error.assert_called_once_with("Got 401 from Bruin. Re-logging in...")
        assert response['status'] == 401
        assert response['body'] == "Got 401 from Bruin"

    @pytest.mark.asyncio
    async def link_ticket_to_email_5xx_test(self):
        email_id = 1234
        ticket_id = 5678

        logger = Mock()

        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value={})
        response_mock.status = 500

        bruin_client = BruinClient(logger, config)
        bruin_client._bearer_token = "Someverysecretaccesstoken"
        bruin_client.login = CoroutineMock()

        with patch.object(bruin_client._session, 'post', new=CoroutineMock(return_value=response_mock)):
            response = await bruin_client.link_ticket_to_email(ticket_id, email_id)

        logger.error.assert_called_once_with("Got HTTP 500 from Bruin")
        assert response['status'] == 500
        assert response['body'] == "Got internal error from Bruin"
