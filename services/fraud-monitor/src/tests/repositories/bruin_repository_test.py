from datetime import datetime
from unittest.mock import AsyncMock, Mock, patch

import pytest
from nats.aio.msg import Msg
from shortuuid import uuid

from application.repositories import bruin_repository as bruin_repository_module
from application.repositories import nats_error_response
from application.repositories.utils_repository import to_json_bytes
from config import testconfig

uuid_ = uuid()
uuid_mock = patch.object(bruin_repository_module, "uuid", return_value=uuid_)


class TestBruinRepository:
    def instance_test(self, bruin_repository, nats_client, notifications_repository):
        assert bruin_repository._nats_client is nats_client
        assert bruin_repository._config is testconfig
        assert bruin_repository._notifications_repository is notifications_repository

    @pytest.mark.asyncio
    async def get_client_info_by_did__rpc_request_success_test(
        self, bruin_repository, make_get_client_info_by_did_request, bruin_generic_200_response
    ):
        did = "+14159999999"
        request = make_get_client_info_by_did_request(request_id=uuid_, did=did)

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(bruin_generic_200_response)
        bruin_repository._nats_client.request = AsyncMock(return_value=response_msg)

        with uuid_mock:
            result = await bruin_repository.get_client_info_by_did(did)

        bruin_repository._nats_client.request.assert_awaited_once_with(
            "bruin.customer.get.info_by_did", to_json_bytes(request), timeout=15
        )
        assert result == bruin_generic_200_response

    @pytest.mark.asyncio
    async def get_client_info_by_did__rpc_request_failing_test(
        self, bruin_repository, make_get_client_info_by_did_request
    ):
        did = "+14159999999"
        request = make_get_client_info_by_did_request(request_id=uuid_, did=did)

        bruin_repository._nats_client.request.side_effect = Exception
        bruin_repository._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await bruin_repository.get_client_info_by_did(did)

        bruin_repository._nats_client.request.assert_awaited_once_with(
            "bruin.customer.get.info_by_did", to_json_bytes(request), timeout=15
        )
        bruin_repository._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_client_info_by_did__rpc_request_has_not_2xx_status_test(
        self, bruin_repository, make_get_client_info_by_did_request, bruin_500_response
    ):
        did = "+14159999999"
        request = make_get_client_info_by_did_request(request_id=uuid_, did=did)

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(bruin_500_response)
        bruin_repository._nats_client.request = AsyncMock(return_value=response_msg)
        bruin_repository._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await bruin_repository.get_client_info_by_did(did)

        bruin_repository._nats_client.request.assert_awaited_once_with(
            "bruin.customer.get.info_by_did", to_json_bytes(request), timeout=15
        )
        bruin_repository._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == bruin_500_response

    @pytest.mark.asyncio
    async def get_tickets__no_service_number_specified_test(
        self, bruin_repository, make_ticket, make_get_tickets_request, make_rpc_response
    ):
        client_id = 12345
        service_number = None
        ticket_statuses = ["New", "InProgress", "Draft"]
        ticket_topic = "VAS"

        ticket_1 = make_ticket(ticket_id=1, client_id=client_id)
        ticket_2 = make_ticket(ticket_id=2, client_id=client_id)
        tickets = [ticket_1, ticket_2]

        request = make_get_tickets_request(
            request_id=uuid_,
            bruin_client_id=client_id,
            ticket_statuses=ticket_statuses,
            ticket_topic=ticket_topic,
        )
        response = make_rpc_response(
            request_id=uuid_,
            body=tickets,
            status=200,
        )

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(response)
        bruin_repository._nats_client.request = AsyncMock(return_value=response_msg)

        with uuid_mock:
            result = await bruin_repository.get_tickets(client_id, ticket_topic, ticket_statuses, service_number)

        bruin_repository._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.basic.request", to_json_bytes(request), timeout=90
        )
        assert result == response

    @pytest.mark.asyncio
    async def get_tickets__service_number_specified_test(
        self, bruin_repository, make_ticket, make_get_tickets_request, make_rpc_response
    ):
        client_id = 12345
        service_number = "VC1234567"
        ticket_statuses = ["New", "InProgress", "Draft"]
        ticket_topic = "VAS"

        ticket_1 = make_ticket(ticket_id=1, client_id=client_id)
        ticket_2 = make_ticket(ticket_id=2, client_id=client_id)
        tickets = [ticket_1, ticket_2]

        request = make_get_tickets_request(
            request_id=uuid_,
            bruin_client_id=client_id,
            ticket_statuses=ticket_statuses,
            ticket_topic=ticket_topic,
            service_number=service_number,
        )
        response = make_rpc_response(
            request_id=uuid_,
            body=tickets,
            status=200,
        )

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(response)
        bruin_repository._nats_client.request = AsyncMock(return_value=response_msg)

        with uuid_mock:
            result = await bruin_repository.get_tickets(client_id, ticket_topic, ticket_statuses, service_number)

        bruin_repository._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.basic.request", to_json_bytes(request), timeout=90
        )
        assert result == response

    @pytest.mark.asyncio
    async def get_tickets__rpc_request_failing_test(self, bruin_repository, make_get_tickets_request):
        client_id = 12345
        service_number = "VC1234567"
        ticket_statuses = ["New", "InProgress", "Draft"]
        ticket_topic = "VAS"

        request = make_get_tickets_request(
            request_id=uuid_,
            bruin_client_id=client_id,
            ticket_statuses=ticket_statuses,
            ticket_topic=ticket_topic,
            service_number=service_number,
        )

        bruin_repository._nats_client.request.side_effect = Exception
        bruin_repository._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await bruin_repository.get_tickets(client_id, ticket_topic, ticket_statuses, service_number)

        bruin_repository._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.basic.request", to_json_bytes(request), timeout=90
        )
        bruin_repository._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_tickets__rpc_request_has_not_2xx_status_test(
        self, bruin_repository, make_get_tickets_request, bruin_500_response
    ):
        client_id = 12345
        service_number = "VC1234567"
        ticket_statuses = ["New", "InProgress", "Draft"]
        ticket_topic = "VAS"

        request = make_get_tickets_request(
            request_id=uuid_,
            bruin_client_id=client_id,
            ticket_statuses=ticket_statuses,
            ticket_topic=ticket_topic,
            service_number=service_number,
        )

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(bruin_500_response)
        bruin_repository._nats_client.request = AsyncMock(return_value=response_msg)
        bruin_repository._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await bruin_repository.get_tickets(client_id, ticket_topic, ticket_statuses, service_number)

        bruin_repository._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.basic.request", to_json_bytes(request), timeout=90
        )
        bruin_repository._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == bruin_500_response

    @pytest.mark.asyncio
    async def get_fraud_tickets_test(self, bruin_repository):
        bruin_client_id = 12345
        service_number = "VC1234567"
        ticket_statuses = ["New", "InProgress", "Draft"]
        ticket_topic = "VAS"

        await bruin_repository.get_fraud_tickets(bruin_client_id, ticket_statuses, service_number)

        bruin_repository.get_tickets.assert_awaited_once_with(
            bruin_client_id, ticket_topic, ticket_statuses, service_number
        )

    @pytest.mark.asyncio
    async def get_open_fraud_tickets_test(self, bruin_repository):
        bruin_client_id = 12345
        service_number = "VC1234567"
        ticket_statuses = ["New", "InProgress", "Draft"]

        await bruin_repository.get_open_fraud_tickets(bruin_client_id, service_number)

        bruin_repository.get_fraud_tickets.assert_awaited_once_with(bruin_client_id, ticket_statuses, service_number)

    @pytest.mark.asyncio
    async def get_resolved_fraud_tickets_test(self, bruin_repository):
        bruin_client_id = 12345
        service_number = "VC1234567"
        ticket_statuses = ["Resolved"]

        await bruin_repository.get_resolved_fraud_tickets(bruin_client_id, service_number)

        bruin_repository.get_fraud_tickets.assert_awaited_once_with(bruin_client_id, ticket_statuses, service_number)

    @pytest.mark.asyncio
    async def get_ticket_details__details_retrieved_test(
        self,
        bruin_repository,
        make_get_ticket_details_request,
        make_detail_item,
        make_ticket_note,
        make_ticket_details,
        make_rpc_response,
    ):
        ticket_id = 11111

        detail_item_1 = make_detail_item(id_=1)
        detail_item_2 = make_detail_item(id_=2)
        detail_items = [detail_item_1, detail_item_2]

        ticket_note_1 = make_ticket_note(id_=1)
        ticket_note_2 = make_ticket_note(id_=2)
        ticket_notes = [ticket_note_1, ticket_note_2]

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

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(response)
        bruin_repository._nats_client.request = AsyncMock(return_value=response_msg)

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

        bruin_repository._nats_client.request.side_effect = Exception
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

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(bruin_500_response)
        bruin_repository._nats_client.request = AsyncMock(return_value=response_msg)
        bruin_repository._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await bruin_repository.get_ticket_details(ticket_id)

        bruin_repository._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.details.request", to_json_bytes(request), timeout=15
        )
        bruin_repository._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == bruin_500_response

    @pytest.mark.asyncio
    async def get_client_info__rpc_request_success_test(
        self, bruin_repository, make_get_client_info_request, bruin_generic_200_response
    ):
        service_number = "VC1234567"
        request = make_get_client_info_request(request_id=uuid_, service_number=service_number)

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(bruin_generic_200_response)
        bruin_repository._nats_client.request = AsyncMock(return_value=response_msg)

        with uuid_mock:
            result = await bruin_repository.get_client_info(service_number)

        bruin_repository._nats_client.request.assert_awaited_once_with(
            "bruin.customer.get.info", to_json_bytes(request), timeout=30
        )
        assert result == bruin_generic_200_response

    @pytest.mark.asyncio
    async def get_client_info__rpc_request_failing_test(self, bruin_repository, make_get_client_info_request):
        service_number = "VC1234567"
        request = make_get_client_info_request(request_id=uuid_, service_number=service_number)

        bruin_repository._nats_client.request.side_effect = Exception
        bruin_repository._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await bruin_repository.get_client_info(service_number)

        bruin_repository._nats_client.request.assert_awaited_once_with(
            "bruin.customer.get.info", to_json_bytes(request), timeout=30
        )
        bruin_repository._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_client_info__rpc_request_has_not_2xx_status_test(
        self, bruin_repository, make_get_client_info_request, bruin_500_response
    ):
        service_number = "VC1234567"
        request = make_get_client_info_request(request_id=uuid_, service_number=service_number)

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(bruin_500_response)
        bruin_repository._nats_client.request = AsyncMock(return_value=response_msg)
        bruin_repository._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await bruin_repository.get_client_info(service_number)

        bruin_repository._nats_client.request.assert_awaited_once_with(
            "bruin.customer.get.info", to_json_bytes(request), timeout=30
        )
        bruin_repository._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == bruin_500_response

    @pytest.mark.asyncio
    async def get_site_details__rpc_request_success_test(
        self, bruin_repository, make_get_site_details_request, bruin_generic_200_response
    ):
        client_id = 12345
        site_id = 11111
        request = make_get_site_details_request(request_id=uuid_, client_id=client_id, site_id=site_id)

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(bruin_generic_200_response)
        bruin_repository._nats_client.request = AsyncMock(return_value=response_msg)

        with uuid_mock:
            result = await bruin_repository.get_site_details(client_id, site_id)

        bruin_repository._nats_client.request.assert_awaited_once_with(
            "bruin.get.site", to_json_bytes(request), timeout=60
        )
        assert result == bruin_generic_200_response

    @pytest.mark.asyncio
    async def get_site_details__rpc_request_failing_test(self, bruin_repository, make_get_site_details_request):
        client_id = 12345
        site_id = 11111
        request = make_get_site_details_request(request_id=uuid_, client_id=client_id, site_id=site_id)

        bruin_repository._nats_client.request.side_effect = Exception
        bruin_repository._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await bruin_repository.get_site_details(client_id, site_id)

        bruin_repository._nats_client.request.assert_awaited_once_with(
            "bruin.get.site", to_json_bytes(request), timeout=60
        )
        bruin_repository._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_site_details__rpc_request_has_not_2xx_status_test(
        self, bruin_repository, make_get_site_details_request, bruin_500_response
    ):
        client_id = 12345
        site_id = 11111
        request = make_get_site_details_request(request_id=uuid_, client_id=client_id, site_id=site_id)

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(bruin_500_response)
        bruin_repository._nats_client.request = AsyncMock(return_value=response_msg)
        bruin_repository._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await bruin_repository.get_site_details(client_id, site_id)

        bruin_repository._nats_client.request.assert_awaited_once_with(
            "bruin.get.site", to_json_bytes(request), timeout=60
        )
        bruin_repository._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == bruin_500_response

    @pytest.mark.asyncio
    async def append_note_to_ticket__rpc_request_success_test(
        self, bruin_repository, make_append_ticket_note_request, bruin_generic_200_response
    ):
        ticket_id = 11111
        ticket_note = "Ticket note"
        email_body = "Email body"
        msg_uid = "123456"
        service_number = "VC1234567"

        request = make_append_ticket_note_request(
            request_id=uuid_,
            ticket_id=ticket_id,
            note=ticket_note,
            service_numbers=[service_number],
        )

        bruin_repository._build_fraud_note.return_value = ticket_note
        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(bruin_generic_200_response)
        bruin_repository._nats_client.request = AsyncMock(return_value=response_msg)

        with uuid_mock:
            result = await bruin_repository.append_note_to_ticket(ticket_id, service_number, email_body, msg_uid)

        bruin_repository._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.note.append.request", to_json_bytes(request), timeout=60
        )
        assert result == bruin_generic_200_response

    @pytest.mark.asyncio
    async def append_note_to_ticket__rpc_request_failing_test(self, bruin_repository, make_append_ticket_note_request):
        ticket_id = 11111
        ticket_note = "Ticket note"
        email_body = "Email body"
        msg_uid = "123456"
        service_number = "VC1234567"

        request = make_append_ticket_note_request(
            request_id=uuid_,
            ticket_id=ticket_id,
            note=ticket_note,
            service_numbers=[service_number],
        )

        bruin_repository._build_fraud_note.return_value = ticket_note
        bruin_repository._nats_client.request.side_effect = Exception
        bruin_repository._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await bruin_repository.append_note_to_ticket(ticket_id, service_number, email_body, msg_uid)

        bruin_repository._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.note.append.request", to_json_bytes(request), timeout=60
        )
        bruin_repository._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def append_note_to_ticket__rpc_request_has_not_2xx_status_test(
        self, bruin_repository, make_append_ticket_note_request, bruin_500_response
    ):
        ticket_id = 11111
        ticket_note = "Ticket note"
        email_body = "Email body"
        msg_uid = "123456"
        service_number = "VC1234567"

        request = make_append_ticket_note_request(
            request_id=uuid_,
            ticket_id=ticket_id,
            note=ticket_note,
            service_numbers=[service_number],
        )

        bruin_repository._build_fraud_note.return_value = ticket_note
        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(bruin_500_response)
        bruin_repository._nats_client.request = AsyncMock(return_value=response_msg)
        bruin_repository._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await bruin_repository.append_note_to_ticket(ticket_id, service_number, email_body, msg_uid)

        bruin_repository._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.note.append.request", to_json_bytes(request), timeout=60
        )
        bruin_repository._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == bruin_500_response

    @pytest.mark.asyncio
    async def create_fraud_ticket__rpc_request_success_test(
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

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(response)
        bruin_repository._nats_client.request = AsyncMock(return_value=response_msg)

        with uuid_mock:
            result = await bruin_repository.create_fraud_ticket(client_id, service_number, contacts)

        bruin_repository._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.creation.request", to_json_bytes(request), timeout=90
        )
        assert result == response

    @pytest.mark.asyncio
    async def create_fraud_ticket__rpc_request_failing_test(
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

        bruin_repository._nats_client.request.side_effect = Exception
        bruin_repository._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await bruin_repository.create_fraud_ticket(client_id, service_number, contacts)

        bruin_repository._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.creation.request", to_json_bytes(request), timeout=90
        )
        bruin_repository._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def create_fraud_ticket__rpc_request_has_not_2xx_status_test(
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

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(bruin_500_response)
        bruin_repository._nats_client.request = AsyncMock(return_value=response_msg)
        bruin_repository._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await bruin_repository.create_fraud_ticket(client_id, service_number, contacts)

        bruin_repository._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.creation.request", to_json_bytes(request), timeout=90
        )
        bruin_repository._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == bruin_500_response

    @pytest.mark.asyncio
    async def open_ticket__rpc_request_success_test(
        self, bruin_repository, make_open_or_resolve_ticket_request, bruin_generic_200_response
    ):
        ticket_id = 12345
        detail_id = 67890

        request = make_open_or_resolve_ticket_request(
            request_id=uuid_,
            ticket_id=ticket_id,
            detail_id=detail_id,
        )

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(bruin_generic_200_response)
        bruin_repository._nats_client.request = AsyncMock(return_value=response_msg)

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

        bruin_repository._nats_client.request.side_effect = Exception
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

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(bruin_500_response)
        bruin_repository._nats_client.request = AsyncMock(return_value=response_msg)
        bruin_repository._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await bruin_repository.open_ticket(ticket_id, detail_id)

        bruin_repository._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.status.open", to_json_bytes(request), timeout=15
        )
        bruin_repository._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == bruin_500_response

    @pytest.mark.asyncio
    async def build_fraud_note_test(self, bruin_repository):
        email_body = "Possible Fraud Warning"
        msg_uid = "123456"
        timestamp = datetime.now()

        open_note = f"#*MetTel's IPA*#\nPossible Fraud Warning\n\nEmail UID: 123456\nTimeStamp: {timestamp}"

        re_open_note = (
            "#*MetTel's IPA*#\n"
            "Re-opening ticket.\n"
            "Possible Fraud Warning\n"
            "\n"
            "Email UID: 123456\n"
            f"TimeStamp: {timestamp}"
        )

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=timestamp)

        with patch.object(bruin_repository_module, "datetime", new=datetime_mock):
            result = bruin_repository._build_fraud_note(email_body, msg_uid, reopening=False)
            assert result == open_note

            result = bruin_repository._build_fraud_note(email_body, msg_uid, reopening=True)
            assert result == re_open_note

    @pytest.mark.asyncio
    async def change_detail_work_queue__work_queue_changed_test(
        self, bruin_repository, make_change_detail_work_queue_request, bruin_generic_200_response
    ):
        ticket_id = 12345
        target_queue = "Wireless Repair Intervention Needed"
        service_number = "VC1234567"

        request = make_change_detail_work_queue_request(
            request_id=uuid_,
            ticket_id=ticket_id,
            service_number=service_number,
            target_queue=target_queue,
        )

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(bruin_generic_200_response)
        bruin_repository._nats_client.request = AsyncMock(return_value=response_msg)

        with uuid_mock:
            result = await bruin_repository.change_detail_work_queue(
                service_number=service_number, ticket_id=ticket_id, task_result=target_queue
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
        target_queue = "Wireless Repair Intervention Needed"
        service_number = "VC1234567"

        request = make_change_detail_work_queue_request(
            request_id=uuid_,
            ticket_id=ticket_id,
            service_number=service_number,
            target_queue=target_queue,
        )

        bruin_repository._nats_client.request.side_effect = Exception
        bruin_repository._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await bruin_repository.change_detail_work_queue(
                service_number=service_number, ticket_id=ticket_id, task_result=target_queue
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
        target_queue = "Wireless Repair Intervention Needed"
        service_number = "VC1234567"

        request = make_change_detail_work_queue_request(
            request_id=uuid_,
            ticket_id=ticket_id,
            service_number=service_number,
            target_queue=target_queue,
        )

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(bruin_500_response)
        bruin_repository._nats_client.request = AsyncMock(return_value=response_msg)
        bruin_repository._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await bruin_repository.change_detail_work_queue(
                service_number=service_number, ticket_id=ticket_id, task_result=target_queue
            )

        bruin_repository._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.change.work", to_json_bytes(request), timeout=90
        )
        bruin_repository._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == bruin_500_response

    @pytest.mark.asyncio
    async def change_detail_work_queue_to_hnoc_test(self, bruin_repository):
        ticket_id = 12345
        task_result = "HNOC Investigate"
        service_number = "VC1234567"

        await bruin_repository.change_detail_work_queue_to_hnoc(ticket_id=ticket_id, service_number=service_number)

        bruin_repository.change_detail_work_queue.assert_awaited_once_with(
            ticket_id=ticket_id, task_result=task_result, service_number=service_number
        )
