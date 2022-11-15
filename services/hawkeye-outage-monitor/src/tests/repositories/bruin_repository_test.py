import json
from datetime import datetime
from typing import Any
from unittest.mock import AsyncMock, Mock, patch

import pytest
from application import nats_error_response
from application.repositories import bruin_repository as bruin_repository_module
from application.repositories.bruin_repository import BruinRepository
from config import testconfig
from nats.aio.msg import Msg
from shortuuid import uuid

uuid_ = uuid()
uuid_mock = patch.object(bruin_repository_module, "uuid", return_value=uuid_)


@pytest.fixture(scope="function")
def bruin_repository_instance():
    return BruinRepository(
        nats_client=Mock(),
        config=testconfig,
        notifications_repository=Mock(),
    )


def to_json_bytes(message: dict[str, Any]):
    return json.dumps(message, default=str, separators=(",", ":")).encode()


class TestBruinRepository:
    def instance_test(self, bruin_repository_instance):
        nats_client = Mock()
        config = testconfig
        notifications_repository = Mock()

        bruin_repository = BruinRepository(config, nats_client, notifications_repository)

        assert bruin_repository._nats_client is nats_client
        assert bruin_repository._config is config
        assert bruin_repository._notifications_repository is notifications_repository

    @pytest.mark.asyncio
    async def get_ticket_details_test(self, bruin_repository_instance):
        ticket_id = 11111

        request = {
            "request_id": uuid_,
            "body": {
                "ticket_id": ticket_id,
            },
        }
        response = {
            "request_id": uuid_,
            "body": {
                "ticketDetails": [
                    {
                        "detailID": 2746938,
                        "detailValue": "VC1234567890",
                    },
                ],
                "ticketNotes": [
                    {
                        "noteId": 41894043,
                        "noteValue": f"#*MetTel's IPA*#\nTriage (VeloCloud)\nTimeStamp: 2019-07-30 06:38:00+00:00",
                        "createdDate": "2020-02-24T10:07:13.503-05:00",
                    },
                    {
                        "noteId": 41894044,
                        "noteValue": f"#*MetTel's IPA*#\nTriage (VeloCloud)\nTimeStamp: 2019-07-30 06:38:00+00:00",
                        "createdDate": "2020-02-24T10:07:13.503-05:00",
                    },
                ],
            },
            "status": 200,
        }
        NATS_AIO_MSG = Msg(_client="NATS", data=to_json_bytes(response))
        bruin_repository_instance._nats_client.request = AsyncMock(return_value=NATS_AIO_MSG)

        with uuid_mock:
            result = await bruin_repository_instance.get_ticket_details(ticket_id)

        bruin_repository_instance._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.details.request", to_json_bytes(request), timeout=75
        )
        assert result == response

    @pytest.mark.asyncio
    async def get_ticket_details_with_rpc_request_failing_test(self, bruin_repository_instance):
        ticket_id = 11111

        request = {
            "request_id": uuid_,
            "body": {
                "ticket_id": ticket_id,
            },
        }

        bruin_repository_instance._nats_client.request = AsyncMock(side_effect=Exception)

        bruin_repository_instance._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await bruin_repository_instance.get_ticket_details(ticket_id)

        bruin_repository_instance._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.details.request", to_json_bytes(request), timeout=75
        )
        bruin_repository_instance._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_ticket_details_with_rpc_request_returning_non_2xx_status_test(self, bruin_repository_instance):
        ticket_id = 11111

        request = {
            "request_id": uuid_,
            "body": {
                "ticket_id": ticket_id,
            },
        }
        response = {
            "request_id": uuid_,
            "body": "Got internal error from Bruin",
            "status": 500,
        }
        NATS_AIO_MSG = Msg(_client="NATS", data=to_json_bytes(response))
        bruin_repository_instance._nats_client.request = AsyncMock(return_value=NATS_AIO_MSG)

        bruin_repository_instance._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await bruin_repository_instance.get_ticket_details(ticket_id)

        bruin_repository_instance._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.details.request", to_json_bytes(request), timeout=75
        )
        bruin_repository_instance._notifications_repository.send_slack_message.assert_awaited_once()

        assert result == response

    @pytest.mark.asyncio
    async def append_note_to_ticket_test(self, bruin_repository_instance):
        ticket_id = 11111
        ticket_note = "This is a ticket note"

        request = {
            "request_id": uuid_,
            "body": {
                "ticket_id": ticket_id,
                "note": ticket_note,
            },
        }
        response = {
            "request_id": uuid_,
            "body": "Note appended with success",
            "status": 200,
        }
        NATS_AIO_MSG = Msg(_client="NATS", data=to_json_bytes(response))
        bruin_repository_instance._nats_client.request = AsyncMock(return_value=NATS_AIO_MSG)

        with uuid_mock:
            result = await bruin_repository_instance.append_note_to_ticket(ticket_id, ticket_note)

        bruin_repository_instance._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.note.append.request", to_json_bytes(request), timeout=75
        )
        assert result == response

    @pytest.mark.asyncio
    async def append_note_to_ticket_with_optional_service_numbers_param_test(self, bruin_repository_instance):
        ticket_id = 11111
        ticket_note = "This is a ticket note"
        service_number = "B827EB76A8DE"

        request = {
            "request_id": uuid_,
            "body": {
                "ticket_id": ticket_id,
                "note": ticket_note,
                "service_numbers": [service_number],
            },
        }
        response = {
            "request_id": uuid_,
            "body": "Note appended with success",
            "status": 200,
        }
        NATS_AIO_MSG = Msg(_client="NATS", data=to_json_bytes(response))
        bruin_repository_instance._nats_client.request = AsyncMock(return_value=NATS_AIO_MSG)

        with uuid_mock:
            result = await bruin_repository_instance.append_note_to_ticket(
                ticket_id, ticket_note, service_numbers=[service_number]
            )

        bruin_repository_instance._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.note.append.request", to_json_bytes(request), timeout=75
        )
        assert result == response

    @pytest.mark.asyncio
    async def append_note_to_ticket_with_rpc_request_failing_test(self, bruin_repository_instance):
        ticket_id = 11111
        ticket_note = "This is a ticket note"

        request = {
            "request_id": uuid_,
            "body": {
                "ticket_id": ticket_id,
                "note": ticket_note,
            },
        }

        bruin_repository_instance._nats_client.request = AsyncMock(side_effect=Exception)

        bruin_repository_instance._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await bruin_repository_instance.append_note_to_ticket(ticket_id, ticket_note)

        bruin_repository_instance._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.note.append.request", to_json_bytes(request), timeout=75
        )
        bruin_repository_instance._notifications_repository.send_slack_message.assert_awaited_once()

        assert result == nats_error_response

    @pytest.mark.asyncio
    async def append_note_to_ticket_with_rpc_request_returning_non_2xx_status_test(self, bruin_repository_instance):
        ticket_id = 11111
        ticket_note = "This is a ticket note"

        request = {
            "request_id": uuid_,
            "body": {
                "ticket_id": ticket_id,
                "note": ticket_note,
            },
        }
        response = {
            "request_id": uuid_,
            "body": "Got internal error from Bruin",
            "status": 500,
        }
        NATS_AIO_MSG = Msg(_client="NATS", data=to_json_bytes(response))
        bruin_repository_instance._nats_client.request = AsyncMock(return_value=NATS_AIO_MSG)

        bruin_repository_instance._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await bruin_repository_instance.append_note_to_ticket(ticket_id, ticket_note)

        bruin_repository_instance._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.note.append.request", to_json_bytes(request), timeout=75
        )
        bruin_repository_instance._notifications_repository.send_slack_message.assert_awaited_once()

        assert result == response

    @pytest.mark.asyncio
    async def create_outage_ticket_returning_2xx_status_test(self, bruin_repository_instance):
        client_id = 12345
        service_number = "B827EB76A8DE"

        request = {
            "request_id": uuid_,
            "body": {
                "client_id": client_id,
                "service_number": service_number,
            },
        }
        response = {
            "request_id": uuid_,
            "body": 9999,
            "status": 200,
        }
        NATS_AIO_MSG = Msg(_client="NATS", data=to_json_bytes(response))
        bruin_repository_instance._nats_client.request = AsyncMock(return_value=NATS_AIO_MSG)

        with uuid_mock:
            result = await bruin_repository_instance.create_outage_ticket(client_id, service_number)

        bruin_repository_instance._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.creation.outage.request", to_json_bytes(request), timeout=90
        )
        assert result == response

    @pytest.mark.asyncio
    async def create_outage_ticket_returning_409_status_test(self, bruin_repository_instance):
        client_id = 12345
        service_number = "B827EB76A8DE"

        request = {
            "request_id": uuid_,
            "body": {
                "client_id": client_id,
                "service_number": service_number,
            },
        }
        response = {
            "request_id": uuid_,
            "body": 9999,
            "status": 409,
        }
        NATS_AIO_MSG = Msg(_client="NATS", data=to_json_bytes(response))
        bruin_repository_instance._nats_client.request = AsyncMock(return_value=NATS_AIO_MSG)

        with uuid_mock:
            result = await bruin_repository_instance.create_outage_ticket(client_id, service_number)

        bruin_repository_instance._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.creation.outage.request", to_json_bytes(request), timeout=90
        )
        assert result == response

    @pytest.mark.asyncio
    async def create_outage_ticket_returning_471_status_test(self, bruin_repository_instance):
        client_id = 12345
        service_number = "B827EB76A8DE"

        request = {
            "request_id": uuid_,
            "body": {
                "client_id": client_id,
                "service_number": service_number,
            },
        }
        response = {
            "request_id": uuid_,
            "body": 9999,
            "status": 471,
        }
        NATS_AIO_MSG = Msg(_client="NATS", data=to_json_bytes(response))
        bruin_repository_instance._nats_client.request = AsyncMock(return_value=NATS_AIO_MSG)

        with uuid_mock:
            result = await bruin_repository_instance.create_outage_ticket(client_id, service_number)

        bruin_repository_instance._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.creation.outage.request", to_json_bytes(request), timeout=90
        )
        assert result == response

    @pytest.mark.asyncio
    async def create_outage_ticket_with_rpc_request_failing_test(self, bruin_repository_instance):
        client_id = 12345
        service_number = "B827EB76A8DE"

        request = {
            "request_id": uuid_,
            "body": {
                "client_id": client_id,
                "service_number": service_number,
            },
        }

        bruin_repository_instance._nats_client.request = AsyncMock(side_effect=Exception)

        bruin_repository_instance._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await bruin_repository_instance.create_outage_ticket(client_id, service_number)

        bruin_repository_instance._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.creation.outage.request", to_json_bytes(request), timeout=90
        )
        bruin_repository_instance._notifications_repository.send_slack_message.assert_awaited_once()

        assert result == nats_error_response

    @pytest.mark.asyncio
    async def create_outage_ticket_with_rpc_request_returning_no_2xx_or_409_or_471_status_test(
        self, bruin_repository_instance
    ):
        client_id = 12345
        service_number = "B827EB76A8DE"

        request = {
            "request_id": uuid_,
            "body": {
                "client_id": client_id,
                "service_number": service_number,
            },
        }
        response = {
            "request_id": uuid_,
            "body": "Got internal error from Bruin",
            "status": 500,
        }
        NATS_AIO_MSG = Msg(_client="NATS", data=to_json_bytes(response))
        bruin_repository_instance._nats_client.request = AsyncMock(return_value=NATS_AIO_MSG)

        bruin_repository_instance._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await bruin_repository_instance.create_outage_ticket(client_id, service_number)

        bruin_repository_instance._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.creation.outage.request", to_json_bytes(request), timeout=90
        )
        bruin_repository_instance._notifications_repository.send_slack_message.assert_awaited_once()

        assert result == response

    @pytest.mark.asyncio
    async def append_triage_note_to_ticket_with_less_than_1500_chars_test(self, bruin_repository_instance):
        ticket_id = 12345
        service_number = "B827EB76A8DE"

        note_contents = "XXXX\n" * 200  # 1000 chars
        triage_note = "*MetTel's IPA*#\n" "Triage (Ixia)\n\n{note_contents}"

        append_note_response = {
            "body": "Note appended with success",
            "status": 200,
        }

        bruin_repository_instance.append_note_to_ticket = AsyncMock(return_value=append_note_response)

        result = await bruin_repository_instance.append_triage_note_to_ticket(ticket_id, service_number, triage_note)

        bruin_repository_instance.append_note_to_ticket.assert_awaited_once_with(
            ticket_id,
            triage_note,
            service_numbers=[service_number],
        )
        assert result == append_note_response

    @pytest.mark.asyncio
    async def append_triage_note_to_ticket_with_more_than_1500_chars_and_all_notes_appended_successfully_test(
        self, bruin_repository_instance
    ):
        ticket_id = 12345
        service_number = "B827EB76A8DE"

        note_contents = "XXXX\n" * 400  # 2000 chars
        triage_note = f"*MetTel's IPA*#\nTriage (Ixia)\n\n{note_contents}"

        append_note_response = {
            "body": "Note appended with success",
            "status": 200,
        }
        summary_response = {
            "body": f"Triage note split into 3 chunks and appended successfully!",
            "status": 200,
        }

        bruin_repository_instance.append_note_to_ticket = AsyncMock(return_value=append_note_response)

        result = await bruin_repository_instance.append_triage_note_to_ticket(ticket_id, service_number, triage_note)

        assert bruin_repository_instance.append_note_to_ticket.await_count == 3
        assert result == summary_response

    @pytest.mark.asyncio
    async def append_triage_note_to_ticket_with_more_than_1500_chars_and_one_note_append_failing_test(
        self, bruin_repository_instance
    ):
        ticket_id = 12345
        service_number = "B827EB76A8DE"

        note_contents = "XXXX\n" * 400  # 2000 chars
        triage_note = f"*MetTel's IPA*#\nTriage (Ixia)\n\n{note_contents}"

        append_note_success_response = {
            "body": "Note appended with success",
            "status": 200,
        }
        append_note_error_response = {
            "body": "Got internal error from Bruin",
            "status": 500,
        }

        bruin_repository_instance.append_note_to_ticket = AsyncMock(
            side_effect=[
                append_note_success_response,
                append_note_error_response,
            ]
        )

        result = await bruin_repository_instance.append_triage_note_to_ticket(ticket_id, service_number, triage_note)

        assert bruin_repository_instance.append_note_to_ticket.await_count == 2
        assert result == append_note_error_response

    @pytest.mark.asyncio
    async def get_tickets_with_no_service_number_specified_test(self, bruin_repository_instance):
        bruin_client_id = 12345
        ticket_statuses = ["New", "InProgress", "Draft"]
        ticket_topic = "VAS"

        request = {
            "request_id": uuid_,
            "body": {
                "client_id": bruin_client_id,
                "ticket_statuses": ticket_statuses,
                "ticket_topic": ticket_topic,
                "product_category": "Network Scout",
            },
        }
        response = {
            "request_id": uuid_,
            "body": [
                {"ticketID": 11111},
                {"ticketID": 22222},
            ],
            "status": 200,
        }
        NATS_AIO_MSG = Msg(_client="NATS", data=to_json_bytes(response))
        bruin_repository_instance._nats_client.request = AsyncMock(return_value=NATS_AIO_MSG)

        with uuid_mock:
            result = await bruin_repository_instance.get_tickets(bruin_client_id, ticket_topic, ticket_statuses)

        bruin_repository_instance._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.basic.request", to_json_bytes(request), timeout=150
        )
        assert result == response

    @pytest.mark.asyncio
    async def get_tickets_with_service_number_specified_test(self, bruin_repository_instance):
        bruin_client_id = 12345
        service_number = "VC1234567"
        ticket_statuses = ["New", "InProgress", "Draft"]
        ticket_topic = "VAS"

        request = {
            "request_id": uuid_,
            "body": {
                "client_id": bruin_client_id,
                "ticket_statuses": ticket_statuses,
                "ticket_topic": ticket_topic,
                "product_category": "Network Scout",
                "service_number": service_number,
            },
        }
        response = {
            "request_id": uuid_,
            "body": [
                {"ticketID": 11111},
                {"ticketID": 22222},
            ],
            "status": 200,
        }
        NATS_AIO_MSG = Msg(_client="NATS", data=to_json_bytes(response))
        bruin_repository_instance._nats_client.request = AsyncMock(return_value=NATS_AIO_MSG)

        with uuid_mock:
            result = await bruin_repository_instance.get_tickets(
                bruin_client_id, ticket_topic, ticket_statuses, service_number=service_number
            )

        bruin_repository_instance._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.basic.request", to_json_bytes(request), timeout=150
        )
        assert result == response

    @pytest.mark.asyncio
    async def get_tickets_with_rpc_request_failing_test(self, bruin_repository_instance):
        bruin_client_id = 12345
        ticket_statuses = ["New", "InProgress", "Draft"]
        ticket_topic = "VAS"

        request = {
            "request_id": uuid_,
            "body": {
                "client_id": bruin_client_id,
                "ticket_statuses": ticket_statuses,
                "ticket_topic": ticket_topic,
                "product_category": "Network Scout",
            },
        }

        bruin_repository_instance._nats_client.request = AsyncMock(side_effect=Exception)

        bruin_repository_instance._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await bruin_repository_instance.get_tickets(bruin_client_id, ticket_topic, ticket_statuses)

        bruin_repository_instance._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.basic.request", to_json_bytes(request), timeout=150
        )
        bruin_repository_instance._notifications_repository.send_slack_message.assert_awaited_once()

        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_tickets_with_rpc_request_returning_non_2xx_status_test(self, bruin_repository_instance):
        bruin_client_id = 12345
        ticket_statuses = ["New", "InProgress", "Draft"]
        ticket_topic = "VAS"

        request = {
            "request_id": uuid_,
            "body": {
                "client_id": bruin_client_id,
                "ticket_statuses": ticket_statuses,
                "ticket_topic": ticket_topic,
                "product_category": "Network Scout",
            },
        }
        response = {
            "request_id": uuid_,
            "body": "Got internal error from Bruin",
            "status": 500,
        }
        NATS_AIO_MSG = Msg(_client="NATS", data=to_json_bytes(response))
        bruin_repository_instance._nats_client.request = AsyncMock(return_value=NATS_AIO_MSG)

        bruin_repository_instance._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await bruin_repository_instance.get_tickets(bruin_client_id, ticket_topic, ticket_statuses)

        bruin_repository_instance._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.basic.request", to_json_bytes(request), timeout=150
        )
        bruin_repository_instance._notifications_repository.send_slack_message.assert_awaited_once()

        assert result == response

    @pytest.mark.asyncio
    async def resolve_ticket_test(self, bruin_repository_instance):
        ticket_id = 12345
        detail_id = 67890

        request = {
            "request_id": uuid_,
            "body": {
                "ticket_id": ticket_id,
                "detail_id": detail_id,
            },
        }
        response = {
            "request_id": uuid_,
            "body": "ok",
            "status": 200,
        }
        NATS_AIO_MSG = Msg(_client="NATS", data=to_json_bytes(response))
        bruin_repository_instance._nats_client.request = AsyncMock(return_value=NATS_AIO_MSG)

        with uuid_mock:
            result = await bruin_repository_instance.resolve_ticket(ticket_id, detail_id)

        bruin_repository_instance._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.status.resolve", to_json_bytes(request), timeout=75
        )
        assert result == response

    @pytest.mark.asyncio
    async def resolve_ticket_with_rpc_request_failing_test(self, bruin_repository_instance):
        ticket_id = 12345
        detail_id = 67890

        request = {
            "request_id": uuid_,
            "body": {
                "ticket_id": ticket_id,
                "detail_id": detail_id,
            },
        }

        bruin_repository_instance._nats_client.request = AsyncMock(side_effect=Exception)

        bruin_repository_instance._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await bruin_repository_instance.resolve_ticket(ticket_id, detail_id)

        bruin_repository_instance._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.status.resolve", to_json_bytes(request), timeout=75
        )
        bruin_repository_instance._notifications_repository.send_slack_message.assert_awaited_once()

        assert result == nats_error_response

    @pytest.mark.asyncio
    async def resolve_ticket_with_rpc_request_returning_non_2xx_status_test(self, bruin_repository_instance):
        ticket_id = 12345
        detail_id = 67890

        request = {
            "request_id": uuid_,
            "body": {
                "ticket_id": ticket_id,
                "detail_id": detail_id,
            },
        }
        response = {
            "request_id": uuid_,
            "body": "Got internal error from Bruin",
            "status": 500,
        }
        NATS_AIO_MSG = Msg(_client="NATS", data=to_json_bytes(response))
        bruin_repository_instance._nats_client.request = AsyncMock(return_value=NATS_AIO_MSG)

        bruin_repository_instance._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await bruin_repository_instance.resolve_ticket(ticket_id, detail_id)

        bruin_repository_instance._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.status.resolve", to_json_bytes(request), timeout=75
        )
        bruin_repository_instance._notifications_repository.send_slack_message.assert_awaited_once()

        assert result == response

    @pytest.mark.asyncio
    async def unpause_ticket_detail_with_only_detail_id_specified_test(self, bruin_repository_instance):
        ticket_id = 12345
        detail_id = 67890

        request = {
            "request_id": uuid_,
            "body": {
                "ticket_id": ticket_id,
                "detail_id": detail_id,
            },
        }
        response = {
            "request_id": uuid_,
            "body": "ok",
            "status": 200,
        }
        NATS_AIO_MSG = Msg(_client="NATS", data=to_json_bytes(response))
        bruin_repository_instance._nats_client.request = AsyncMock(return_value=NATS_AIO_MSG)

        with uuid_mock:
            result = await bruin_repository_instance.unpause_ticket_detail(ticket_id, detail_id=detail_id)

        bruin_repository_instance._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.unpause", to_json_bytes(request), timeout=90
        )
        assert result == response

    @pytest.mark.asyncio
    async def unpause_ticket_detail_with_only_service_number_specified_test(self, bruin_repository_instance):
        ticket_id = 12345
        service_number = "VC1234567"

        request = {
            "request_id": uuid_,
            "body": {
                "ticket_id": ticket_id,
                "service_number": service_number,
            },
        }
        response = {
            "request_id": uuid_,
            "body": "ok",
            "status": 200,
        }
        NATS_AIO_MSG = Msg(_client="NATS", data=to_json_bytes(response))
        bruin_repository_instance._nats_client.request = AsyncMock(return_value=NATS_AIO_MSG)

        with uuid_mock:
            result = await bruin_repository_instance.unpause_ticket_detail(ticket_id, service_number=service_number)

        bruin_repository_instance._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.unpause", to_json_bytes(request), timeout=90
        )
        assert result == response

    @pytest.mark.asyncio
    async def unpause_ticket_detail_with_detail_id_and_service_number_specified_test(self, bruin_repository_instance):
        ticket_id = 12345
        detail_id = 67890
        service_number = "VC1234567"

        request = {
            "request_id": uuid_,
            "body": {
                "ticket_id": ticket_id,
                "detail_id": detail_id,
                "service_number": service_number,
            },
        }
        response = {
            "request_id": uuid_,
            "body": "ok",
            "status": 200,
        }
        NATS_AIO_MSG = Msg(_client="NATS", data=to_json_bytes(response))
        bruin_repository_instance._nats_client.request = AsyncMock(return_value=NATS_AIO_MSG)

        with uuid_mock:
            result = await bruin_repository_instance.unpause_ticket_detail(
                ticket_id, detail_id=detail_id, service_number=service_number
            )

        bruin_repository_instance._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.unpause", to_json_bytes(request), timeout=90
        )
        assert result == response

    @pytest.mark.asyncio
    async def unpause_ticket_detail_with_rpc_request_failing_test(self, bruin_repository_instance):
        ticket_id = 12345
        detail_id = 67890

        request = {
            "request_id": uuid_,
            "body": {
                "ticket_id": ticket_id,
                "detail_id": detail_id,
            },
        }

        bruin_repository_instance._nats_client.request = AsyncMock(side_effect=Exception)

        bruin_repository_instance._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await bruin_repository_instance.unpause_ticket_detail(ticket_id, detail_id=detail_id)

        bruin_repository_instance._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.unpause", to_json_bytes(request), timeout=90
        )
        bruin_repository_instance._notifications_repository.send_slack_message.assert_awaited_once()

        assert result == nats_error_response

    @pytest.mark.asyncio
    async def unpause_ticket_detail_with_rpc_request_returning_non_2xx_status_test(self, bruin_repository_instance):
        ticket_id = 12345
        detail_id = 67890

        request = {
            "request_id": uuid_,
            "body": {
                "ticket_id": ticket_id,
                "detail_id": detail_id,
            },
        }
        response = {
            "request_id": uuid_,
            "body": "Got internal error from Bruin",
            "status": 500,
        }
        NATS_AIO_MSG = Msg(_client="NATS", data=to_json_bytes(response))
        bruin_repository_instance._nats_client.request = AsyncMock(return_value=NATS_AIO_MSG)

        bruin_repository_instance._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await bruin_repository_instance.unpause_ticket_detail(ticket_id, detail_id=detail_id)

        bruin_repository_instance._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.unpause", to_json_bytes(request), timeout=90
        )
        bruin_repository_instance._notifications_repository.send_slack_message.assert_awaited_once()

        assert result == response

    @pytest.mark.asyncio
    async def get_open_outage_tickets_with_no_service_number_specified_test(self, bruin_repository_instance):
        bruin_client_id = 12345
        ticket_statuses = ["New", "InProgress", "Draft"]

        bruin_repository_instance.get_outage_tickets = AsyncMock()

        with uuid_mock:
            await bruin_repository_instance.get_open_outage_tickets(bruin_client_id)

        bruin_repository_instance.get_outage_tickets.assert_awaited_once_with(
            bruin_client_id, ticket_statuses, service_number=None
        )

    @pytest.mark.asyncio
    async def get_open_outage_tickets_test(self, bruin_repository_instance):
        bruin_client_id = 12345
        service_number = "VC1234567"
        ticket_statuses = ["New", "InProgress", "Draft"]

        bruin_repository_instance.get_outage_tickets = AsyncMock()

        with uuid_mock:
            await bruin_repository_instance.get_open_outage_tickets(bruin_client_id, service_number=service_number)

        bruin_repository_instance.get_outage_tickets.assert_awaited_once_with(
            bruin_client_id, ticket_statuses, service_number=service_number
        )

    @pytest.mark.asyncio
    async def get_outage_tickets_with_no_service_number_specified_test(self, bruin_repository_instance):
        bruin_client_id = 12345
        ticket_statuses = ["New", "InProgress", "Draft"]
        ticket_topic = "VOO"

        bruin_repository_instance.get_tickets = AsyncMock()

        with uuid_mock:
            await bruin_repository_instance.get_outage_tickets(bruin_client_id, ticket_statuses)

        bruin_repository_instance.get_tickets.assert_awaited_once_with(
            bruin_client_id, ticket_topic, ticket_statuses, service_number=None
        )

    @pytest.mark.asyncio
    async def get_outage_tickets_test(self, bruin_repository_instance):
        bruin_client_id = 12345
        service_number = "VC1234567"
        ticket_statuses = ["New", "InProgress", "Draft"]
        ticket_topic = "VOO"

        bruin_repository_instance.get_tickets = AsyncMock()

        await bruin_repository_instance.get_outage_tickets(
            bruin_client_id, ticket_statuses, service_number=service_number
        )

        bruin_repository_instance.get_tickets.assert_awaited_once_with(
            bruin_client_id, ticket_topic, ticket_statuses, service_number=service_number
        )

    @pytest.mark.asyncio
    async def append_autoresolve_note_to_ticket_test(self, bruin_repository_instance):
        serial_number = "VC1234567"

        current_datetime = datetime.now()
        ticket_id = 11111
        ticket_note = (
            "#*MetTel's IPA*#\n"
            f"Auto-resolving detail for serial: {serial_number}\n"
            f"Real service status is UP.\n"
            f"Node to node status is UP.\n"
            f"TimeStamp: {current_datetime}"
        )

        response = {
            "request_id": uuid_,
            "body": "Note appended with success",
            "status": 200,
        }

        bruin_repository_instance.append_note_to_ticket = AsyncMock(return_value=response)

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)
        with patch.object(bruin_repository_module, "datetime", new=datetime_mock):
            with patch.object(bruin_repository_module, "timezone", new=Mock()):
                result = await bruin_repository_instance.append_autoresolve_note_to_ticket(ticket_id, serial_number)

        bruin_repository_instance.append_note_to_ticket.assert_awaited_once_with(
            ticket_id, ticket_note, service_numbers=[serial_number]
        )
        assert result == response

    @pytest.mark.asyncio
    async def open_ticket_test(self, bruin_repository_instance):
        ticket_id = 12345
        detail_id = 67890

        request = {
            "request_id": uuid_,
            "body": {
                "ticket_id": ticket_id,
                "detail_id": detail_id,
            },
        }
        response = {
            "request_id": uuid_,
            "body": "ok",
            "status": 200,
        }
        NATS_AIO_MSG = Msg(_client="NATS", data=to_json_bytes(response))
        bruin_repository_instance._nats_client.request = AsyncMock(return_value=NATS_AIO_MSG)

        with uuid_mock:
            result = await bruin_repository_instance.open_ticket(ticket_id, detail_id)

        bruin_repository_instance._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.status.open", to_json_bytes(request), timeout=75
        )
        assert result == response

    @pytest.mark.asyncio
    async def open_ticket_with_rpc_request_failing_test(self, bruin_repository_instance):
        ticket_id = 12345
        detail_id = 67890

        request = {
            "request_id": uuid_,
            "body": {
                "ticket_id": ticket_id,
                "detail_id": detail_id,
            },
        }

        bruin_repository_instance._nats_client.request = AsyncMock(side_effect=Exception)

        bruin_repository_instance._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await bruin_repository_instance.open_ticket(ticket_id, detail_id)

        bruin_repository_instance._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.status.open", to_json_bytes(request), timeout=75
        )
        bruin_repository_instance._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def open_ticket_with_rpc_request_returning_non_2xx_status_test(self, bruin_repository_instance):
        ticket_id = 12345
        detail_id = 67890

        request = {
            "request_id": uuid_,
            "body": {
                "ticket_id": ticket_id,
                "detail_id": detail_id,
            },
        }
        response = {
            "request_id": uuid_,
            "body": "Got internal error from Bruin",
            "status": 500,
        }
        NATS_AIO_MSG = Msg(_client="NATS", data=to_json_bytes(response))
        bruin_repository_instance._nats_client.request = AsyncMock(return_value=NATS_AIO_MSG)

        bruin_repository_instance._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await bruin_repository_instance.open_ticket(ticket_id, detail_id)

        bruin_repository_instance._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.status.open", to_json_bytes(request), timeout=75
        )
        bruin_repository_instance._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == response

    @pytest.mark.asyncio
    async def create_outage_ticket_returning_472_status_test(self, bruin_repository_instance):
        client_id = 12345
        service_number = "VC1234567"

        request = {
            "request_id": uuid_,
            "body": {
                "client_id": client_id,
                "service_number": service_number,
            },
        }
        response = {
            "request_id": uuid_,
            "body": 9999,
            "status": 472,
        }
        NATS_AIO_MSG = Msg(_client="NATS", data=to_json_bytes(response))
        bruin_repository_instance._nats_client.request = AsyncMock(return_value=NATS_AIO_MSG)

        with uuid_mock:
            result = await bruin_repository_instance.create_outage_ticket(client_id, service_number)

        bruin_repository_instance._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.creation.outage.request", to_json_bytes(request), timeout=90
        )
        assert result == response

    @pytest.mark.asyncio
    async def create_outage_ticket_returning_473_status_test(self, bruin_repository_instance):
        client_id = 12345
        service_number = "VC1234567"

        request = {
            "request_id": uuid_,
            "body": {
                "client_id": client_id,
                "service_number": service_number,
            },
        }
        response = {
            "request_id": uuid_,
            "body": 9999,
            "status": 473,
        }
        NATS_AIO_MSG = Msg(_client="NATS", data=to_json_bytes(response))
        bruin_repository_instance._nats_client.request = AsyncMock(return_value=NATS_AIO_MSG)

        with uuid_mock:
            result = await bruin_repository_instance.create_outage_ticket(client_id, service_number)

        bruin_repository_instance._nats_client.request.assert_awaited_once_with(
            "bruin.ticket.creation.outage.request", to_json_bytes(request), timeout=90
        )
        assert result == response
