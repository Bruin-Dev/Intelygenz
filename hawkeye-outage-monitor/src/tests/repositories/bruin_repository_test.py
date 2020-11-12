from unittest.mock import Mock
from unittest.mock import patch

import pytest

from asynctest import CoroutineMock
from shortuuid import uuid

from application import nats_error_response
from application.repositories import bruin_repository as bruin_repository_module
from application.repositories.bruin_repository import BruinRepository
from config import testconfig

uuid_ = uuid()
uuid_mock = patch.object(bruin_repository_module, 'uuid', return_value=uuid_)


class TestBruinRepository:
    def instance_test(self):
        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        bruin_repository = BruinRepository(config, logger, event_bus, notifications_repository)

        assert bruin_repository._event_bus is event_bus
        assert bruin_repository._logger is logger
        assert bruin_repository._config is config
        assert bruin_repository._notifications_repository is notifications_repository

    @pytest.mark.asyncio
    async def append_note_to_ticket_test(self):
        ticket_id = 11111
        ticket_note = 'This is a ticket note'

        request = {
            'request_id': uuid_,
            'body': {
                'ticket_id': ticket_id,
                'note': ticket_note,
            },
        }
        response = {
            'request_id': uuid_,
            'body': 'Note appended with success',
            'status': 200,
        }

        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        bruin_repository = BruinRepository(config, logger, event_bus, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.append_note_to_ticket(ticket_id, ticket_note)

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.note.append.request", request, timeout=15)
        assert result == response

    @pytest.mark.asyncio
    async def append_note_to_ticket_with_optional_service_numbers_param_test(self):
        ticket_id = 11111
        ticket_note = 'This is a ticket note'
        service_number = 'B827EB76A8DE'

        request = {
            'request_id': uuid_,
            'body': {
                'ticket_id': ticket_id,
                'note': ticket_note,
                'service_numbers': [service_number],
            },
        }
        response = {
            'request_id': uuid_,
            'body': 'Note appended with success',
            'status': 200,
        }

        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        bruin_repository = BruinRepository(config, logger, event_bus, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.append_note_to_ticket(
                ticket_id, ticket_note, service_numbers=[service_number]
            )

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.note.append.request", request, timeout=15)
        assert result == response

    @pytest.mark.asyncio
    async def append_note_to_ticket_with_rpc_request_failing_test(self):
        ticket_id = 11111
        ticket_note = 'This is a ticket note'

        request = {
            'request_id': uuid_,
            'body': {
                'ticket_id': ticket_id,
                'note': ticket_note,
            },
        }

        logger = Mock()
        config = testconfig

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(side_effect=Exception)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        bruin_repository = BruinRepository(config, logger, event_bus, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.append_note_to_ticket(ticket_id, ticket_note)

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.note.append.request", request, timeout=15)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def append_note_to_ticket_with_rpc_request_returning_non_2xx_status_test(self):
        ticket_id = 11111
        ticket_note = 'This is a ticket note'

        request = {
            'request_id': uuid_,
            'body': {
                'ticket_id': ticket_id,
                'note': ticket_note,
            },
        }
        response = {
            'request_id': uuid_,
            'body': 'Got internal error from Bruin',
            'status': 500,
        }

        logger = Mock()
        config = testconfig

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        bruin_repository = BruinRepository(config, logger, event_bus, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.append_note_to_ticket(ticket_id, ticket_note)

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.note.append.request", request, timeout=15)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == response

    @pytest.mark.asyncio
    async def create_outage_ticket_returning_2xx_status_test(self):
        client_id = 12345
        service_number = 'B827EB76A8DE'

        request = {
            'request_id': uuid_,
            'body': {
                'client_id': client_id,
                'service_number': service_number,
            },
        }
        response = {
            'request_id': uuid_,
            'body': 9999,
            'status': 200,
        }

        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        bruin_repository = BruinRepository(config, logger, event_bus, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.create_outage_ticket(client_id, service_number)

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.creation.outage.request", request, timeout=30)
        assert result == response

    @pytest.mark.asyncio
    async def create_outage_ticket_returning_409_status_test(self):
        client_id = 12345
        service_number = 'B827EB76A8DE'

        request = {
            'request_id': uuid_,
            'body': {
                'client_id': client_id,
                'service_number': service_number,
            },
        }
        response = {
            'request_id': uuid_,
            'body': 9999,
            'status': 409,
        }

        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        bruin_repository = BruinRepository(config, logger, event_bus, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.create_outage_ticket(client_id, service_number)

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.creation.outage.request", request, timeout=30)
        assert result == response

    @pytest.mark.asyncio
    async def create_outage_ticket_returning_471_status_test(self):
        client_id = 12345
        service_number = 'B827EB76A8DE'

        request = {
            'request_id': uuid_,
            'body': {
                'client_id': client_id,
                'service_number': service_number,
            },
        }
        response = {
            'request_id': uuid_,
            'body': 9999,
            'status': 471,
        }

        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        bruin_repository = BruinRepository(config, logger, event_bus, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.create_outage_ticket(client_id, service_number)

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.creation.outage.request", request, timeout=30)
        assert result == response

    @pytest.mark.asyncio
    async def create_outage_ticket_with_rpc_request_failing_test(self):
        client_id = 12345
        service_number = 'B827EB76A8DE'

        request = {
            'request_id': uuid_,
            'body': {
                'client_id': client_id,
                'service_number': service_number,
            },
        }

        logger = Mock()
        config = testconfig

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(side_effect=Exception)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        bruin_repository = BruinRepository(config, logger, event_bus, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.create_outage_ticket(client_id, service_number)

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.creation.outage.request", request, timeout=30)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def create_outage_ticket_with_rpc_request_returning_no_2xx_or_409_or_471_status_test(self):
        client_id = 12345
        service_number = 'B827EB76A8DE'

        request = {
            'request_id': uuid_,
            'body': {
                'client_id': client_id,
                'service_number': service_number,
            },
        }
        response = {
            'request_id': uuid_,
            'body': 'Got internal error from Bruin',
            'status': 500,
        }

        logger = Mock()
        config = testconfig

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        bruin_repository = BruinRepository(config, logger, event_bus, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.create_outage_ticket(client_id, service_number)

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.creation.outage.request", request, timeout=30)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == response

    @pytest.mark.asyncio
    async def append_triage_note_to_ticket_with_less_than_1500_chars_test(self):
        ticket_id = 12345
        service_number = 'B827EB76A8DE'

        note_contents = "XXXX\n" * 200  # 1000 chars
        triage_note = (
            '*Automation Engine*#\n'
            'Triage (Ixia)\n\n'
            f'{note_contents}'
        )

        append_note_response = {
            'body': 'Note appended with success',
            'status': 200,
        }

        logger = Mock()
        config = testconfig
        event_bus = Mock()
        notifications_repository = Mock()

        bruin_repository = BruinRepository(config, logger, event_bus, notifications_repository)
        bruin_repository.append_note_to_ticket = CoroutineMock(return_value=append_note_response)

        result = await bruin_repository.append_triage_note_to_ticket(ticket_id, service_number, triage_note)

        bruin_repository.append_note_to_ticket.assert_awaited_once_with(
            ticket_id,
            triage_note,
            service_numbers=[service_number],
        )
        assert result == append_note_response

    @pytest.mark.asyncio
    async def append_triage_note_to_ticket_with_more_than_1500_chars_and_all_notes_appended_successfully_test(self):
        ticket_id = 12345
        service_number = 'B827EB76A8DE'

        note_contents = "XXXX\n" * 400  # 2000 chars
        triage_note = (
            '*Automation Engine*#\n'
            'Triage (Ixia)\n\n'
            f'{note_contents}'
        )

        append_note_response = {
            'body': 'Note appended with success',
            'status': 200,
        }
        summary_response = {
            'body': f'Triage note split into 3 chunks and appended successfully!',
            'status': 200,
        }

        logger = Mock()
        config = testconfig
        event_bus = Mock()
        notifications_repository = Mock()

        bruin_repository = BruinRepository(config, logger, event_bus, notifications_repository)
        bruin_repository.append_note_to_ticket = CoroutineMock(return_value=append_note_response)

        result = await bruin_repository.append_triage_note_to_ticket(ticket_id, service_number, triage_note)

        assert bruin_repository.append_note_to_ticket.await_count == 3
        assert result == summary_response

    @pytest.mark.asyncio
    async def append_triage_note_to_ticket_with_more_than_1500_chars_and_one_note_append_failing_test(self):
        ticket_id = 12345
        service_number = 'B827EB76A8DE'

        note_contents = "XXXX\n" * 400  # 2000 chars
        triage_note = (
            '*Automation Engine*#\n'
            'Triage (Ixia)\n\n'
            f'{note_contents}'
        )

        append_note_success_response = {
            'body': 'Note appended with success',
            'status': 200,
        }
        append_note_error_response = {
            'body': 'Got internal error from Bruin',
            'status': 500,
        }

        logger = Mock()
        config = testconfig
        event_bus = Mock()
        notifications_repository = Mock()

        bruin_repository = BruinRepository(config, logger, event_bus, notifications_repository)
        bruin_repository.append_note_to_ticket = CoroutineMock(side_effect=[
            append_note_success_response,
            append_note_error_response,
        ])

        result = await bruin_repository.append_triage_note_to_ticket(ticket_id, service_number, triage_note)

        assert bruin_repository.append_note_to_ticket.await_count == 2
        assert result == append_note_error_response
