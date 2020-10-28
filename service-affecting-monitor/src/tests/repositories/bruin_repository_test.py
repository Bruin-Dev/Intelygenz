from datetime import datetime
from unittest.mock import Mock
from unittest.mock import patch

import pytest

from asynctest import CoroutineMock
from shortuuid import uuid

from application.repositories import bruin_repository as bruin_repository_module
from application.repositories import nats_error_response
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

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)

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

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.append_note_to_ticket(ticket_id, ticket_note)

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

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)

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
        config.MONITOR_CONFIG['environment'] = 'dev'

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.append_note_to_ticket(ticket_id, ticket_note)

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.note.append.request", request, timeout=15)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == response

    @pytest.mark.asyncio
    async def open_ticket_test(self):
        ticket_id = 12345
        detail_id = 67890

        request = {
            'request_id': uuid_,
            'body': {
                'ticket_id': ticket_id,
                'detail_id': detail_id,
            },
        }
        response = {
            'request_id': uuid_,
            'body': 'ok',
            'status': 200,
        }

        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.open_ticket(ticket_id, detail_id)

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.status.open", request, timeout=15)
        assert result == response

    @pytest.mark.asyncio
    async def open_ticket_with_rpc_request_failing_test(self):
        ticket_id = 12345
        detail_id = 67890

        request = {
            'request_id': uuid_,
            'body': {
                'ticket_id': ticket_id,
                'detail_id': detail_id,
            },
        }

        logger = Mock()
        config = testconfig

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(side_effect=Exception)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.open_ticket(ticket_id, detail_id)

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.status.open", request, timeout=15)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def open_ticket_with_rpc_request_returning_non_2xx_status_test(self):
        ticket_id = 12345
        detail_id = 67890

        request = {
            'request_id': uuid_,
            'body': {
                'ticket_id': ticket_id,
                'detail_id': detail_id,
            },
        }
        response = {
            'request_id': uuid_,
            'body': 'Got internal error from Bruin',
            'status': 500,
        }

        logger = Mock()
        config = testconfig
        config.MONITOR_CONFIG['environment'] = 'dev'

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.open_ticket(ticket_id, detail_id)

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.status.open", request, timeout=15)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == response

    @pytest.mark.asyncio
    async def append_reopening_note_to_ticket_test(self):
        current_datetime = datetime.now()
        ticket_id = 11111
        outage_causes = "Some causes of the outage"
        ticket_note = (
            '#*Automation Engine*#\n'
            f'Re-opening ticket.\n'
            f'{outage_causes}\n'
            f'TimeStamp: {current_datetime}'
        )

        response = {
            'request_id': uuid_,
            'body': 'Note appended with success',
            'status': 200,
        }

        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)
        bruin_repository.append_note_to_ticket = CoroutineMock(return_value=response)

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)
        with patch.object(bruin_repository_module, 'datetime', new=datetime_mock):
            with patch.object(bruin_repository_module, 'timezone', new=Mock()):
                result = await bruin_repository.append_reopening_note_to_ticket(ticket_id, outage_causes)

        bruin_repository.append_note_to_ticket.assert_awaited_once_with(ticket_id, ticket_note)
        assert result == response

    def find_detail_by_serial_test(self):
        edge_serial_number = 'VC05200028729'

        ticket_details = [{"detailID": 5217537, "detailValue": 'VC05200028729', "detailStatus": "R"}]
        ticket_mock = {
            "ticketID": 3521039,
            "ticketDetails": ticket_details,
            "ticketNotes": [
                {
                    "noteValue": '#*Automation Engine*# \n '
                                 'Trouble: LATENCY\n '
                                 'TimeStamp: 2019-09-10 10:34:00-04:00 ',
                    'createdDate': '2019-09-10 10:34:00-04:00'
                }
            ]
        }
        response = BruinRepository.find_detail_by_serial(ticket_mock, edge_serial_number)
        assert response == ticket_details[0]

        ticket_details = [{"detailID": 5217537, "detailValue": 'NOT_FOUND', "detailStatus": "R"}]
        ticket_mock = {
            "ticketID": 3521039,
            "ticketDetails": ticket_details,
            "ticketNotes": [
                {
                    "noteValue": '#*Automation Engine*# \n '
                                 'Trouble: LATENCY\n '
                                 'TimeStamp: 2019-09-10 10:34:00-04:00 ',
                    'createdDate': '2019-09-10 10:34:00-04:00'
                }
            ]
        }
        response = BruinRepository.find_detail_by_serial(ticket_mock, edge_serial_number)
        assert response is None

    @pytest.mark.asyncio
    async def get_affecting_ticket_by_trouble_ok_test(self):
        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)
        affecting_ticket_mock = {
            "ticketID": 3521039,
            "ticketDetails": [{"detailID": 5217537, "detailValue": 'VC05200026138'}],
            "ticketNotes": [
                {
                    "noteValue": '#*Automation Engine*# \n '
                                 'Trouble: LATENCY\n '
                                 'TimeStamp: 2019-09-10 10:34:00-04:00 ',
                    'createdDate': '2019-09-10 10:34:00-04:00'
                }
            ]
        }
        ticket_list = {
                        'body': [{'ticketID': 3521039}],
                        'status': 200
        }
        ticket_details = {
            'body': affecting_ticket_mock,
            'status': 200
        }
        event_bus.rpc_request = CoroutineMock(side_effect=[ticket_list, ticket_details])

        affecting_ticket = await bruin_repository.get_affecting_ticket(85940, 'VC05200026138')
        assert affecting_ticket == ticket_details['body']
        assert event_bus.rpc_request.called

    @pytest.mark.asyncio
    async def get_affecting_ticket_by_trouble_error_get_tickets_details_test(self):
        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)

        ticket_list = {
                        'body': [{'ticketID': 3521039}],
                        'status': 200
        }
        ticket_details = {
            'body': 'ERROR',
            'status': 400
        }
        event_bus.rpc_request = CoroutineMock(side_effect=[ticket_list, ticket_details])

        affecting_ticket = await bruin_repository.get_affecting_ticket(85940, 'VC05200026138')
        assert affecting_ticket is None
        assert event_bus.rpc_request.called

    @pytest.mark.asyncio
    async def get_affecting_ticket_by_trouble_error_get_tickets_test(self):
        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)
        ticket_list = {
            'body': None,
            'status': 400
        }
        event_bus.rpc_request = CoroutineMock(side_effect=[ticket_list])

        affecting_ticket = await bruin_repository.get_affecting_ticket(85940, 'VC05200026138')
        assert affecting_ticket is None
        assert event_bus.rpc_request.called

    @pytest.mark.asyncio
    async def get_affecting_ticket_by_trouble_no_tickets_test(self):
        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)

        ticket_list = {
            'body': [],
            'status': 200
        }
        event_bus.rpc_request = CoroutineMock(side_effect=[ticket_list])

        affecting_ticket = await bruin_repository.get_affecting_ticket(85940, 'VC05200026138')

        assert affecting_ticket is None
        assert event_bus.rpc_request.called
