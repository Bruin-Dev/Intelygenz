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
    async def get_tickets_with_no_service_number_specified_test(self):
        bruin_client_id = 12345
        ticket_statuses = ['New', 'InProgress', 'Draft']
        ticket_topic = "VAS"

        request = {
            'request_id': uuid_,
            'body': {
                'client_id': bruin_client_id,
                'ticket_status': ticket_statuses,
                'category': 'Network Scout',
                'ticket_topic': ticket_topic,
            },
        }
        response = {
            'request_id': uuid_,
            'body': [
                {'ticketID': 11111},
                {'ticketID': 22222},
            ],
            'status': 200,
        }

        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        bruin_repository = BruinRepository(config, logger, event_bus, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.get_tickets(bruin_client_id, ticket_topic, ticket_statuses)

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.request", request, timeout=90)
        assert result == response

    @pytest.mark.asyncio
    async def get_tickets_with_service_number_specified_test(self):
        bruin_client_id = 12345
        service_number = 'B827EB92EB72'
        ticket_statuses = ['New', 'InProgress', 'Draft']
        ticket_topic = "VAS"

        request = {
            'request_id': uuid_,
            'body': {
                'client_id': bruin_client_id,
                'ticket_status': ticket_statuses,
                'category': 'Network Scout',
                'ticket_topic': ticket_topic,
                'service_number': service_number,
            },
        }
        response = {
            'request_id': uuid_,
            'body': [
                {'ticketID': 11111},
                {'ticketID': 22222},
            ],
            'status': 200,
        }

        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        bruin_repository = BruinRepository(config, logger, event_bus, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.get_tickets(
                bruin_client_id, ticket_topic, ticket_statuses, service_number=service_number
            )

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.request", request, timeout=90)
        assert result == response

    @pytest.mark.asyncio
    async def get_tickets_with_rpc_request_failing_test(self):
        bruin_client_id = 12345
        ticket_statuses = ['New', 'InProgress', 'Draft']
        ticket_topic = "VAS"

        request = {
            'request_id': uuid_,
            'body': {
                'client_id': bruin_client_id,
                'ticket_status': ticket_statuses,
                'category': 'Network Scout',
                'ticket_topic': ticket_topic,
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
            result = await bruin_repository.get_tickets(bruin_client_id, ticket_topic, ticket_statuses)

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.request", request, timeout=90)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_tickets_with_rpc_request_returning_non_2xx_status_test(self):
        bruin_client_id = 12345
        ticket_statuses = ['New', 'InProgress', 'Draft']
        ticket_topic = "VAS"

        request = {
            'request_id': uuid_,
            'body': {
                'client_id': bruin_client_id,
                'ticket_status': ticket_statuses,
                'category': 'Network Scout',
                'ticket_topic': ticket_topic,
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
            result = await bruin_repository.get_tickets(bruin_client_id, ticket_topic, ticket_statuses)

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.request", request, timeout=90)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == response

    @pytest.mark.asyncio
    async def get_affecting_tickets_with_service_number_specified_test(self):
        bruin_client_id = 12345
        service_number = 'B827EB92EB72'
        ticket_statuses = ['New', 'InProgress', 'Draft']
        ticket_topic = "VAS"

        response = {
            'request_id': uuid_,
            'body': [
                {'ticketID': 11111},
                {'ticketID': 22222},
            ],
            'status': 200,
        }

        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        bruin_repository = BruinRepository(config, logger, event_bus, notifications_repository)
        bruin_repository.get_tickets = CoroutineMock(return_value=response)

        with uuid_mock:
            result = await bruin_repository.get_affecting_tickets(
                bruin_client_id, ticket_statuses, service_number=service_number
            )

        bruin_repository.get_tickets.assert_awaited_once_with(
            bruin_client_id, ticket_topic, ticket_statuses, service_number=service_number
        )
        assert result == response

    @pytest.mark.asyncio
    async def get_affecting_tickets_with_no_service_number_specified_test(self):
        bruin_client_id = 12345
        ticket_statuses = ['New', 'InProgress', 'Draft']
        ticket_topic = "VAS"

        response = {
            'request_id': uuid_,
            'body': [
                {'ticketID': 11111},
                {'ticketID': 22222},
            ],
            'status': 200,
        }

        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        bruin_repository = BruinRepository(config, logger, event_bus, notifications_repository)
        bruin_repository.get_tickets = CoroutineMock(return_value=response)

        with uuid_mock:
            result = await bruin_repository.get_affecting_tickets(bruin_client_id, ticket_statuses)

        bruin_repository.get_tickets.assert_awaited_once_with(
            bruin_client_id, ticket_topic, ticket_statuses, service_number=None
        )
        assert result == response

    @pytest.mark.asyncio
    async def get_open_affecting_tickets_with_service_number_specified_test(self):
        bruin_client_id = 12345
        service_number = 'B827EB92EB72'
        ticket_statuses = ['New', 'InProgress', 'Draft']

        response = {
            'request_id': uuid_,
            'body': [
                {'ticketID': 11111},
                {'ticketID': 22222},
            ],
            'status': 200,
        }

        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        bruin_repository = BruinRepository(config, logger, event_bus, notifications_repository)
        bruin_repository.get_affecting_tickets = CoroutineMock(return_value=response)

        with uuid_mock:
            result = await bruin_repository.get_open_affecting_tickets(bruin_client_id, service_number=service_number)

        bruin_repository.get_affecting_tickets.assert_awaited_once_with(
            bruin_client_id, ticket_statuses, service_number=service_number
        )
        assert result == response

    @pytest.mark.asyncio
    async def get_open_affecting_tickets_with_no_service_number_specified_test(self):
        bruin_client_id = 12345
        ticket_statuses = ['New', 'InProgress', 'Draft']

        response = {
            'request_id': uuid_,
            'body': [
                {'ticketID': 11111},
                {'ticketID': 22222},
            ],
            'status': 200,
        }

        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        bruin_repository = BruinRepository(config, logger, event_bus, notifications_repository)
        bruin_repository.get_affecting_tickets = CoroutineMock(return_value=response)

        with uuid_mock:
            result = await bruin_repository.get_open_affecting_tickets(bruin_client_id)

        bruin_repository.get_affecting_tickets.assert_awaited_once_with(
            bruin_client_id, ticket_statuses, service_number=None
        )
        assert result == response

    @pytest.mark.asyncio
    async def get_ticket_details_test(self):
        ticket_id = 11111

        request = {
            'request_id': uuid_,
            'body': {
                'ticket_id': ticket_id,
            },
        }
        response = {
            'request_id': uuid_,
            'body': {
                'ticketDetails': [
                    {
                        "detailID": 2746938,
                        "detailValue": 'B827EB92EB72',
                    },
                ],
                'ticketNotes': [
                    {
                        "noteId": 41894043,
                        "noteValue": f'#*Automation Engine*#\nTriage (Ixia)\nTimeStamp: 2019-07-30 06:38:00+00:00',
                        "createdDate": "2020-02-24T10:07:13.503-05:00",
                    },
                    {
                        "noteId": 41894044,
                        "noteValue": f'#*Automation Engine*#\nTriage (Ixia)\nTimeStamp: 2019-07-30 06:38:00+00:00',
                        "createdDate": "2020-02-24T10:07:13.503-05:00",
                    }
                ]
            },
            'status': 200,
        }

        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        bruin_repository = BruinRepository(config, logger, event_bus, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.get_ticket_details(ticket_id)

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.details.request", request, timeout=15)
        assert result == response

    @pytest.mark.asyncio
    async def get_ticket_details_with_rpc_request_failing_test(self):
        ticket_id = 11111

        request = {
            'request_id': uuid_,
            'body': {
                'ticket_id': ticket_id,
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
            result = await bruin_repository.get_ticket_details(ticket_id)

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.details.request", request, timeout=15)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_ticket_details_with_rpc_request_returning_non_2xx_status_test(self):
        ticket_id = 11111

        request = {
            'request_id': uuid_,
            'body': {
                'ticket_id': ticket_id,
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
            result = await bruin_repository.get_ticket_details(ticket_id)

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.details.request", request, timeout=15)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == response

    @pytest.mark.asyncio
    async def create_affecting_ticket_test(self):
        client_id = 12345
        service_number = 'B827EB76A8DE'

        request = {
            'request_id': uuid_,
            'body': {
                'clientId': client_id,
                "services": [
                    {
                        "serviceNumber": service_number,
                    },
                ],
                'category': 'VAS',
                'contacts': [
                    {
                        "email": 'ndimuro@mettel.net',
                        "phone": '9876543210',
                        "name": 'Nicholas DiMuro',
                        "type": "site",
                    },
                    {
                        "email": 'ndimuro@mettel.net',
                        "phone": '9876543210',
                        "name": 'Nicholas DiMuro',
                        "type": "ticket",
                    },
                ],
            },
        }
        response = {
            'request_id': uuid_,
            'body': {
                'ticketIds': [
                    9999,
                ],
            },
            'status': 200,
        }

        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        bruin_repository = BruinRepository(config, logger, event_bus, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.create_affecting_ticket(client_id, service_number)

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.creation.request", request, timeout=30)
        assert result == response

    @pytest.mark.asyncio
    async def create_affecting_ticket_with_rpc_request_failing_test(self):
        client_id = 12345
        service_number = 'B827EB76A8DE'

        request = {
            'request_id': uuid_,
            'body': {
                'clientId': client_id,
                "services": [
                    {
                        "serviceNumber": service_number,
                    },
                ],
                'category': 'VAS',
                'contacts': [
                    {
                        "email": 'ndimuro@mettel.net',
                        "phone": '9876543210',
                        "name": 'Nicholas DiMuro',
                        "type": "site",
                    },
                    {
                        "email": 'ndimuro@mettel.net',
                        "phone": '9876543210',
                        "name": 'Nicholas DiMuro',
                        "type": "ticket",
                    },
                ],
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
            result = await bruin_repository.create_affecting_ticket(client_id, service_number)

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.creation.request", request, timeout=30)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def create_affecting_ticket_with_rpc_request_returning_non_2xx_status_test(self):
        client_id = 12345
        service_number = 'B827EB76A8DE'

        request = {
            'request_id': uuid_,
            'body': {
                'clientId': client_id,
                "services": [
                    {
                        "serviceNumber": service_number,
                    },
                ],
                'category': 'VAS',
                'contacts': [
                    {
                        "email": 'ndimuro@mettel.net',
                        "phone": '9876543210',
                        "name": 'Nicholas DiMuro',
                        "type": "site",
                    },
                    {
                        "email": 'ndimuro@mettel.net',
                        "phone": '9876543210',
                        "name": 'Nicholas DiMuro',
                        "type": "ticket",
                    },
                ],
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
            result = await bruin_repository.create_affecting_ticket(client_id, service_number)

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.creation.request", request, timeout=30)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == response

    @pytest.mark.asyncio
    async def append_multiple_notes_to_ticket_test(self):
        ticket_id = 12345
        note_1 = {
            'text': 'This is ticket note 1',
            'service_number': 'B827EB76A8DE',
        }
        note_2 = {
            'text': 'This is ticket note 2',
            'service_number': 'B827EB76A8DE',
        }
        note_3 = {
            'text': 'This is ticket note 3',
            'service_number': 'B827EB76A8DE',
        }
        notes = [
            note_1,
            note_2,
            note_3,
        ]

        request = {
            'request_id': uuid_,
            'body': {
                'ticket_id': ticket_id,
                'notes': notes,
            },
        }
        response = {
            'request_id': uuid_,
            'body': {
                "ticketNotes": [
                    {
                        "noteID": 70646090,
                        "noteType": "ADN",
                        "noteValue": "This is ticket note 1",
                        "actionID": None,
                        "detailID": 123,
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
                    {
                        "noteID": 70646091,
                        "noteType": "ADN",
                        "noteValue": "This is ticket note 2",
                        "actionID": None,
                        "detailID": 999,
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
                    {
                        "noteID": 70646092,
                        "noteType": "ADN",
                        "noteValue": "This is ticket note 3",
                        "actionID": None,
                        "detailID": 456,
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
            },
            'status': 200,
        }

        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        bruin_repository = BruinRepository(config, logger, event_bus, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.append_multiple_notes_to_ticket(ticket_id, notes)

        event_bus.rpc_request.assert_awaited_once_with(
            "bruin.ticket.multiple.notes.append.request", request, timeout=45
        )
        assert result == response

    @pytest.mark.asyncio
    async def append_multiple_notes_to_ticket_with_rpc_request_failing_test(self):
        ticket_id = 12345
        note_1 = {
            'text': 'This is ticket note 1',
            'service_number': 'B827EB76A8DE',
        }
        note_2 = {
            'text': 'This is ticket note 2',
            'service_number': 'B827EB76A8DE',
        }
        note_3 = {
            'text': 'This is ticket note 3',
            'service_number': 'B827EB76A8DE',
        }
        notes = [
            note_1,
            note_2,
            note_3,
        ]

        request = {
            'request_id': uuid_,
            'body': {
                'ticket_id': ticket_id,
                'notes': notes,
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
            result = await bruin_repository.append_multiple_notes_to_ticket(ticket_id, notes)

        event_bus.rpc_request.assert_awaited_once_with(
            "bruin.ticket.multiple.notes.append.request", request, timeout=45
        )
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def append_multiple_notes_to_ticket_with_rpc_request_returning_non_2xx_status_test(self):
        ticket_id = 12345
        note_1 = {
            'text': 'This is ticket note 1',
            'service_number': 'B827EB76A8DE',
        }
        note_2 = {
            'text': 'This is ticket note 2',
            'service_number': 'B827EB76A8DE',
        }
        note_3 = {
            'text': 'This is ticket note 3',
            'service_number': 'B827EB76A8DE',
        }
        notes = [
            note_1,
            note_2,
            note_3,
        ]

        request = {
            'request_id': uuid_,
            'body': {
                'ticket_id': ticket_id,
                'notes': notes,
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
            result = await bruin_repository.append_multiple_notes_to_ticket(ticket_id, notes)

        event_bus.rpc_request.assert_awaited_once_with(
            "bruin.ticket.multiple.notes.append.request", request, timeout=45
        )
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == response
