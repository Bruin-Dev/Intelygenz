from unittest.mock import patch

import pytest
from application import nats_error_response
from application.repositories import bruin_repository as bruin_repository_module
from asynctest import CoroutineMock
from config import testconfig
from shortuuid import uuid

uuid_ = uuid()
uuid_mock = patch.object(bruin_repository_module, "uuid", return_value=uuid_)


class TestBruinRepository:
    def instance_test(self, bruin_repository, event_bus, logger, notifications_repository):
        assert bruin_repository._event_bus is event_bus
        assert bruin_repository._logger is logger
        assert bruin_repository._config is testconfig
        assert bruin_repository._notifications_repository is notifications_repository

    @pytest.mark.asyncio
    async def get_tickets_with_no_service_number_specified_test(
        self, bruin_repository, get_open_affecting_ticket_200_response
    ):
        bruin_client_id = 12345
        ticket_statuses = ["New", "InProgress", "Draft"]
        ticket_topic = "VAS"
        product_category = bruin_repository._config.MONITOR_CONFIG["product_category"]

        request = {
            "request_id": uuid_,
            "body": {
                "client_id": bruin_client_id,
                "ticket_statuses": ticket_statuses,
                "product_category": product_category,
                "ticket_topic": ticket_topic,
            },
        }

        bruin_repository._event_bus.rpc_request.return_value = get_open_affecting_ticket_200_response

        with uuid_mock:
            result = await bruin_repository.get_tickets(bruin_client_id, ticket_topic, ticket_statuses)

        bruin_repository._event_bus.rpc_request.assert_awaited_once_with(
            "bruin.ticket.basic.request", request, timeout=90
        )
        assert result == get_open_affecting_ticket_200_response

    @pytest.mark.asyncio
    async def get_tickets_with_service_number_specified_test(
        self, bruin_repository, get_open_affecting_ticket_200_response
    ):
        bruin_client_id = 12345
        service_number = "B827EB92EB72"
        ticket_statuses = ["New", "InProgress", "Draft"]
        ticket_topic = "VAS"
        product_category = bruin_repository._config.MONITOR_CONFIG["product_category"]

        request = {
            "request_id": uuid_,
            "body": {
                "client_id": bruin_client_id,
                "ticket_statuses": ticket_statuses,
                "product_category": product_category,
                "ticket_topic": ticket_topic,
                "service_number": service_number,
            },
        }

        bruin_repository._event_bus.rpc_request.return_value = get_open_affecting_ticket_200_response

        with uuid_mock:
            result = await bruin_repository.get_tickets(
                bruin_client_id, ticket_topic, ticket_statuses, service_number=service_number
            )

        bruin_repository._event_bus.rpc_request.assert_awaited_once_with(
            "bruin.ticket.basic.request", request, timeout=90
        )
        assert result == get_open_affecting_ticket_200_response

    @pytest.mark.asyncio
    async def get_tickets_with_rpc_request_failing_test(self, bruin_repository):
        bruin_client_id = 12345
        ticket_statuses = ["New", "InProgress", "Draft"]
        ticket_topic = "VAS"
        product_category = bruin_repository._config.MONITOR_CONFIG["product_category"]

        request = {
            "request_id": uuid_,
            "body": {
                "client_id": bruin_client_id,
                "ticket_statuses": ticket_statuses,
                "product_category": product_category,
                "ticket_topic": ticket_topic,
            },
        }

        bruin_repository._event_bus.rpc_request.side_effect = Exception
        bruin_repository._notifications_repository.send_slack_message = CoroutineMock()

        with uuid_mock:
            result = await bruin_repository.get_tickets(bruin_client_id, ticket_topic, ticket_statuses)

        bruin_repository._event_bus.rpc_request.assert_awaited_once_with(
            "bruin.ticket.basic.request", request, timeout=90
        )
        bruin_repository._notifications_repository.send_slack_message.assert_awaited_once()
        bruin_repository._logger.error.assert_called()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_tickets_with_rpc_request_returning_non_2xx_status_test(self, bruin_repository, bruin_500_response):
        bruin_client_id = 12345
        ticket_statuses = ["New", "InProgress", "Draft"]
        ticket_topic = "VAS"
        product_category = bruin_repository._config.MONITOR_CONFIG["product_category"]

        request = {
            "request_id": uuid_,
            "body": {
                "client_id": bruin_client_id,
                "ticket_statuses": ticket_statuses,
                "product_category": product_category,
                "ticket_topic": ticket_topic,
            },
        }

        bruin_repository._event_bus.rpc_request = CoroutineMock(return_value=bruin_500_response)
        bruin_repository._notifications_repository.send_slack_message = CoroutineMock()

        with uuid_mock:
            result = await bruin_repository.get_tickets(bruin_client_id, ticket_topic, ticket_statuses)

        bruin_repository._event_bus.rpc_request.assert_awaited_once_with(
            "bruin.ticket.basic.request", request, timeout=90
        )
        bruin_repository._notifications_repository.send_slack_message.assert_awaited_once()
        bruin_repository._logger.error.assert_called()
        assert result == bruin_500_response

    @pytest.mark.asyncio
    async def get_affecting_tickets_with_service_number_specified_test(
        self, bruin_repository, get_open_affecting_ticket_200_response
    ):
        bruin_client_id = 12345
        service_number = "B827EB92EB72"
        ticket_statuses = ["New", "InProgress", "Draft"]
        ticket_topic = "VAS"
        product_category = bruin_repository._config.MONITOR_CONFIG["product_category"]

        bruin_repository.get_tickets.return_value = get_open_affecting_ticket_200_response

        with uuid_mock:
            result = await bruin_repository.get_affecting_tickets(
                bruin_client_id, ticket_statuses, service_number=service_number
            )

        bruin_repository.get_tickets.assert_awaited_once_with(
            bruin_client_id, ticket_topic, ticket_statuses, service_number=service_number
        )
        assert result == get_open_affecting_ticket_200_response

    @pytest.mark.asyncio
    async def get_affecting_tickets_with_no_service_number_specified_test(
        self, bruin_repository, get_open_affecting_ticket_200_response
    ):
        bruin_client_id = 12345
        ticket_statuses = ["New", "InProgress", "Draft"]
        ticket_topic = "VAS"
        product_category = bruin_repository._config.MONITOR_CONFIG["product_category"]

        bruin_repository.get_tickets.return_value = get_open_affecting_ticket_200_response

        with uuid_mock:
            result = await bruin_repository.get_affecting_tickets(bruin_client_id, ticket_statuses)

        bruin_repository.get_tickets.assert_awaited_once_with(
            bruin_client_id, ticket_topic, ticket_statuses, service_number=None
        )
        assert result == get_open_affecting_ticket_200_response

    @pytest.mark.asyncio
    async def get_open_affecting_tickets_with_service_number_specified_test(
        self, bruin_repository, get_open_affecting_ticket_200_response
    ):
        bruin_client_id = 12345
        service_number = "B827EB92EB72"
        ticket_statuses = ["New", "InProgress", "Draft", "Resolved"]

        bruin_repository.get_affecting_tickets.return_value = get_open_affecting_ticket_200_response

        with uuid_mock:
            result = await bruin_repository.get_open_affecting_tickets(bruin_client_id, service_number=service_number)

        bruin_repository.get_affecting_tickets.assert_awaited_once_with(
            bruin_client_id, ticket_statuses, service_number=service_number
        )
        assert result == get_open_affecting_ticket_200_response

    @pytest.mark.asyncio
    async def get_open_affecting_tickets_with_no_service_number_specified_test(
        self, bruin_repository, get_open_affecting_ticket_200_response
    ):
        bruin_client_id = 12345
        ticket_statuses = ["New", "InProgress", "Draft", "Resolved"]

        bruin_repository.get_affecting_tickets.return_value = get_open_affecting_ticket_200_response

        with uuid_mock:
            result = await bruin_repository.get_open_affecting_tickets(bruin_client_id)

        bruin_repository.get_affecting_tickets.assert_awaited_once_with(
            bruin_client_id, ticket_statuses, service_number=None
        )
        assert result == get_open_affecting_ticket_200_response

    @pytest.mark.asyncio
    async def get_ticket_details_test(self, bruin_repository, get_ticket_details_200_response):
        ticket_id = 11111

        request = {
            "request_id": uuid_,
            "body": {
                "ticket_id": ticket_id,
            },
        }

        bruin_repository._event_bus.rpc_request.return_value = get_ticket_details_200_response

        with uuid_mock:
            result = await bruin_repository.get_ticket_details(ticket_id)

        bruin_repository._event_bus.rpc_request.assert_awaited_once_with(
            "bruin.ticket.details.request", request, timeout=15
        )
        assert result == get_ticket_details_200_response

    @pytest.mark.asyncio
    async def get_ticket_details_with_rpc_request_failing_test(self, bruin_repository):
        ticket_id = 11111

        request = {
            "request_id": uuid_,
            "body": {
                "ticket_id": ticket_id,
            },
        }

        bruin_repository._event_bus.rpc_request.side_effect = Exception
        bruin_repository._notifications_repository.send_slack_message = CoroutineMock()

        with uuid_mock:
            result = await bruin_repository.get_ticket_details(ticket_id)

        bruin_repository._event_bus.rpc_request.assert_awaited_once_with(
            "bruin.ticket.details.request", request, timeout=15
        )
        bruin_repository._notifications_repository.send_slack_message.assert_awaited_once()
        bruin_repository._logger.error.assert_called()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_ticket_details_with_rpc_request_returning_non_2xx_status_test(
        self, bruin_repository, bruin_500_response
    ):
        ticket_id = 11111

        request = {
            "request_id": uuid_,
            "body": {
                "ticket_id": ticket_id,
            },
        }

        bruin_repository._event_bus.rpc_request.return_value = bruin_500_response
        bruin_repository._notifications_repository.send_slack_message = CoroutineMock()

        with uuid_mock:
            result = await bruin_repository.get_ticket_details(ticket_id)

        bruin_repository._event_bus.rpc_request.assert_awaited_once_with(
            "bruin.ticket.details.request", request, timeout=15
        )
        bruin_repository._notifications_repository.send_slack_message.assert_awaited_once()
        bruin_repository._logger.error.assert_called()
        assert result == bruin_500_response

    @pytest.mark.asyncio
    async def create_affecting_ticket_test(self, bruin_repository, create_affecting_ticket_200_response):
        client_id = 12345
        service_number = "B827EB76A8DE"

        request = {
            "request_id": uuid_,
            "body": {
                "clientId": client_id,
                "services": [
                    {
                        "serviceNumber": service_number,
                    },
                ],
                "category": "VAS",
                "contacts": [
                    {
                        "email": "ndimuro@mettel.net",
                        "phone": "9876543210",
                        "name": "Nicholas DiMuro",
                        "type": "site",
                    },
                    {
                        "email": "ndimuro@mettel.net",
                        "phone": "9876543210",
                        "name": "Nicholas DiMuro",
                        "type": "ticket",
                    },
                ],
            },
        }

        bruin_repository._event_bus.rpc_request.return_value = create_affecting_ticket_200_response

        with uuid_mock:
            result = await bruin_repository.create_affecting_ticket(client_id, service_number)

        bruin_repository._event_bus.rpc_request.assert_awaited_once_with(
            "bruin.ticket.creation.request", request, timeout=30
        )
        assert result == create_affecting_ticket_200_response

    @pytest.mark.asyncio
    async def create_affecting_ticket_with_rpc_request_failing_test(self, bruin_repository):
        client_id = 12345
        service_number = "B827EB76A8DE"

        request = {
            "request_id": uuid_,
            "body": {
                "clientId": client_id,
                "services": [
                    {
                        "serviceNumber": service_number,
                    },
                ],
                "category": "VAS",
                "contacts": [
                    {
                        "email": "ndimuro@mettel.net",
                        "phone": "9876543210",
                        "name": "Nicholas DiMuro",
                        "type": "site",
                    },
                    {
                        "email": "ndimuro@mettel.net",
                        "phone": "9876543210",
                        "name": "Nicholas DiMuro",
                        "type": "ticket",
                    },
                ],
            },
        }

        bruin_repository._event_bus.rpc_request.side_effect = Exception
        bruin_repository._notifications_repository.send_slack_message = CoroutineMock()

        with uuid_mock:
            result = await bruin_repository.create_affecting_ticket(client_id, service_number)

        bruin_repository._event_bus.rpc_request.assert_awaited_once_with(
            "bruin.ticket.creation.request", request, timeout=30
        )
        bruin_repository._notifications_repository.send_slack_message.assert_awaited_once()
        bruin_repository._logger.error.assert_called()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def create_affecting_ticket_with_rpc_request_returning_non_2xx_status_test(
        self, bruin_repository, bruin_500_response
    ):
        client_id = 12345
        service_number = "B827EB76A8DE"

        request = {
            "request_id": uuid_,
            "body": {
                "clientId": client_id,
                "services": [
                    {
                        "serviceNumber": service_number,
                    },
                ],
                "category": "VAS",
                "contacts": [
                    {
                        "email": "ndimuro@mettel.net",
                        "phone": "9876543210",
                        "name": "Nicholas DiMuro",
                        "type": "site",
                    },
                    {
                        "email": "ndimuro@mettel.net",
                        "phone": "9876543210",
                        "name": "Nicholas DiMuro",
                        "type": "ticket",
                    },
                ],
            },
        }

        bruin_repository._event_bus.rpc_request.return_value = bruin_500_response
        bruin_repository._notifications_repository.send_slack_message = CoroutineMock()

        with uuid_mock:
            result = await bruin_repository.create_affecting_ticket(client_id, service_number)

        bruin_repository._event_bus.rpc_request.assert_awaited_once_with(
            "bruin.ticket.creation.request", request, timeout=30
        )
        bruin_repository._notifications_repository.send_slack_message.assert_awaited_once()
        bruin_repository._logger.error.assert_called()
        assert result == bruin_500_response

    @pytest.mark.asyncio
    async def append_multiple_notes_to_ticket_test(self, bruin_repository, append_multiple_notes_200_response):
        ticket_id = 12345
        note_1 = {
            "text": "This is ticket note 1",
            "service_number": "B827EB76A8DE",
        }
        note_2 = {
            "text": "This is ticket note 2",
            "service_number": "B827EB76A8DE",
        }
        note_3 = {
            "text": "This is ticket note 3",
            "service_number": "B827EB76A8DE",
        }
        notes = [
            note_1,
            note_2,
            note_3,
        ]

        request = {
            "request_id": uuid_,
            "body": {
                "ticket_id": ticket_id,
                "notes": notes,
            },
        }

        bruin_repository._event_bus.rpc_request.return_value = append_multiple_notes_200_response

        with uuid_mock:
            result = await bruin_repository.append_multiple_notes_to_ticket(ticket_id, notes)

        bruin_repository._event_bus.rpc_request.assert_awaited_once_with(
            "bruin.ticket.multiple.notes.append.request", request, timeout=45
        )
        assert result == append_multiple_notes_200_response

    @pytest.mark.asyncio
    async def append_multiple_notes_to_ticket_with_rpc_request_failing_test(self, bruin_repository):
        ticket_id = 12345
        note_1 = {
            "text": "This is ticket note 1",
            "service_number": "B827EB76A8DE",
        }
        note_2 = {
            "text": "This is ticket note 2",
            "service_number": "B827EB76A8DE",
        }
        note_3 = {
            "text": "This is ticket note 3",
            "service_number": "B827EB76A8DE",
        }
        notes = [
            note_1,
            note_2,
            note_3,
        ]

        request = {
            "request_id": uuid_,
            "body": {
                "ticket_id": ticket_id,
                "notes": notes,
            },
        }

        bruin_repository._event_bus.rpc_request.side_effect = Exception
        bruin_repository._notifications_repository.send_slack_message = CoroutineMock()

        with uuid_mock:
            result = await bruin_repository.append_multiple_notes_to_ticket(ticket_id, notes)

        bruin_repository._event_bus.rpc_request.assert_awaited_once_with(
            "bruin.ticket.multiple.notes.append.request", request, timeout=45
        )
        bruin_repository._notifications_repository.send_slack_message.assert_awaited_once()
        bruin_repository._logger.error.assert_called()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def append_multiple_notes_to_ticket_with_rpc_request_returning_non_2xx_status_test(
        self, bruin_repository, bruin_500_response
    ):
        ticket_id = 12345
        note_1 = {
            "text": "This is ticket note 1",
            "service_number": "B827EB76A8DE",
        }
        note_2 = {
            "text": "This is ticket note 2",
            "service_number": "B827EB76A8DE",
        }
        note_3 = {
            "text": "This is ticket note 3",
            "service_number": "B827EB76A8DE",
        }
        notes = [
            note_1,
            note_2,
            note_3,
        ]

        request = {
            "request_id": uuid_,
            "body": {
                "ticket_id": ticket_id,
                "notes": notes,
            },
        }

        bruin_repository._event_bus.rpc_request.return_value = bruin_500_response
        bruin_repository._notifications_repository.send_slack_message = CoroutineMock()

        with uuid_mock:
            result = await bruin_repository.append_multiple_notes_to_ticket(ticket_id, notes)

        bruin_repository._event_bus.rpc_request.assert_awaited_once_with(
            "bruin.ticket.multiple.notes.append.request", request, timeout=45
        )
        bruin_repository._notifications_repository.send_slack_message.assert_awaited_once()
        bruin_repository._logger.error.assert_called()
        assert result == bruin_500_response

    @pytest.mark.asyncio
    async def unresolve_ticket_detail_test(self, bruin_repository, unresolve_ticket_detail_200_response):
        ticket_id = 12345
        detail_id = 67890

        request = {
            "request_id": uuid_,
            "body": {
                "ticket_id": ticket_id,
                "detail_id": detail_id,
            },
        }

        bruin_repository._event_bus.rpc_request.return_value = unresolve_ticket_detail_200_response

        with uuid_mock:
            result = await bruin_repository.unresolve_ticket_detail(ticket_id, detail_id)

        bruin_repository._event_bus.rpc_request.assert_awaited_once_with(
            "bruin.ticket.status.open", request, timeout=15
        )
        assert result == unresolve_ticket_detail_200_response

    @pytest.mark.asyncio
    async def unresolve_ticket_detail_with_rpc_request_failing_test(self, bruin_repository):
        ticket_id = 12345
        detail_id = 67890

        request = {
            "request_id": uuid_,
            "body": {
                "ticket_id": ticket_id,
                "detail_id": detail_id,
            },
        }

        bruin_repository._event_bus.rpc_request.side_effect = Exception
        bruin_repository._notifications_repository.send_slack_message = CoroutineMock()

        with uuid_mock:
            result = await bruin_repository.unresolve_ticket_detail(ticket_id, detail_id)

        bruin_repository._event_bus.rpc_request.assert_awaited_once_with(
            "bruin.ticket.status.open", request, timeout=15
        )
        bruin_repository._notifications_repository.send_slack_message.assert_awaited_once()
        bruin_repository._logger.error.assert_called()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def unresolve_ticket_detail_with_rpc_request_returning_non_2xx_status_test(
        self, bruin_repository, bruin_500_response
    ):
        ticket_id = 12345
        detail_id = 67890

        request = {
            "request_id": uuid_,
            "body": {
                "ticket_id": ticket_id,
                "detail_id": detail_id,
            },
        }

        bruin_repository._event_bus.rpc_request.return_value = bruin_500_response
        bruin_repository._notifications_repository.send_slack_message = CoroutineMock()

        with uuid_mock:
            result = await bruin_repository.unresolve_ticket_detail(ticket_id, detail_id)

        bruin_repository._event_bus.rpc_request.assert_awaited_once_with(
            "bruin.ticket.status.open", request, timeout=15
        )
        bruin_repository._notifications_repository.send_slack_message.assert_awaited_once()
        bruin_repository._logger.error.assert_called()
        assert result == bruin_500_response
