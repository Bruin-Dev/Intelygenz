from unittest.mock import AsyncMock, Mock, patch

import pytest
from application.repositories import bruin_repository as bruin_repository_module
from application.repositories import nats_error_response
from application.repositories.bruin_repository import BruinRepository
from application.repositories.utils_repository import to_json_bytes
from config import testconfig
from nats.aio.msg import Msg
from shortuuid import uuid

uuid_ = uuid()
uuid_mock = patch.object(bruin_repository_module, "uuid", return_value=uuid_)


class TestBruinRepository:
    def instance_test(self):
        nats_client = Mock()
        config = testconfig
        notifications_repository = Mock()

        bruin_repository = BruinRepository(config, nats_client, notifications_repository)

        assert bruin_repository._nats_client is nats_client
        assert bruin_repository._config is config
        assert bruin_repository._notifications_repository is notifications_repository

    @pytest.mark.asyncio
    async def get_client_info_test(
        self, instance_bruin_repository, instance_request_message_without_topic, instance_response_message
    ):
        service_number = "VC1234567"
        instance_request_message_without_topic["request_id"] = uuid_
        instance_request_message_without_topic["body"] = {"service_number": service_number}
        instance_response_message["request_id"] = uuid_
        instance_response_message["body"] = {"client_id": 9994, "client_name": "METTEL/NEW YORK", "side_id": 1234}
        instance_response_message["status"] = 200

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(instance_response_message)

        instance_bruin_repository._nats_client.request = AsyncMock(return_value=response_msg)

        with uuid_mock:
            result = await instance_bruin_repository.get_client_info(service_number)

        instance_bruin_repository._nats_client.request.assert_awaited_once_with(
            "bruin.customer.get.info", to_json_bytes(instance_request_message_without_topic), timeout=90
        )
        assert result == instance_response_message

    @pytest.mark.asyncio
    async def get_client_info_with_request_failing_test(
        self, instance_bruin_repository, instance_request_message_without_topic
    ):
        service_number = "VC1234567"

        instance_request_message_without_topic["request_id"] = uuid_
        instance_request_message_without_topic["body"] = {"service_number": service_number}

        instance_bruin_repository._nats_client.request = AsyncMock(side_effect=Exception)

        instance_bruin_repository._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await instance_bruin_repository.get_client_info(service_number)

        instance_bruin_repository._notifications_repository.send_slack_message.assert_awaited_once()
        instance_bruin_repository._nats_client.request.assert_awaited_once_with(
            "bruin.customer.get.info", to_json_bytes(instance_request_message_without_topic), timeout=90
        )
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_client_info_with_request_returning_non_2xx_status_test(
        self, instance_bruin_repository, instance_request_message_without_topic, instance_response_message
    ):
        service_number = "VC1234567"
        instance_request_message_without_topic["request_id"] = uuid_
        instance_request_message_without_topic["body"] = {"service_number": service_number}
        instance_response_message["request_id"] = uuid_
        instance_response_message["body"] = "Got internal error from Bruin"
        instance_response_message["status"] = 500

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(instance_response_message)

        instance_bruin_repository._nats_client.request = AsyncMock(return_value=response_msg)

        instance_bruin_repository._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await instance_bruin_repository.get_client_info(service_number)

        instance_bruin_repository._nats_client.request.assert_awaited_once_with(
            "bruin.customer.get.info", to_json_bytes(instance_request_message_without_topic), timeout=90
        )
        instance_bruin_repository._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == instance_response_message

    @pytest.mark.asyncio
    async def get_management_status_test(
        self, instance_bruin_repository, instance_request_message_without_topic, instance_response_message
    ):
        service_number = "VC1234567"
        client_id = 9994
        instance_request_message_without_topic["request_id"] = uuid_
        instance_request_message_without_topic["body"] = {
            "client_id": client_id,
            "service_number": service_number,
            "status": "A",
        }
        instance_response_message["request_id"] = uuid_
        instance_response_message["body"] = "Active – Gold Monitoring"
        instance_response_message["status"] = 200

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(instance_response_message)

        instance_bruin_repository._nats_client.request = AsyncMock(return_value=response_msg)

        with uuid_mock:
            result = await instance_bruin_repository.get_management_status(client_id, service_number)

        instance_bruin_repository._nats_client.request.assert_awaited_once_with(
            "bruin.inventory.management.status", to_json_bytes(instance_request_message_without_topic), timeout=90
        )
        assert result == instance_response_message

    @pytest.mark.asyncio
    async def get_management_status_with_request_failing_test(
        self, instance_bruin_repository, instance_request_message_without_topic
    ):
        service_number = "VC1234567"
        client_id = 9994
        instance_request_message_without_topic["request_id"] = uuid_
        instance_request_message_without_topic["body"] = {
            "client_id": client_id,
            "service_number": service_number,
            "status": "A",
        }

        instance_bruin_repository._nats_client.request = AsyncMock(side_effect=Exception)

        instance_bruin_repository._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await instance_bruin_repository.get_management_status(client_id, service_number)

        instance_bruin_repository._nats_client.request.assert_awaited_once_with(
            "bruin.inventory.management.status", to_json_bytes(instance_request_message_without_topic), timeout=90
        )
        instance_bruin_repository._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def management_status_with_request_returning_non_2xx_status_test(
        self, instance_bruin_repository, instance_request_message_without_topic, instance_response_message
    ):
        service_number = "VC1234567"
        client_id = 9994
        instance_request_message_without_topic["request_id"] = uuid_
        instance_request_message_without_topic["body"] = {
            "client_id": client_id,
            "service_number": service_number,
            "status": "A",
        }
        instance_response_message["request_id"] = uuid_
        instance_response_message["body"] = "Got internal error from Bruin"
        instance_response_message["status"] = 500

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(instance_response_message)

        instance_bruin_repository._nats_client.request = AsyncMock(return_value=response_msg)
        instance_bruin_repository._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await instance_bruin_repository.get_management_status(client_id, service_number)

        instance_bruin_repository._nats_client.request.assert_awaited_once_with(
            "bruin.inventory.management.status", to_json_bytes(instance_request_message_without_topic), timeout=90
        )
        instance_bruin_repository._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == instance_response_message

    @pytest.mark.asyncio
    async def get_site_details_test(
        self, instance_bruin_repository, instance_request_message_without_topic, instance_response_message
    ):
        client_id = 9994
        site_id = 12345

        instance_request_message_without_topic["request_id"] = uuid_
        instance_request_message_without_topic["body"] = {
            "client_id": client_id,
            "site_id": site_id,
        }
        instance_response_message["request_id"] = uuid_
        instance_response_message["body"] = {
            "clientID": client_id,
            "clientName": "Sarif Industries",
            "siteID": f"{site_id}",
            "siteLabel": "some-label",
            "siteAddDate": "2021-11-24T16:30:05.110Z",
            "address": {
                "addressID": 1,
                "address": "Fake Street 123",
                "city": "Springfield",
                "state": "Nowhere",
                "zip": "12345",
                "country": "Somewhere",
            },
            "longitude": 0,
            "latitude": 0,
            "businessHours": "",
            "timeZone": "",
            "primaryContactName": "Test",
            "primaryContactPhone": "123-456-7890",
            "primaryContactEmail": "test@mail.com",
        }
        instance_response_message["status"] = 200

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(instance_response_message)

        instance_bruin_repository._nats_client.request = AsyncMock(return_value=response_msg)

        with uuid_mock:
            result = await instance_bruin_repository.get_site_details(client_id, site_id)

        instance_bruin_repository._nats_client.request.assert_awaited_once_with(
            "bruin.get.site", to_json_bytes(instance_request_message_without_topic), timeout=120
        )
        assert result == instance_response_message

    @pytest.mark.asyncio
    async def get_site_details_with_request_failing_test(
        self, instance_bruin_repository, instance_request_message_without_topic
    ):
        client_id = 9994
        site_id = 12345

        instance_request_message_without_topic["request_id"] = uuid_
        instance_request_message_without_topic["body"] = {
            "client_id": client_id,
            "site_id": site_id,
        }

        instance_bruin_repository._nats_client.request = AsyncMock(side_effect=Exception)

        instance_bruin_repository._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await instance_bruin_repository.get_site_details(client_id, site_id)

        instance_bruin_repository._nats_client.request.assert_awaited_once_with(
            "bruin.get.site", to_json_bytes(instance_request_message_without_topic), timeout=120
        )
        instance_bruin_repository._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_site_details_with_request_returning_non_2xx_status_test(
        self, instance_bruin_repository, instance_request_message_without_topic, instance_response_message
    ):
        client_id = 9994
        site_id = 12345

        instance_request_message_without_topic["request_id"] = uuid_
        instance_request_message_without_topic["body"] = {
            "client_id": client_id,
            "site_id": site_id,
        }

        instance_response_message["request_id"] = uuid_
        instance_response_message["body"] = "Got internal error from Bruin"
        instance_response_message["status"] = 500

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(instance_response_message)

        instance_bruin_repository._nats_client.request = AsyncMock(return_value=response_msg)
        instance_bruin_repository._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await instance_bruin_repository.get_site_details(client_id, site_id)

        instance_bruin_repository._nats_client.request.assert_awaited_once_with(
            "bruin.get.site", to_json_bytes(instance_request_message_without_topic), timeout=120
        )
        instance_bruin_repository._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == instance_response_message

    @pytest.mark.asyncio
    async def get_ticket_contact_test(
        self, instance_bruin_repository, instance_request_message_without_topic, instance_response_message
    ):
        client_id = 9994

        instance_request_message_without_topic["request_id"] = uuid_
        instance_request_message_without_topic["body"] = {
            "client_id": client_id
        }
        instance_response_message["request_id"] = uuid_
        instance_response_message["body"] = [
            {
                "FirstName": "Test",
                "LastName": "User",
                "Email": "test@test.com",
                "Phone": "123-456-7890"
            },
            {
                "FirstName": "Test2",
                "LastName": "User2",
                "Email": "test2@test.com",
                "Phone": "123-456-7890",
            }
        ]
        instance_response_message["status"] = 200

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(instance_response_message)

        instance_bruin_repository._nats_client.request = AsyncMock(return_value=response_msg)

        with uuid_mock:
            result = await instance_bruin_repository.get_ticket_contact(client_id)

        instance_bruin_repository._nats_client.request.assert_awaited_once_with(
            "bruin.get.ticket.contacts", to_json_bytes(instance_request_message_without_topic), timeout=120
        )
        assert result == instance_response_message

    @pytest.mark.asyncio
    async def get_ticket_contact_with_request_failing_test(
        self, instance_bruin_repository, instance_request_message_without_topic
    ):
        client_id = 9994

        instance_request_message_without_topic["request_id"] = uuid_
        instance_request_message_without_topic["body"] = {
            "client_id": client_id
        }

        instance_bruin_repository._nats_client.request = AsyncMock(side_effect=Exception)

        instance_bruin_repository._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await instance_bruin_repository.get_ticket_contact(client_id)

        instance_bruin_repository._nats_client.request.assert_awaited_once_with(
            "bruin.get.ticket.contacts", to_json_bytes(instance_request_message_without_topic), timeout=120
        )
        instance_bruin_repository._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_ticket_contact_with_request_returning_non_2xx_status_test(
        self, instance_bruin_repository, instance_request_message_without_topic, instance_response_message
    ):
        client_id = 9994

        instance_request_message_without_topic["request_id"] = uuid_
        instance_request_message_without_topic["body"] = {
            "client_id": client_id
        }

        instance_response_message["request_id"] = uuid_
        instance_response_message["body"] = "Got internal error from Bruin"
        instance_response_message["status"] = 500

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(instance_response_message)

        instance_bruin_repository._nats_client.request = AsyncMock(return_value=response_msg)
        instance_bruin_repository._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await instance_bruin_repository.get_ticket_contact(client_id)

        instance_bruin_repository._nats_client.request.assert_awaited_once_with(
            "bruin.get.ticket.contacts", to_json_bytes(instance_request_message_without_topic), timeout=120
        )
        instance_bruin_repository._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == instance_response_message

    def is_management_status_active_test(self, instance_bruin_repository):
        management_status = "Pending"
        result = instance_bruin_repository.is_management_status_active(management_status)
        assert result is True

        management_status = "Active – Gold Monitoring"
        result = instance_bruin_repository.is_management_status_active(management_status)
        assert result is True

        management_status = "Active – Platinum Monitoring"
        result = instance_bruin_repository.is_management_status_active(management_status)
        assert result is True

        management_status = "Fake status"
        result = instance_bruin_repository.is_management_status_active(management_status)
        assert result is False
