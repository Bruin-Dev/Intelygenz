import asyncio
import json
from typing import Any
from unittest.mock import AsyncMock, Mock, call, patch

import pytest
from nats.aio.msg import Msg
from shortuuid import uuid

from application.repositories import bruin_repository as bruin_repository_module
from application.repositories import nats_error_response
from application.repositories import notifications_repository as notifications_repository_module
from config import testconfig
from tests.fixtures._constants import CURRENT_DATETIME

uuid_ = uuid()
uuid_mock = patch.object(bruin_repository_module, "uuid", return_value=uuid_)
uuid_2_mock = patch.object(notifications_repository_module, "uuid", return_value=uuid_)


def to_json_bytes(message: dict[str, Any]):
    return json.dumps(message, default=str, separators=(",", ":")).encode()


def get_data_from_response_message(message):
    return json.loads(message.data)


class TestBruinRepository:
    def instance_test(self, bruin_repository, nats_client, notifications_repository):
        assert bruin_repository._nats_client is nats_client
        assert bruin_repository._config is testconfig
        assert bruin_repository._notifications_repository is notifications_repository

    @pytest.mark.asyncio
    async def get_tickets__no_service_number_specified_test(
        self, bruin_repository, make_ticket, make_list_of_tickets, make_get_tickets_request, make_rpc_response
    ):
        bruin_client_id = 12345
        ticket_statuses = ["New", "InProgress", "Draft"]
        ticket_topic = "VAS"
        product_category = bruin_repository._config.PRODUCT_CATEGORY

        ticket_1 = make_ticket(ticket_id=1, client_id=bruin_client_id)
        ticket_2 = make_ticket(ticket_id=2, client_id=bruin_client_id)
        tickets = make_list_of_tickets(ticket_1, ticket_2)

        request = make_get_tickets_request(
            request_id=uuid_,
            bruin_client_id=bruin_client_id,
            ticket_statuses=ticket_statuses,
            ticket_topic=ticket_topic,
            product_category=product_category,
        )
        response = make_rpc_response(
            request_id=uuid_,
            body=tickets,
            status=200,
        )
        NATS_AIO_MSG = Msg(_client="NATS", data=to_json_bytes(response))
        bruin_repository._nats_client.request = AsyncMock(return_value=NATS_AIO_MSG)

        with uuid_mock:
            result = await bruin_repository.get_tickets(bruin_client_id, ticket_topic, ticket_statuses)

        bruin_repository._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.basic.request", to_json_bytes(request), timeout=90
        )
        assert result == response

    @pytest.mark.asyncio
    async def get_tickets__service_number_specified_test(
        self, bruin_repository, make_ticket, make_list_of_tickets, make_get_tickets_request, make_rpc_response
    ):
        bruin_client_id = 12345
        service_number = "VC1234567"
        ticket_statuses = ["New", "InProgress", "Draft"]
        ticket_topic = "VAS"
        product_category = bruin_repository._config.PRODUCT_CATEGORY

        ticket_1 = make_ticket(ticket_id=1, client_id=bruin_client_id)
        ticket_2 = make_ticket(ticket_id=2, client_id=bruin_client_id)
        tickets = make_list_of_tickets(ticket_1, ticket_2)

        request = make_get_tickets_request(
            request_id=uuid_,
            bruin_client_id=bruin_client_id,
            ticket_statuses=ticket_statuses,
            product_category=product_category,
            ticket_topic=ticket_topic,
            service_number=service_number,
        )
        response = make_rpc_response(
            request_id=uuid_,
            body=tickets,
            status=200,
        )
        NATS_AIO_MSG = Msg(_client="NATS", data=to_json_bytes(response))
        bruin_repository._nats_client.request = AsyncMock(return_value=NATS_AIO_MSG)

        with uuid_mock:
            result = await bruin_repository.get_tickets(
                bruin_client_id, ticket_topic, ticket_statuses, service_number=service_number
            )

        bruin_repository._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.basic.request", to_json_bytes(request), timeout=90
        )
        assert result == response

    @pytest.mark.asyncio
    async def get_tickets__rpc_request_failing_test(self, bruin_repository, make_get_tickets_request):
        bruin_client_id = 12345
        ticket_statuses = ["New", "InProgress", "Draft"]
        ticket_topic = "VAS"
        product_category = bruin_repository._config.PRODUCT_CATEGORY

        request = make_get_tickets_request(
            request_id=uuid_,
            bruin_client_id=bruin_client_id,
            ticket_statuses=ticket_statuses,
            product_category=product_category,
            ticket_topic=ticket_topic,
        )

        bruin_repository._nats_client.request = AsyncMock(side_effect=Exception)
        bruin_repository._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await bruin_repository.get_tickets(bruin_client_id, ticket_topic, ticket_statuses)

        bruin_repository._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.basic.request", to_json_bytes(request), timeout=90
        )
        bruin_repository._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_tickets__rpc_request_has_not_2xx_status_test(
        self, bruin_repository, make_get_tickets_request, bruin_500_response
    ):
        bruin_client_id = 12345
        ticket_statuses = ["New", "InProgress", "Draft"]
        ticket_topic = "VAS"
        product_category = bruin_repository._config.PRODUCT_CATEGORY

        request = make_get_tickets_request(
            request_id=uuid_,
            bruin_client_id=bruin_client_id,
            ticket_statuses=ticket_statuses,
            product_category=product_category,
            ticket_topic=ticket_topic,
        )
        NATS_AIO_MSG = Msg(_client="NATS", data=to_json_bytes(bruin_500_response))
        bruin_repository._nats_client.request = AsyncMock(return_value=NATS_AIO_MSG)
        bruin_repository._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await bruin_repository.get_tickets(bruin_client_id, ticket_topic, ticket_statuses)

        bruin_repository._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.basic.request", to_json_bytes(request), timeout=90
        )
        bruin_repository._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == bruin_500_response

    @pytest.mark.asyncio
    async def get_ticket_details__details_retrieved_test(
        self,
        bruin_repository,
        make_get_ticket_details_request,
        make_detail_item,
        make_list_of_detail_items,
        make_ticket_note,
        make_list_of_ticket_notes,
        make_ticket_details,
        make_rpc_response,
    ):
        ticket_id = 11111

        detail_item_1 = make_detail_item(id_=1)
        detail_item_2 = make_detail_item(id_=2)
        detail_items = make_list_of_detail_items(detail_item_1, detail_item_2)
        ticket_note_1 = make_ticket_note(id_=1)
        ticket_note_2 = make_ticket_note(id_=2)
        ticket_notes = make_list_of_ticket_notes(ticket_note_1, ticket_note_2)
        ticket_details = make_ticket_details(detail_items=detail_items, notes=ticket_notes)

        request = make_get_ticket_details_request(
            request_id=uuid_,
            ticket_id=ticket_id,
        )
        response = make_rpc_response(
            request_id=uuid_,
            body=ticket_details,
            status=200,
        )
        NATS_AIO_MSG = Msg(_client="NATS", data=to_json_bytes(response))
        bruin_repository._nats_client.request = AsyncMock(return_value=NATS_AIO_MSG)

        with uuid_mock:
            result = await bruin_repository.get_ticket_details(ticket_id)

        bruin_repository._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.details.request", to_json_bytes(request), timeout=15
        )
        assert result == response

    @pytest.mark.asyncio
    async def get_ticket_details__rpc_request_failing_test(self, bruin_repository, make_get_ticket_details_request):
        ticket_id = 11111

        request = make_get_ticket_details_request(
            request_id=uuid_,
            ticket_id=ticket_id,
        )
        bruin_repository._nats_client.request = AsyncMock(side_effect=Exception)
        bruin_repository._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await bruin_repository.get_ticket_details(ticket_id)

        bruin_repository._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.details.request", to_json_bytes(request), timeout=15
        )
        bruin_repository._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_ticket_details__rpc_request_has_not_2xx_status_test(
        self, bruin_repository, make_get_ticket_details_request, bruin_500_response
    ):
        ticket_id = 11111

        request = make_get_ticket_details_request(
            request_id=uuid_,
            ticket_id=ticket_id,
        )
        NATS_AIO_MSG = Msg(_client="NATS", data=to_json_bytes(bruin_500_response))
        bruin_repository._nats_client.request = AsyncMock(return_value=NATS_AIO_MSG)
        bruin_repository._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await bruin_repository.get_ticket_details(ticket_id)

        bruin_repository._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.details.request", to_json_bytes(request), timeout=15
        )
        bruin_repository._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == bruin_500_response

    @pytest.mark.asyncio
    async def append_note_to_ticket__no_service_numbers_specified_test(
        self, bruin_repository, make_append_ticket_note_request, bruin_generic_200_response
    ):
        ticket_id = 11111
        ticket_note = "This is a ticket note"

        request = make_append_ticket_note_request(
            request_id=uuid_,
            ticket_id=ticket_id,
            note=ticket_note,
        )
        NATS_AIO_MSG = Msg(_client="NATS", data=to_json_bytes(bruin_generic_200_response))
        bruin_repository._nats_client.request = AsyncMock(return_value=NATS_AIO_MSG)

        with uuid_mock:
            result = await bruin_repository.append_note_to_ticket(ticket_id, ticket_note)

        bruin_repository._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.note.append.request", to_json_bytes(request), timeout=15
        )
        assert result == bruin_generic_200_response

    @pytest.mark.asyncio
    async def append_note_to_ticket__service_numbers_specified_test(
        self, bruin_repository, make_append_ticket_note_request, bruin_generic_200_response
    ):
        ticket_id = 11111
        ticket_note = "This is a ticket note"
        service_number = "VC1234567"
        service_numbers = [service_number]

        request = make_append_ticket_note_request(
            request_id=uuid_,
            ticket_id=ticket_id,
            note=ticket_note,
            service_numbers=service_numbers,
        )
        NATS_AIO_MSG = Msg(_client="NATS", data=to_json_bytes(bruin_generic_200_response))
        bruin_repository._nats_client.request = AsyncMock(return_value=NATS_AIO_MSG)

        with uuid_mock:
            result = await bruin_repository.append_note_to_ticket(
                ticket_id, ticket_note, service_numbers=service_numbers
            )

        bruin_repository._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.note.append.request", to_json_bytes(request), timeout=15
        )
        assert result == bruin_generic_200_response

    @pytest.mark.asyncio
    async def append_note_to_ticket__rpc_request_failing_test(self, bruin_repository, make_append_ticket_note_request):
        ticket_id = 11111
        ticket_note = "This is a ticket note"

        request = make_append_ticket_note_request(
            request_id=uuid_,
            ticket_id=ticket_id,
            note=ticket_note,
        )

        bruin_repository._nats_client.request = AsyncMock(side_effect=Exception)
        bruin_repository._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await bruin_repository.append_note_to_ticket(ticket_id, ticket_note)

        bruin_repository._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.note.append.request", to_json_bytes(request), timeout=15
        )
        bruin_repository._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def append_note_to_ticket__rpc_request_has_not_2xx_status_test(
        self, bruin_repository, make_append_ticket_note_request, bruin_500_response
    ):
        ticket_id = 11111
        ticket_note = "This is a ticket note"

        request = make_append_ticket_note_request(
            request_id=uuid_,
            ticket_id=ticket_id,
            note=ticket_note,
        )
        NATS_AIO_MSG = Msg(_client="NATS", data=to_json_bytes(bruin_500_response))
        bruin_repository._nats_client.request = AsyncMock(return_value=NATS_AIO_MSG)
        bruin_repository._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await bruin_repository.append_note_to_ticket(ticket_id, ticket_note)

        bruin_repository._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.note.append.request", to_json_bytes(request), timeout=15
        )
        bruin_repository._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == bruin_500_response

    @pytest.mark.asyncio
    async def unpause_ticket_detail__detail_unpaused_test(
        self, bruin_repository, make_unpause_ticket_detail_request, bruin_generic_200_response
    ):
        ticket_id = 12345
        service_number = "VC1234567"

        request = make_unpause_ticket_detail_request(
            request_id=uuid_,
            ticket_id=ticket_id,
            service_number=service_number,
        )
        NATS_AIO_MSG = Msg(_client="NATS", data=to_json_bytes(bruin_generic_200_response))
        bruin_repository._nats_client.request = AsyncMock(return_value=NATS_AIO_MSG)

        with uuid_mock:
            result = await bruin_repository.unpause_ticket_detail(ticket_id, service_number)

        bruin_repository._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.unpause", to_json_bytes(request), timeout=30
        )
        assert result == bruin_generic_200_response

    @pytest.mark.asyncio
    async def unpause_ticket_detail__rpc_request_failing_test(
        self, bruin_repository, make_unpause_ticket_detail_request
    ):
        ticket_id = 12345
        service_number = "VC1234567"

        request = make_unpause_ticket_detail_request(
            request_id=uuid_,
            ticket_id=ticket_id,
            service_number=service_number,
        )

        bruin_repository._nats_client.request = AsyncMock(side_effect=Exception)
        bruin_repository._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await bruin_repository.unpause_ticket_detail(ticket_id, service_number)

        bruin_repository._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.unpause", to_json_bytes(request), timeout=30
        )
        bruin_repository._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def unpause_ticket_detail__rpc_request_has_not_2xx_status_test(
        self, bruin_repository, make_unpause_ticket_detail_request, bruin_500_response
    ):
        ticket_id = 12345
        service_number = "VC1234567"

        request = make_unpause_ticket_detail_request(
            request_id=uuid_,
            ticket_id=ticket_id,
            service_number=service_number,
        )
        NATS_AIO_MSG = Msg(_client="NATS", data=to_json_bytes(bruin_500_response))
        bruin_repository._nats_client.request = AsyncMock(return_value=NATS_AIO_MSG)
        bruin_repository._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await bruin_repository.unpause_ticket_detail(ticket_id, service_number)

        bruin_repository._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.unpause", to_json_bytes(request), timeout=30
        )
        bruin_repository._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == bruin_500_response

    @pytest.mark.asyncio
    async def create_affecting_ticket__ticket_created_test(
        self, bruin_repository, make_create_ticket_request, make_create_ticket_200_response, make_contact_info
    ):
        client_id = 12345
        service_number = "VC0125"
        contacts = make_contact_info()

        request = make_create_ticket_request(
            request_id=uuid_,
            bruin_client_id=client_id,
            service_number=service_number,
            contact_info=contacts,
        )
        response = make_create_ticket_200_response(request_id=uuid_)
        NATS_AIO_MSG = Msg(_client="NATS", data=to_json_bytes(response))
        bruin_repository._nats_client.request = AsyncMock(return_value=NATS_AIO_MSG)

        with uuid_mock:
            result = await bruin_repository.create_affecting_ticket(client_id, service_number, contacts)

        bruin_repository._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.creation.request", to_json_bytes(request), timeout=90
        )
        assert result == response

    @pytest.mark.asyncio
    async def create_affecting_ticket__rpc_request_failing_test(
        self, bruin_repository, make_create_ticket_request, make_contact_info
    ):
        client_id = 12345
        service_number = "VC0125"
        contacts = make_contact_info()

        request = make_create_ticket_request(
            request_id=uuid_,
            bruin_client_id=client_id,
            service_number=service_number,
            contact_info=contacts,
        )

        bruin_repository._nats_client.request = AsyncMock(side_effect=Exception)
        bruin_repository._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await bruin_repository.create_affecting_ticket(client_id, service_number, contacts)

        bruin_repository._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.creation.request", to_json_bytes(request), timeout=90
        )
        bruin_repository._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def create_affecting_ticket__rpc_request_has_not_2xx_status_test(
        self, bruin_repository, make_create_ticket_request, bruin_500_response, make_contact_info
    ):

        client_id = 12345
        service_number = "VC0125"
        contacts = make_contact_info()

        request = make_create_ticket_request(
            request_id=uuid_,
            bruin_client_id=client_id,
            service_number=service_number,
            contact_info=contacts,
        )
        NATS_AIO_MSG = Msg(_client="NATS", data=to_json_bytes(bruin_500_response))
        bruin_repository._nats_client.request = AsyncMock(return_value=NATS_AIO_MSG)
        bruin_repository._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await bruin_repository.create_affecting_ticket(client_id, service_number, contacts)

        bruin_repository._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.creation.request", to_json_bytes(request), timeout=90
        )
        bruin_repository._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == bruin_500_response

    @pytest.mark.asyncio
    async def open_ticket__ticket_detail_reopened_test(
        self, bruin_repository, make_open_or_resolve_ticket_request, bruin_generic_200_response
    ):
        ticket_id = 12345
        detail_id = 67890

        request = make_open_or_resolve_ticket_request(
            request_id=uuid_,
            ticket_id=ticket_id,
            detail_id=detail_id,
        )
        NATS_AIO_MSG = Msg(_client="NATS", data=to_json_bytes(bruin_generic_200_response))
        bruin_repository._nats_client.request = AsyncMock(return_value=NATS_AIO_MSG)

        with uuid_mock:
            result = await bruin_repository.open_ticket(ticket_id, detail_id)

        bruin_repository._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.status.open", to_json_bytes(request), timeout=15
        )
        assert result == bruin_generic_200_response

    @pytest.mark.asyncio
    async def open_ticket__rpc_request_failing_test(self, bruin_repository, make_open_or_resolve_ticket_request):
        ticket_id = 12345
        detail_id = 67890

        request = make_open_or_resolve_ticket_request(
            request_id=uuid_,
            ticket_id=ticket_id,
            detail_id=detail_id,
        )

        bruin_repository._nats_client.request = AsyncMock(side_effect=Exception)
        bruin_repository._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await bruin_repository.open_ticket(ticket_id, detail_id)

        bruin_repository._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.status.open", to_json_bytes(request), timeout=15
        )
        bruin_repository._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def open_ticket__rpc_request_has_not_2xx_status_test(
        self, bruin_repository, make_open_or_resolve_ticket_request, bruin_500_response
    ):
        ticket_id = 12345
        detail_id = 67890

        request = make_open_or_resolve_ticket_request(
            request_id=uuid_,
            ticket_id=ticket_id,
            detail_id=detail_id,
        )
        NATS_AIO_MSG = Msg(_client="NATS", data=to_json_bytes(bruin_500_response))
        bruin_repository._nats_client.request = AsyncMock(return_value=NATS_AIO_MSG)
        bruin_repository._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await bruin_repository.open_ticket(ticket_id, detail_id)

        bruin_repository._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.status.open", to_json_bytes(request), timeout=15
        )
        bruin_repository._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == bruin_500_response

    @pytest.mark.asyncio
    async def change_detail_work_queue__work_queue_changed_test(
        self, bruin_repository, make_change_detail_work_queue_request, bruin_generic_200_response
    ):
        ticket_id = 12345
        detail_id = 67890
        target_queue = "Wireless Repair Intervention Needed"
        service_number = "VC1234567"

        request = make_change_detail_work_queue_request(
            request_id=uuid_,
            ticket_id=ticket_id,
            detail_id=detail_id,
            service_number=service_number,
            target_queue=target_queue,
        )
        NATS_AIO_MSG = Msg(_client="NATS", data=to_json_bytes(bruin_generic_200_response))
        bruin_repository._nats_client.request = AsyncMock(return_value=NATS_AIO_MSG)

        with uuid_mock:
            result = await bruin_repository.change_detail_work_queue(
                service_number=service_number, ticket_id=ticket_id, detail_id=detail_id, task_result=target_queue
            )

        bruin_repository._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.change.work", to_json_bytes(request), timeout=90
        )
        assert result == bruin_generic_200_response

    @pytest.mark.asyncio
    async def change_detail_work_queue__rpc_request_failing_test(
        self, bruin_repository, make_change_detail_work_queue_request
    ):
        ticket_id = 12345
        detail_id = 67890
        target_queue = "Wireless Repair Intervention Needed"
        service_number = "VC1234567"

        request = make_change_detail_work_queue_request(
            request_id=uuid_,
            ticket_id=ticket_id,
            detail_id=detail_id,
            service_number=service_number,
            target_queue=target_queue,
        )

        bruin_repository._nats_client.request = AsyncMock(side_effect=Exception)
        bruin_repository._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await bruin_repository.change_detail_work_queue(
                service_number=service_number, ticket_id=ticket_id, detail_id=detail_id, task_result=target_queue
            )

        bruin_repository._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.change.work", to_json_bytes(request), timeout=90
        )
        bruin_repository._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def change_detail_work_queue__rpc_request_has_not_2xx_status_test(
        self, bruin_repository, make_change_detail_work_queue_request, bruin_500_response
    ):
        ticket_id = 12345
        detail_id = 67890
        target_queue = "Wireless Repair Intervention Needed"
        service_number = "VC1234567"

        request = make_change_detail_work_queue_request(
            request_id=uuid_,
            ticket_id=ticket_id,
            detail_id=detail_id,
            service_number=service_number,
            target_queue=target_queue,
        )
        NATS_AIO_MSG = Msg(_client="NATS", data=to_json_bytes(bruin_500_response))
        bruin_repository._nats_client.request = AsyncMock(return_value=NATS_AIO_MSG)
        bruin_repository._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await bruin_repository.change_detail_work_queue(
                service_number=service_number, ticket_id=ticket_id, detail_id=detail_id, task_result=target_queue
            )

        bruin_repository._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.change.work", to_json_bytes(request), timeout=90
        )
        bruin_repository._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == bruin_500_response

    @pytest.mark.asyncio
    async def resolve_ticket__ticket_detail_resolved_test(
        self, bruin_repository, make_open_or_resolve_ticket_request, bruin_generic_200_response
    ):
        ticket_id = 12345
        detail_id = 67890

        request = make_open_or_resolve_ticket_request(
            request_id=uuid_,
            ticket_id=ticket_id,
            detail_id=detail_id,
        )
        NATS_AIO_MSG = Msg(_client="NATS", data=to_json_bytes(bruin_generic_200_response))
        bruin_repository._nats_client.request = AsyncMock(return_value=NATS_AIO_MSG)

        with uuid_mock:
            result = await bruin_repository.resolve_ticket(ticket_id, detail_id)

        bruin_repository._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.status.resolve", to_json_bytes(request), timeout=15
        )
        assert result == bruin_generic_200_response

    @pytest.mark.asyncio
    async def resolve_ticket__rpc_request_failing_test(self, bruin_repository, make_open_or_resolve_ticket_request):
        ticket_id = 12345
        detail_id = 67890

        request = make_open_or_resolve_ticket_request(
            request_id=uuid_,
            ticket_id=ticket_id,
            detail_id=detail_id,
        )

        bruin_repository._nats_client.request = AsyncMock(side_effect=Exception)
        bruin_repository._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await bruin_repository.resolve_ticket(ticket_id, detail_id)

        bruin_repository._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.status.resolve", to_json_bytes(request), timeout=15
        )
        bruin_repository._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def resolve_ticket__rpc_request_has_not_2xx_status_test(
        self, bruin_repository, make_open_or_resolve_ticket_request, bruin_500_response
    ):
        ticket_id = 12345
        detail_id = 67890

        request = make_open_or_resolve_ticket_request(
            request_id=uuid_,
            ticket_id=ticket_id,
            detail_id=detail_id,
        )
        NATS_AIO_MSG = Msg(_client="NATS", data=to_json_bytes(bruin_500_response))
        bruin_repository._nats_client.request = AsyncMock(return_value=NATS_AIO_MSG)
        bruin_repository._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await bruin_repository.resolve_ticket(ticket_id, detail_id)

        bruin_repository._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.status.resolve", to_json_bytes(request), timeout=15
        )
        bruin_repository._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == bruin_500_response

    def get_contact_info_for_site__all_fields_ok_test(self, bruin_repository, make_site_details, make_contact_info):
        site_detail_email = "test@email.com"
        site_detail_phone = "510-111-111"
        site_detail_name = "Help Desk"

        site_details = make_site_details(
            contact_name=site_detail_name, contact_phone=site_detail_phone, contact_email=site_detail_email
        )

        contact_info = bruin_repository.get_contact_info_for_site(site_details)

        expected = make_contact_info(email=site_detail_email, phone=site_detail_phone, name=site_detail_name)
        assert contact_info == expected

    def get_contact_info_for_site__no_phone_test(self, bruin_repository, make_site_details, make_contact_info):
        site_detail_email = "test@email.com"
        site_detail_phone = None
        site_detail_name = "Help Desk"

        site_details = make_site_details(
            contact_name=site_detail_name, contact_phone=site_detail_phone, contact_email=site_detail_email
        )

        contact_info = bruin_repository.get_contact_info_for_site(site_details)

        expected = make_contact_info(email=site_detail_email, name=site_detail_name)
        assert contact_info == expected

    def get_contact_info_for_site__no_email_test(self, bruin_repository, make_site_details):
        site_detail_email = None
        site_detail_phone = "510-111-111"
        site_detail_name = "Help Desk"

        site_details = make_site_details(
            contact_name=site_detail_name, contact_phone=site_detail_phone, contact_email=site_detail_email
        )

        contact_info = bruin_repository.get_contact_info_for_site(site_details)

        assert contact_info is None

    def get_contact_info_for_site__no_name_test(self, bruin_repository, make_site_details):
        site_detail_email = "test@email.com"
        site_detail_phone = "510-111-111"
        site_detail_name = None

        site_details = make_site_details(
            contact_name=site_detail_name, contact_phone=site_detail_phone, contact_email=site_detail_email
        )

        contact_info = bruin_repository.get_contact_info_for_site(site_details)

        assert contact_info is None

    @pytest.mark.asyncio
    async def get_affecting_tickets__no_service_number_specified_test(self, bruin_repository):
        bruin_client_id = 12345
        ticket_statuses = ["New", "InProgress", "Draft"]
        ticket_topic = "VAS"

        await bruin_repository.get_affecting_tickets(bruin_client_id, ticket_statuses)

        bruin_repository.get_tickets.assert_awaited_once_with(
            bruin_client_id, ticket_topic, ticket_statuses, service_number=None
        )

    @pytest.mark.asyncio
    async def get_affecting_tickets__service_number_specified_test(self, bruin_repository):
        bruin_client_id = 12345
        service_number = "VC1234567"
        ticket_statuses = ["New", "InProgress", "Draft"]
        ticket_topic = "VAS"

        await bruin_repository.get_affecting_tickets(bruin_client_id, ticket_statuses, service_number=service_number)

        bruin_repository.get_tickets.assert_awaited_once_with(
            bruin_client_id, ticket_topic, ticket_statuses, service_number=service_number
        )

    @pytest.mark.asyncio
    async def get_open_affecting_tickets__no_service_number_specified_test(self, bruin_repository):
        bruin_client_id = 12345
        ticket_statuses = ["New", "InProgress", "Draft"]

        await bruin_repository.get_open_affecting_tickets(bruin_client_id)

        bruin_repository.get_affecting_tickets.assert_awaited_once_with(
            bruin_client_id, ticket_statuses, service_number=None
        )

    @pytest.mark.asyncio
    async def get_open_affecting_tickets__service_number_specified_test(self, bruin_repository):
        bruin_client_id = 12345
        service_number = "VC1234567"
        ticket_statuses = ["New", "InProgress", "Draft"]

        await bruin_repository.get_open_affecting_tickets(bruin_client_id, service_number=service_number)

        bruin_repository.get_affecting_tickets.assert_awaited_once_with(
            bruin_client_id, ticket_statuses, service_number=service_number
        )

    @pytest.mark.asyncio
    async def get_resolved_affecting_tickets__no_service_number_specified_test(self, bruin_repository):
        bruin_client_id = 12345
        ticket_statuses = ["Resolved"]

        await bruin_repository.get_resolved_affecting_tickets(bruin_client_id)

        bruin_repository.get_affecting_tickets.assert_awaited_once_with(
            bruin_client_id, ticket_statuses, service_number=None
        )

    @pytest.mark.asyncio
    async def get_resolved_affecting_tickets__service_number_specified_test(self, bruin_repository):
        bruin_client_id = 12345
        service_number = "VC1234567"
        ticket_statuses = ["Resolved"]

        await bruin_repository.get_resolved_affecting_tickets(bruin_client_id, service_number=service_number)

        bruin_repository.get_affecting_tickets.assert_awaited_once_with(
            bruin_client_id, ticket_statuses, service_number=service_number
        )

    @pytest.mark.asyncio
    async def append_autoresolve_note_to_ticket_test(self, bruin_repository, bruin_generic_200_response):
        serial_number = "VC1234567"

        ticket_id = 11111
        ticket_note = (
            "#*MetTel's IPA*#\n"
            "All Service Affecting conditions (Latency, Packet Loss, Jitter, Bandwidth Over Utilization "
            "and Circuit Instability) have stabilized.\n"
            f"Auto-resolving task for serial: {serial_number}\n"
            f"TimeStamp: {CURRENT_DATETIME}"
        )

        bruin_repository.append_note_to_ticket.return_value = bruin_generic_200_response

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=CURRENT_DATETIME)
        with patch.object(bruin_repository_module, "datetime", new=datetime_mock):
            with patch.object(bruin_repository_module, "timezone", new=Mock()):
                result = await bruin_repository.append_autoresolve_note_to_ticket(ticket_id, serial_number)

        bruin_repository.append_note_to_ticket.assert_awaited_once_with(
            ticket_id, ticket_note, service_numbers=[serial_number]
        )
        assert result == bruin_generic_200_response

    @pytest.mark.asyncio
    async def post_notification_email_milestone__200_test(
        self, bruin_repository, make_post_notification_email_milestone_request, bruin_generic_200_response
    ):
        ticket_id = 12345
        service_number = "VC1234567"
        notification_type = "TicketBYOBAffectingRepairAcknowledgement-E-Mail"
        request = make_post_notification_email_milestone_request(
            request_id=uuid_,
            ticket_id=ticket_id,
            service_number=service_number,
            notification_type=notification_type,
        )
        NATS_AIO_MSG = Msg(_client="NATS", data=to_json_bytes(bruin_generic_200_response))
        bruin_repository._nats_client.request = AsyncMock(return_value=NATS_AIO_MSG)

        with uuid_mock:
            result = await bruin_repository.post_notification_email_milestone(
                ticket_id, service_number, notification_type
            )

        bruin_repository._nats_client.request.assert_awaited_once_with(
            "bruin.notification.email.milestone", to_json_bytes(request), timeout=90
        )
        bruin_repository._notifications_repository.send_slack_message.assert_not_awaited()
        assert result == bruin_generic_200_response

    @pytest.mark.asyncio
    async def post_notification_email_milestone__exception_test(
        self, bruin_repository, make_post_notification_email_milestone_request
    ):
        ticket_id = 12345
        service_number = "VC1234567"
        notification_type = "TicketBYOBAffectingRepairAcknowledgement-E-Mail"
        request = make_post_notification_email_milestone_request(
            request_id=uuid_,
            ticket_id=ticket_id,
            service_number=service_number,
            notification_type=notification_type,
        )
        bruin_repository._nats_client.request = AsyncMock(side_effect=Exception)
        bruin_repository._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await bruin_repository.post_notification_email_milestone(
                ticket_id, service_number, notification_type
            )

        bruin_repository._nats_client.request.assert_awaited_once_with(
            "bruin.notification.email.milestone", to_json_bytes(request), timeout=90
        )
        bruin_repository._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def post_notification_email_milestone__non_2xx_status_test(
        self, bruin_repository, make_post_notification_email_milestone_request, bruin_500_response
    ):
        ticket_id = 12345
        service_number = "VC1234567"
        notification_type = "TicketBYOBAffectingRepairAcknowledgement-E-Mail"
        request = make_post_notification_email_milestone_request(
            request_id=uuid_,
            ticket_id=ticket_id,
            service_number=service_number,
            notification_type=notification_type,
        )
        NATS_AIO_MSG = Msg(_client="NATS", data=to_json_bytes(bruin_500_response))
        bruin_repository._nats_client.request = AsyncMock(return_value=NATS_AIO_MSG)
        bruin_repository._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await bruin_repository.post_notification_email_milestone(
                ticket_id, service_number, notification_type
            )

        bruin_repository._nats_client.request.assert_awaited_once_with(
            "bruin.notification.email.milestone", to_json_bytes(request), timeout=90
        )
        bruin_repository._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == bruin_500_response

    @pytest.mark.asyncio
    async def send_initial_email_milestone_notification_test(self, bruin_repository, bruin_generic_200_response):
        ticket_id = 12345
        service_number = "VC1234567"
        notification_type = "TicketBYOBAffectingRepairAcknowledgement-E-Mail"
        NATS_AIO_MSG = Msg(_client="NATS", data=to_json_bytes(bruin_generic_200_response))
        bruin_repository._nats_client.request = AsyncMock(return_value=NATS_AIO_MSG)

        response = await bruin_repository.send_initial_email_milestone_notification(ticket_id, service_number)

        bruin_repository.post_notification_email_milestone.assert_awaited_once_with(
            ticket_id, service_number, notification_type
        )
        assert response == bruin_generic_200_response

    @pytest.mark.asyncio
    async def send_reminder_email_milestone_notification_test(self, bruin_repository, bruin_generic_200_response):
        ticket_id = 12345
        service_number = "VC1234567"
        notification_type = "TicketBYOBAffectingRepairReminder-E-Mail"
        NATS_AIO_MSG = Msg(_client="NATS", data=to_json_bytes(bruin_generic_200_response))
        bruin_repository._nats_client.request = AsyncMock(return_value=NATS_AIO_MSG)

        response = await bruin_repository.send_reminder_email_milestone_notification(ticket_id, service_number)

        bruin_repository.post_notification_email_milestone.assert_awaited_once_with(
            ticket_id, service_number, notification_type
        )
        assert response == bruin_generic_200_response

    # ------------------------ Legacy tests for methods used in SA reports ------------------------
    @pytest.mark.asyncio
    async def get_ticket_details_test(self, service_affecting_monitor_reports, ticket_1, ticket_details_1):
        response_ticket_details_1 = {"body": ticket_details_1, "status": 200}
        expected_response = {"ticket": ticket_1, "ticket_details": ticket_details_1}
        NATS_AIO_MSG = Msg(_client="NATS", data=to_json_bytes(response_ticket_details_1))
        service_affecting_monitor_reports._bruin_repository._nats_client.request = AsyncMock(side_effect=[NATS_AIO_MSG])
        response = await service_affecting_monitor_reports._bruin_repository._get_ticket_details(ticket_1)
        assert response == expected_response

    @pytest.mark.asyncio
    async def get_ticket_details_400_test(self, service_affecting_monitor_reports, ticket_1):
        response_ticket_details_1 = {"body": "Some error", "status": 400}
        expected_response = None
        NATS_AIO_MSG = Msg(_client="NATS", data=to_json_bytes(response_ticket_details_1))
        service_affecting_monitor_reports._bruin_repository._nats_client.request = AsyncMock(side_effect=[NATS_AIO_MSG])
        service_affecting_monitor_reports._notifications_repository.send_slack_message = AsyncMock()

        response = await service_affecting_monitor_reports._bruin_repository._get_ticket_details(ticket_1)

        assert response == expected_response

    @pytest.mark.asyncio
    async def get_ticket_details_401_and_or_403_test(self, service_affecting_monitor_reports, ticket_1):
        response_ticket_details_1 = {"body": "Some error", "status": 401}
        slack_msg = (
            f"[service-affecting-monitor-reports]Max retries reached getting ticket details {ticket_1['ticketID']}"
        )
        expected_response = None
        service_affecting_monitor_reports._notifications_repository.send_slack_message = AsyncMock()
        NATS_AIO_MSG = Msg(_client="NATS", data=to_json_bytes(response_ticket_details_1))
        service_affecting_monitor_reports._bruin_repository.get_ticket_details = AsyncMock(side_effect=[NATS_AIO_MSG])
        service_affecting_monitor_reports._notifications_repository.send_slack_message = AsyncMock()

        response = await service_affecting_monitor_reports._bruin_repository._get_ticket_details(ticket_1)

        assert response == expected_response

        service_affecting_monitor_reports._notifications_repository.send_slack_message.assert_awaited_once_with(
            slack_msg
        )

    @pytest.mark.asyncio
    async def get_affecting_ticket_for_report_test(
        self,
        service_affecting_monitor_reports,
        response_bruin_with_all_tickets,
        response_bruin_with_all_tickets_without_details,
        report,
        ticket_1,
        ticket_details_1,
        ticket_2,
        ticket_details_2,
        ticket_3,
        ticket_details_3,
        ticket_4,
        ticket_details_4,
    ):
        start_date = "start_date"
        end_date = "end_date"
        ticket_statuses = ["New", "InProgress", "Draft", "Resolved", "Closed"]
        responses_get_ticket_details = [
            {"ticket": ticket_1, "ticket_details": ticket_details_1},
            {"ticket": ticket_2, "ticket_details": ticket_details_2},
            {"ticket": ticket_3, "ticket_details": ticket_details_3},
            {"ticket": ticket_4, "ticket_details": ticket_details_4},
        ]
        service_affecting_monitor_reports._bruin_repository.get_all_affecting_tickets = AsyncMock(
            side_effect=[response_bruin_with_all_tickets_without_details]
        )

        with uuid_mock:
            with patch.object(asyncio, "gather", new=AsyncMock(side_effect=[responses_get_ticket_details])):
                response = await service_affecting_monitor_reports._bruin_repository.get_affecting_ticket_for_report(
                    report["client_id"], start_date, end_date
                )

        assert response == response_bruin_with_all_tickets

        service_affecting_monitor_reports._bruin_repository.get_all_affecting_tickets.assert_has_awaits(
            [
                call(
                    client_id=report["client_id"],
                    end_date=end_date,
                    start_date=start_date,
                    ticket_statuses=ticket_statuses,
                )
            ]
        )

    @pytest.mark.asyncio
    async def get_affecting_ticket_for_report_no_tickets_test(
        self, service_affecting_monitor_reports, report, response_bruin_with_no_tickets
    ):
        start_date = "start_date"
        end_date = "end_date"
        ticket_statuses = ["New", "InProgress", "Draft", "Resolved", "Closed"]
        ticket_request_msg = {
            "request_id": uuid_,
            "body": {
                "client_id": report["client_id"],
                "category": service_affecting_monitor_reports._config.PRODUCT_CATEGORY,
                "ticket_topic": "VAS",
                "ticket_status": ticket_statuses,
                "start_date": start_date,
                "end_date": end_date,
            },
        }

        responses_get_ticket_details = []
        NATS_AIO_MSG = Msg(_client="NATS", data=to_json_bytes(response_bruin_with_no_tickets))
        service_affecting_monitor_reports._bruin_repository._nats_client.request = AsyncMock(side_effect=[NATS_AIO_MSG])

        with uuid_mock:
            with patch.object(asyncio, "gather", new=AsyncMock(side_effect=[responses_get_ticket_details])):
                response = await service_affecting_monitor_reports._bruin_repository.get_affecting_ticket_for_report(
                    report["client_id"], start_date, end_date
                )

        assert response == {}

        service_affecting_monitor_reports._bruin_repository._nats_client.request.assert_has_awaits(
            [call("bruin.ticket.request", to_json_bytes(ticket_request_msg), timeout=90)]
        )

    @pytest.mark.asyncio
    async def get_affecting_ticket_for_report_retries_test(
        self, service_affecting_monitor_reports, report, response_bruin_401, response_bruin_403
    ):
        start_date = "start_date"
        end_date = "end_date"
        ticket_statuses = ["New", "InProgress", "Draft", "Resolved", "Closed"]
        ticket_request_msg = {
            "request_id": uuid_,
            "body": {
                "client_id": report["client_id"],
                "category": service_affecting_monitor_reports._config.PRODUCT_CATEGORY,
                "ticket_topic": "VAS",
                "ticket_status": ticket_statuses,
                "start_date": start_date,
                "end_date": end_date,
            },
        }
        slack_msg = f"Max retries reached getting all tickets for the service affecting monitor process."

        responses_get_ticket_details = []
        NATS_AIO_MSG_401 = Msg(_client="NATS", data=to_json_bytes(response_bruin_401))
        NATS_AIO_MSG_403 = Msg(_client="NATS", data=to_json_bytes(response_bruin_403))
        service_affecting_monitor_reports._bruin_repository._nats_client.request = AsyncMock(
            side_effect=[NATS_AIO_MSG_403, NATS_AIO_MSG_401, NATS_AIO_MSG_403]
        )
        service_affecting_monitor_reports._notifications_repository.send_slack_message = AsyncMock()

        with uuid_2_mock:
            with uuid_mock:
                with patch.object(asyncio, "gather", new=AsyncMock(side_effect=[responses_get_ticket_details])):
                    response = (
                        await service_affecting_monitor_reports._bruin_repository.get_affecting_ticket_for_report(
                            report["client_id"], start_date, end_date
                        )
                    )

        assert response is None

        service_affecting_monitor_reports._bruin_repository._nats_client.request.assert_has_awaits(
            [
                call("bruin.ticket.request", to_json_bytes(ticket_request_msg), timeout=90),
                call("bruin.ticket.request", to_json_bytes(ticket_request_msg), timeout=90),
            ]
        )
        service_affecting_monitor_reports._notifications_repository.send_slack_message.assert_awaited_once_with(
            slack_msg
        )

    @pytest.mark.asyncio
    async def get_affecting_ticket_for_report_with_error_test(
        self, bruin_repository, report, response_bruin_with_error
    ):
        start_date = "start_date"
        end_date = "end_date"
        ticket_statuses = ["New", "InProgress", "Draft", "Resolved", "Closed"]
        ticket_request_msg = {
            "request_id": uuid_,
            "body": {
                "client_id": report["client_id"],
                "category": bruin_repository._config.PRODUCT_CATEGORY,
                "ticket_topic": "VAS",
                "ticket_status": ticket_statuses,
                "start_date": start_date,
                "end_date": end_date,
            },
        }
        responses_get_ticket_details = []
        NATS_AIO_MSG = Msg(_client="NATS", data=to_json_bytes(response_bruin_with_error))
        bruin_repository._nats_client.request = AsyncMock(side_effect=[NATS_AIO_MSG])

        with uuid_mock:
            with patch.object(asyncio, "gather", new=AsyncMock(side_effect=[responses_get_ticket_details])):
                response = await bruin_repository.get_affecting_ticket_for_report(
                    report["client_id"], start_date, end_date
                )

        assert response is None

        bruin_repository._nats_client.request.assert_has_awaits(
            [call("bruin.ticket.request", to_json_bytes(ticket_request_msg), timeout=90)]
        )

    @pytest.mark.asyncio
    async def append_asr_forwarding_note_test(self, bruin_repository, make_link, bruin_generic_200_response):
        ticket_id = 11111
        serial_number = "VC1234567"
        link = make_link(interface="GE1", display_name="Test", state="KO")

        ticket_note = (
            "#*MetTel's IPA*#\n"
            "Status of Wired Link GE1 (Test) is KO.\n"
            "Moving task to: ASR Investigate\n"
            f"TimeStamp: {CURRENT_DATETIME}"
        )

        bruin_repository.append_note_to_ticket.return_value = bruin_generic_200_response

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=CURRENT_DATETIME)
        with patch.object(bruin_repository_module, "datetime", new=datetime_mock):
            with patch.object(bruin_repository_module, "timezone", new=Mock()):
                result = await bruin_repository.append_asr_forwarding_note(ticket_id, link, serial_number)

        bruin_repository.append_note_to_ticket.assert_awaited_once_with(
            ticket_id, ticket_note, service_numbers=[serial_number]
        )

        assert result == bruin_generic_200_response
