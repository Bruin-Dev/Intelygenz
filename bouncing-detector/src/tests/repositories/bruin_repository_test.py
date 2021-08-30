from datetime import datetime
from unittest.mock import Mock
from unittest.mock import patch, call

import asyncio
import pytest
from asynctest import CoroutineMock
from shortuuid import uuid

from application.repositories import bruin_repository as bruin_repository_module
from application.repositories import nats_error_response
from application.repositories import notifications_repository as notifications_repository_module
from application.repositories.bruin_repository import BruinRepository
from config import testconfig

uuid_ = uuid()
uuid_mock = patch.object(bruin_repository_module, 'uuid', return_value=uuid_)
uuid_2_mock = patch.object(notifications_repository_module, 'uuid', return_value=uuid_)


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
    async def get_affecting_ticket_test(self):
        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)
        ticket_statuses = ['New', 'InProgress', 'Draft', 'Resolved']
        client_id = 85940
        serial = 'VC05200026138'
        ticket_request_msg = {
            'request_id': uuid_,
            'body': {
                'client_id': client_id,
                'product_category': 'SD-WAN',
                'ticket_topic': 'VAS',
                'service_number': serial,
                'ticket_statuses': ticket_statuses
            }
        }
        ticket_details_request = {'request_id': uuid_, 'body': {'ticket_id': 3521039}}

        affecting_ticket_mock = {
            "ticketID": 3521039,
            "ticketDetails": [{"detailID": 5217537, "detailValue": 'VC05200026138'}],
            "ticketNotes": [
                {
                    "noteValue": "#*MetTel's IPA*# \n "
                                 'Trouble: LATENCY\n '
                                 'TimeStamp: 2019-09-10 10:34:00-04:00 ',
                    'createdDate': '2019-09-10 10:34:00-04:00'
                }
            ]
        }
        ticket_list = {
            'body': [{'ticketID': 3521038, "createDate": "11/9/2020 2:15:36 AM"},
                     {'ticketID': 3521039, "createDate": "11/9/2020 3:15:36 AM"}],
            'status': 200
        }
        ticket_details = {
            'body': affecting_ticket_mock,
            'status': 200
        }
        event_bus.rpc_request = CoroutineMock(side_effect=[ticket_list, ticket_details])

        with uuid_mock:
            affecting_ticket = await bruin_repository.get_affecting_ticket(client_id, serial)

        event_bus.rpc_request.assert_has_awaits([
            call("bruin.ticket.basic.request", ticket_request_msg, timeout=90),
            call("bruin.ticket.details.request", ticket_details_request, timeout=15)
        ])
        assert affecting_ticket == ticket_details['body']
        assert event_bus.rpc_request.called

    @pytest.mark.asyncio
    async def get_affecting_ticket_error_get_tickets_details_test(self):
        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)
        bruin_repository._notifications_repository.send_slack_message = CoroutineMock()

        ticket_list = {
            'body': [{'ticketID': 3521038, "createDate": "11/9/2020 2:15:36 AM"},
                     {'ticketID': 3521039, "createDate": "11/9/2020 3:15:36 AM"}],
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
    async def get_affecting_ticket_exception_get_tickets_details_test(self):
        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)
        bruin_repository._notifications_repository.send_slack_message = CoroutineMock()

        ticket_list = {
            'body': [{'ticketID': 3521038, "createDate": "11/9/2020 2:15:36 AM"},
                     {'ticketID': 3521039, "createDate": "11/9/2020 3:15:36 AM"}],
            'status': 200
        }

        event_bus.rpc_request = CoroutineMock(side_effect=[ticket_list, Exception])

        affecting_ticket = await bruin_repository.get_affecting_ticket(85940, 'VC05200026138')
        assert affecting_ticket is None
        assert event_bus.rpc_request.called

    @pytest.mark.asyncio
    async def get_affecting_ticket_error_get_tickets_test(self):
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
    async def get_affecting_ticket_no_tickets_test(self):
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

        assert affecting_ticket == {}
        assert event_bus.rpc_request.called

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
    async def append_note_to_ticket_service_number_test(self):
        ticket_id = 11111
        ticket_note = 'This is a ticket note'
        serial_number = ['VC1234567']

        request = {
            'request_id': uuid_,
            'body': {
                'ticket_id': ticket_id,
                'note': ticket_note,
                'service_numbers': serial_number
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
            result = await bruin_repository.append_note_to_ticket(ticket_id, ticket_note, service_numbers=serial_number)

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
        config.BOUNCING_DETECTOR_CONFIG['environment'] = 'dev'

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
    async def create_affecting_ticket_returning_2xx_status_test(self):
        client_id = 12345
        service_number = 'VC1234567'
        contact_info = {
            "ticket": {
                "email": "test@test.com",
                "phone": "No Contact Phone Available",
                "name": "Test man"
            },
            "site": {
                "email": "test@test.com",
                "phone": "3147317663",
                "name": "Test man"
            }
        }
        request = {
            'request_id': uuid_,
            "body": {
                        "clientId": client_id,
                        "category": "VAS",
                        "services": [
                            {
                                "serviceNumber": service_number
                            }
                        ],
                        "contacts": [
                            {
                                "email": contact_info['site']['email'],
                                "phone": contact_info['site']['phone'],
                                "name": contact_info['site']['name'],
                                "type": "site"
                            },
                            {
                                "email": contact_info['ticket']['email'],
                                "phone": contact_info['ticket']['phone'],
                                "name": contact_info['ticket']['name'],
                                "type": "ticket"
                            }
                        ]
            }
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

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.create_affecting_ticket(client_id, service_number, contact_info)

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.creation.request", request, timeout=90)
        assert result == response

    @pytest.mark.asyncio
    async def create_affecting_ticket_returning_non_2xx_status_test(self):
        client_id = 12345
        service_number = 'VC1234567'
        contact_info = {
            "ticket": {
                "email": "test@test.com",
                "phone": "No Contact Phone Available",
                "name": "Test man"
            },
            "site": {
                "email": "test@test.com",
                "phone": "3147317663",
                "name": "Test man"
            }
        }
        request = {
            'request_id': uuid_,
            "body": {
                        "clientId": client_id,
                        "category": "VAS",
                        "services": [
                            {
                                "serviceNumber": service_number
                            }
                        ],
                        "contacts": [
                            {
                                "email": contact_info['site']['email'],
                                "phone": contact_info['site']['phone'],
                                "name": contact_info['site']['name'],
                                "type": "site"
                            },
                            {
                                "email": contact_info['ticket']['email'],
                                "phone": contact_info['ticket']['phone'],
                                "name": contact_info['ticket']['name'],
                                "type": "ticket"
                            }
                        ]
            }
        }
        response = {
            'request_id': uuid_,
            'body': 9999,
            'status': 400,
        }

        err_msg = (
            f'Error while opening affecting ticket for client {client_id} and serial {service_number} in '
            f'{testconfig.BOUNCING_DETECTOR_CONFIG["environment"].upper()} environment: '
            f'Error {response["status"]} - {response["body"]}'
        )

        logger = Mock()
        config = testconfig
        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.create_affecting_ticket(client_id, service_number, contact_info)

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.creation.request", request, timeout=90)
        notifications_repository.send_slack_message.assert_awaited_once_with(err_msg)
        assert result == response

    @pytest.mark.asyncio
    async def create_affecting_ticket_exception_test(self):
        client_id = 12345
        service_number = 'VC1234567'
        contact_info = {
            "ticket": {
                "email": "test@test.com",
                "phone": "No Contact Phone Available",
                "name": "Test man"
            },
            "site": {
                "email": "test@test.com",
                "phone": "3147317663",
                "name": "Test man"
            }
        }
        request = {
            'request_id': uuid_,
            "body": {
                        "clientId": client_id,
                        "category": "VAS",
                        "services": [
                            {
                                "serviceNumber": service_number
                            }
                        ],
                        "contacts": [
                            {
                                "email": contact_info['site']['email'],
                                "phone": contact_info['site']['phone'],
                                "name": contact_info['site']['name'],
                                "type": "site"
                            },
                            {
                                "email": contact_info['ticket']['email'],
                                "phone": contact_info['ticket']['phone'],
                                "name": contact_info['ticket']['name'],
                                "type": "ticket"
                            }
                        ]
            }
        }
        response = {
            'request_id': uuid_,
            'body': 9999,
            'status': 400,
        }

        err_msg = (
                f'An error occurred while creating affecting ticket for client id {client_id} and serial '
                f'{service_number} -> ')

        logger = Mock()
        config = testconfig
        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(side_effect=Exception)

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.create_affecting_ticket(client_id, service_number, contact_info)

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.creation.request", request, timeout=90)
        notifications_repository.send_slack_message.assert_awaited_once_with(err_msg)
        assert result == nats_error_response

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
        config.BOUNCING_DETECTOR_CONFIG['environment'] = 'dev'

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
            "#*MetTel's IPA*#\n"
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
                    "noteValue": "#*MetTel's IPA*# \n "
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
                    "noteValue": "#*MetTel's IPA*# \n "
                                 'Trouble: LATENCY\n '
                                 'TimeStamp: 2019-09-10 10:34:00-04:00 ',
                    'createdDate': '2019-09-10 10:34:00-04:00'
                }
            ]
        }
        response = BruinRepository.find_detail_by_serial(ticket_mock, edge_serial_number)
        assert response is None
