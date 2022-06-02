import hashlib
import hmac
from http import HTTPStatus
from unittest.mock import Mock, patch

import application
import application.server.api_server as api_server_module
import pytest
from application.repositories.utils_repository import UtilsRepository
from application.server.api_server import APIServer
from asynctest import CoroutineMock
from config import testconfig
from hypercorn.config import Config as HyperCornConfig
from quart import Quart


class TestApiServer:
    def instance_test(self):
        logger = Mock()
        new_emails_repository = Mock()
        new_tickets_repository = Mock()

        notifications_repository = Mock()
        utils_repository = Mock()

        api_server_test = APIServer(
            logger,
            testconfig,
            new_emails_repository,
            new_tickets_repository,
            notifications_repository,
            utils_repository,
        )

        assert api_server_test._logger is logger
        assert api_server_test._new_emails_repository is new_emails_repository
        assert api_server_test._notifications_repository is notifications_repository

        assert api_server_test._title == testconfig.QUART_CONFIG["title"]
        assert api_server_test._port == testconfig.QUART_CONFIG["port"]
        assert isinstance(api_server_test._hypercorn_config, HyperCornConfig) is True
        assert api_server_test._new_bind == f"0.0.0.0:{api_server_test._port}"
        assert isinstance(api_server_test._app, Quart) is True
        assert api_server_test._app.title == api_server_test._title

    @pytest.mark.asyncio
    async def run_server_test(self, api_server_test):
        with patch.object(application.server.api_server, "serve", new=CoroutineMock()) as mock_serve:
            await api_server_test.run_server()
            assert api_server_test._hypercorn_config.bind == [api_server_test._new_bind]
            assert mock_serve.called

    def attach_swagger_test(self, api_server_test):
        with patch.object(api_server_module, "quart_api_doc", new=CoroutineMock()) as quart_api_doc_mock:
            api_server_test.attach_swagger()
            quart_api_doc_mock.assert_called_once()

    @pytest.mark.asyncio
    async def ok_app_test(self, api_server_test):
        client = api_server_test._app.test_client()
        response = await client.get("/_health")
        data = await response.get_json()
        assert response.status_code == 200
        assert data is None

    @pytest.mark.asyncio
    async def post_new_email_ok_test(self, api_server_test):
        headers = {"api-key": "123456", "x-bruin-webhook-signature": "test-signature"}
        payload = {
            "Notification": {
                "Body": {
                    "Body": "the issue here",
                    "DATE": "2021-01-01T08:00:00.001Z",
                    "EmailId": "123456",
                    "ClientId": "5555",
                    "ParentID": "67890",
                    "Subject": "the title",
                    "TagID": ["1003"],
                }
            }
        }

        email_data = {
            "email": {
                "body": "the issue here",
                "date": "2021-01-01T08:00:00.001Z",
                "email_id": "123456",
                "client_id": "5555",
                "parent_id": "67890",
                "subject": "the title",
            },
            "tag_ids": ["1003"],
        }

        api_server_test._new_emails_repository.save_new_email = Mock()
        api_server_test._utils = UtilsRepository()
        api_server_test._is_valid_signature = Mock(return_value=True)

        client = api_server_test._app.test_client()
        response = await client.post(f"/email", json=payload, headers=headers)

        api_server_test._new_emails_repository.save_new_email.assert_called_once_with(email_data)
        api_server_test._logger.info.assert_called()

        assert response.status_code == HTTPStatus.NO_CONTENT

    @pytest.mark.asyncio
    async def post_new_ticket_ok_test(self, api_server_test):
        headers = {"api-key": "123456", "x-bruin-webhook-signature": "test-signature"}
        payload = {
            "Notification": {
                "Body": {
                    "EmailID": "2726244",
                    "Date": "2016-08-29T09:12:33.001Z",
                    "Subject": "Email Subject",
                    "Body": "EMAIL BODY",
                    "ParentID": "2726243",
                    "TagID": [3, 2, 1],
                    "Ticket": {
                        "TicketID": "123456",
                    },
                }
            }
        }

        email_data = {
            "email": {
                "email_id": "2726244",
                "date": "2016-08-29T09:12:33.001Z",
                "subject": "Email Subject",
                "body": "EMAIL BODY",
                "parent_id": "2726243",
            },
            "tag_ids": [3, 2, 1],
        }

        ticket_data = {
            "ticket_id": "123456",
        }

        api_server_test._new_tickets_repository.save_new_ticket = Mock()
        api_server_test._utils = UtilsRepository()
        api_server_test._is_valid_signature = Mock(return_value=True)

        client = api_server_test._app.test_client()
        response = await client.post(f"/ticket", json=payload, headers=headers)

        api_server_test._new_tickets_repository.save_new_ticket.assert_called_once_with(email_data, ticket_data)
        api_server_test._logger.info.assert_called()

        assert response.status_code == HTTPStatus.NO_CONTENT

    def _is_valid_signature_ok_test(self, api_server_test):
        content = b'{"Something": "test"}'
        secret = bytes(api_server_test._config.MONITOR_CONFIG["api_server"]["request_signature_secret_key"], "utf-8")
        signature = hmac.new(secret, content, hashlib.sha256).hexdigest()

        response = api_server_test._is_valid_signature(content, signature)
        assert response
