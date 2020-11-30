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
    async def get_tickets_with_no_service_number_specified_test(self):
        bruin_client_id = 12345
        ticket_statuses = ['New', 'InProgress', 'Draft']
        ticket_topic = "VAS"

        request = {
            'request_id': uuid_,
            'body': {
                'client_id': bruin_client_id,
                'ticket_status': ticket_statuses,
                'category': 'SD-WAN',
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

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.get_tickets(bruin_client_id, ticket_topic, ticket_statuses)

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.request", request, timeout=90)
        assert result == response

    @pytest.mark.asyncio
    async def get_tickets_with_service_number_specified_test(self):
        bruin_client_id = 12345
        service_number = 'VC1234567'
        ticket_statuses = ['New', 'InProgress', 'Draft']
        ticket_topic = "VAS"

        request = {
            'request_id': uuid_,
            'body': {
                'client_id': bruin_client_id,
                'ticket_status': ticket_statuses,
                'category': 'SD-WAN',
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

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)

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
                'category': 'SD-WAN',
                'ticket_topic': ticket_topic,
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
                'category': 'SD-WAN',
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

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.get_tickets(bruin_client_id, ticket_topic, ticket_statuses)

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.request", request, timeout=90)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
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
                        "detailValue": 'VC1234567890',
                    },
                ],
                'ticketNotes': [
                    {
                        "noteId": 41894043,
                        "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
                        "createdDate": "2020-02-24T10:07:13.503-05:00",
                    },
                    {
                        "noteId": 41894044,
                        "noteValue": f'#*Automation Engine*#\nTriage\nTimeStamp: 2019-07-30 06:38:00+00:00',
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

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)

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

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)

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

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.get_ticket_details(ticket_id)

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.details.request", request, timeout=15)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == response

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
    async def append_note_to_ticket_with_optional_service_numbers_param_test(self):
        ticket_id = 11111
        ticket_note = 'This is a ticket note'
        service_number = 'VC1234567'

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

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)

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
    async def get_client_info_test(self):
        service_number = 'VC1234567'

        request = {
            'request_id': uuid_,
            'body': {
                'service_number': service_number,
            },
        }
        response = {
            'request_id': uuid_,
            'body': {
                'client_id': 9994,
                'client_name': 'METTEL/NEW YORK',
            },
            'status': 200,
        }

        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.get_client_info(service_number)

        event_bus.rpc_request.assert_awaited_once_with("bruin.customer.get.info", request, timeout=30)
        assert result == response

    @pytest.mark.asyncio
    async def get_client_info_with_rpc_request_failing_test(self):
        service_number = 'VC1234567'

        request = {
            'request_id': uuid_,
            'body': {
                'service_number': service_number,
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
            result = await bruin_repository.get_client_info(service_number)

        event_bus.rpc_request.assert_awaited_once_with("bruin.customer.get.info", request, timeout=30)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_client_info_with_rpc_request_returning_non_2xx_status_test(self):
        service_number = 'VC1234567'

        request = {
            'request_id': uuid_,
            'body': {
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

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)
        with uuid_mock:
            result = await bruin_repository.get_client_info(service_number)

        event_bus.rpc_request.assert_awaited_once_with("bruin.customer.get.info", request, timeout=30)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == response

    @pytest.mark.asyncio
    async def get_management_status_test(self):
        service_number = 'VC1234567'
        client_id = 9994

        request = {
            'request_id': uuid_,
            'body': {
                'client_id': client_id,
                'service_number': service_number,
                'status': 'A',
            },
        }
        response = {
            'request_id': uuid_,
            'body': 'Active – Gold Monitoring',
            'status': 200,
        }

        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)
        with uuid_mock:
            result = await bruin_repository.get_management_status(client_id, service_number)

        event_bus.rpc_request.assert_awaited_once_with("bruin.inventory.management.status", request, timeout=30)
        assert result == response

    @pytest.mark.asyncio
    async def get_management_status_with_rpc_request_failing_test(self):
        service_number = 'VC1234567'
        client_id = 9994

        request = {
            'request_id': uuid_,
            'body': {
                'client_id': client_id,
                'service_number': service_number,
                'status': 'A',
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
            result = await bruin_repository.get_management_status(client_id, service_number)

        event_bus.rpc_request.assert_awaited_once_with("bruin.inventory.management.status", request, timeout=30)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_management_status_with_rpc_request_returning_non_2xx_status_test(self):
        service_number = 'VC1234567'
        client_id = 9994

        request = {
            'request_id': uuid_,
            'body': {
                'client_id': client_id,
                'service_number': service_number,
                'status': 'A',
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

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.get_management_status(client_id, service_number)

        event_bus.rpc_request.assert_awaited_once_with("bruin.inventory.management.status", request, timeout=30)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == response

    @pytest.mark.asyncio
    async def resolve_ticket_test(self):
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
            result = await bruin_repository.resolve_ticket(ticket_id, detail_id)

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.status.resolve", request, timeout=15)
        assert result == response

    @pytest.mark.asyncio
    async def resolve_ticket_with_rpc_request_failing_test(self):
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
            result = await bruin_repository.resolve_ticket(ticket_id, detail_id)

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.status.resolve", request, timeout=15)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def resolve_ticket_with_rpc_request_returning_non_2xx_status_test(self):
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

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.resolve_ticket(ticket_id, detail_id)

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.status.resolve", request, timeout=15)
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
    async def create_outage_ticket_returning_2xx_status_test(self):
        client_id = 12345
        service_number = 'VC1234567'

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

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.create_outage_ticket(client_id, service_number)

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.creation.outage.request", request, timeout=30)
        assert result == response

    @pytest.mark.asyncio
    async def create_outage_ticket_returning_409_status_test(self):
        client_id = 12345
        service_number = 'VC1234567'

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

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.create_outage_ticket(client_id, service_number)

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.creation.outage.request", request, timeout=30)
        assert result == response

    @pytest.mark.asyncio
    async def create_outage_ticket_returning_471_status_test(self):
        client_id = 12345
        service_number = 'VC1234567'

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

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.create_outage_ticket(client_id, service_number)

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.creation.outage.request", request, timeout=30)
        assert result == response

    @pytest.mark.asyncio
    async def create_outage_ticket_with_rpc_request_failing_test(self):
        client_id = 12345
        service_number = 'VC1234567'

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

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.create_outage_ticket(client_id, service_number)

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.creation.outage.request", request, timeout=30)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def create_outage_ticket_with_rpc_request_returning_no_2xx_or_409_or_471_status_test(self):
        client_id = 12345
        service_number = 'VC1234567'

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

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.create_outage_ticket(client_id, service_number)

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.creation.outage.request", request, timeout=30)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == response

    @pytest.mark.asyncio
    async def append_autoresolve_note_to_ticket_test(self):
        serial_number = 'VC1234567'

        current_datetime = datetime.now()
        ticket_id = 11111
        ticket_note = (
            '#*Automation Engine*#\n'
            f'Auto-resolving detail for serial: {serial_number}\n'
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
                result = await bruin_repository.append_autoresolve_note_to_ticket(ticket_id, serial_number)

        bruin_repository.append_note_to_ticket.assert_awaited_once_with(ticket_id, ticket_note)
        assert result == response

    @pytest.mark.asyncio
    async def append_reopening_note_to_ticket_test(self):
        current_datetime = datetime.now()
        ticket_id = 11111
        service_number = 'VC1234567'
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
                result = await bruin_repository.append_reopening_note_to_ticket(
                    ticket_id, service_number, outage_causes
                )

        bruin_repository.append_note_to_ticket.assert_awaited_once_with(
            ticket_id, ticket_note, service_numbers=[service_number]
        )
        assert result == response

    @pytest.mark.asyncio
    async def get_outage_tickets_with_no_service_number_specified_test(self):
        bruin_client_id = 12345
        ticket_statuses = ['New', 'InProgress', 'Draft']
        ticket_topic = "VOO"

        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)
        bruin_repository.get_tickets = CoroutineMock()

        with uuid_mock:
            await bruin_repository.get_outage_tickets(bruin_client_id, ticket_statuses)

        bruin_repository.get_tickets.assert_awaited_once_with(
            bruin_client_id, ticket_topic, ticket_statuses, service_number=None
        )

    @pytest.mark.asyncio
    async def get_outage_tickets_test(self):
        bruin_client_id = 12345
        service_number = 'VC1234567'
        ticket_statuses = ['New', 'InProgress', 'Draft']
        ticket_topic = "VOO"

        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)
        bruin_repository.get_tickets = CoroutineMock()

        await bruin_repository.get_outage_tickets(bruin_client_id, ticket_statuses, service_number=service_number)

        bruin_repository.get_tickets.assert_awaited_once_with(
            bruin_client_id, ticket_topic, ticket_statuses, service_number=service_number
        )

    @pytest.mark.asyncio
    async def get_open_outage_tickets_with_no_service_number_specified_test(self):
        bruin_client_id = 12345
        ticket_statuses = ['New', 'InProgress', 'Draft']

        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)
        bruin_repository.get_outage_tickets = CoroutineMock()

        with uuid_mock:
            await bruin_repository.get_open_outage_tickets(bruin_client_id)

        bruin_repository.get_outage_tickets.assert_awaited_once_with(
            bruin_client_id, ticket_statuses, service_number=None
        )

    @pytest.mark.asyncio
    async def get_open_outage_tickets_test(self):
        bruin_client_id = 12345
        service_number = 'VC1234567'
        ticket_statuses = ['New', 'InProgress', 'Draft']

        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)
        bruin_repository.get_outage_tickets = CoroutineMock()

        with uuid_mock:
            await bruin_repository.get_open_outage_tickets(bruin_client_id, service_number=service_number)

        bruin_repository.get_outage_tickets.assert_awaited_once_with(
            bruin_client_id, ticket_statuses, service_number=service_number
        )

    def is_management_status_active_test(self):
        management_status = "Pending"
        result = BruinRepository.is_management_status_active(management_status)
        assert result is True

        management_status = "Active – Gold Monitoring"
        result = BruinRepository.is_management_status_active(management_status)
        assert result is True

        management_status = "Active – Platinum Monitoring"
        result = BruinRepository.is_management_status_active(management_status)
        assert result is True

        management_status = "Fake status"
        result = BruinRepository.is_management_status_active(management_status)
        assert result is False

    @pytest.mark.asyncio
    async def append_triage_note_with_dev_environment_test(self):
        ticket_id = 12345
        service_number = 'VC1234567'

        ticket_detail = {
            'ticket_id': ticket_id,
            'ticket_detail': {
                'detailID': 67890,
                'detailValue': service_number,
            }
        }
        edge_status_1 = {
            'edgeState': 'OFFLINE',
            'edgeName': 'Travis Touchdown',
            'edgeSerialNumber': service_number,
            'linkId': 1234,
            'linkState': 'DISCONNECTED',
            'interface': 'GE1',
            'displayName': 'Solid Snake',
            'enterpriseName': 'EVIL-CORP|12345|',
        }

        edge_status_2 = {
            'edgeState': 'OFFLINE',
            'edgeSerialNumber': service_number,
            'edgeName': 'Travis Touchdown',
            'linkId': 9012,
            'linkState': 'STABLE',
            'interface': 'GE7',
            'displayName': 'Big Boss',
            'enterpriseName': 'EVIL-CORP|12345|',
        }

        edge_status_3 = {
            'edgeState': 'OFFLINE',
            'edgeSerialNumber': service_number,
            'edgeName': 'Travis Touchdown',
            'linkId': 5678,
            'linkState': 'STABLE',
            'interface': 'INTERNET3',
            'displayName': 'Otacon',
            'enterpriseName': 'EVIL-CORP|12345|',
        }

        edge_status = [edge_status_1, edge_status_2, edge_status_3]

        ticket_note = 'This is the first ticket note'

        event_bus = Mock()
        logger = Mock()
        config = testconfig

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)
        bruin_repository.append_note_to_ticket = CoroutineMock()

        await bruin_repository.append_triage_note(ticket_detail, ticket_note)

        notifications_repository.send_slack_message.assert_awaited_once()
        bruin_repository.append_note_to_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def append_triage_note_with_production_environment_test(self):
        ticket_id = 12345
        service_number = 'VC1234567'

        ticket_detail = {
            'ticket_id': ticket_id,
            'ticket_detail': {
                'detailID': 67890,
                'detailValue': service_number,
            },
        }
        edge_status_1 = {
            'edgeState': 'OFFLINE',
            'edgeName': 'Travis Touchdown',
            'edgeSerialNumber': service_number,
            'linkId': 1234,
            'linkState': 'DISCONNECTED',
            'interface': 'GE1',
            'displayName': 'Solid Snake',
            'enterpriseName': 'EVIL-CORP|12345|',
        }

        edge_status_2 = {
            'edgeState': 'OFFLINE',
            'edgeSerialNumber': service_number,
            'edgeName': 'Travis Touchdown',
            'linkId': 9012,
            'linkState': 'STABLE',
            'interface': 'GE7',
            'displayName': 'Big Boss',
            'enterpriseName': 'EVIL-CORP|12345|',
        }

        edge_status_3 = {
            'edgeState': 'OFFLINE',
            'edgeSerialNumber': service_number,
            'edgeName': 'Travis Touchdown',
            'linkId': 5678,
            'linkState': 'STABLE',
            'interface': 'INTERNET3',
            'displayName': 'Otacon',
            'enterpriseName': 'EVIL-CORP|12345|',
        }

        edge_status = [edge_status_1, edge_status_2, edge_status_3]

        ticket_note = 'This is the first ticket note'

        append_note_to_ticket_response = {
            'body': 'Note appended with success',
            'status': 200,
        }

        event_bus = Mock()
        logger = Mock()
        config = testconfig

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)
        bruin_repository.append_note_to_ticket = CoroutineMock(return_value=append_note_to_ticket_response)

        custom_triage_config = config.TRIAGE_CONFIG.copy()
        custom_triage_config['environment'] = 'production'
        with patch.dict(config.TRIAGE_CONFIG, custom_triage_config):
            await bruin_repository.append_triage_note(ticket_detail, ticket_note)

        bruin_repository.append_note_to_ticket.assert_awaited_once_with(
            ticket_id, ticket_note, service_numbers=[service_number]
        )

    @pytest.mark.asyncio
    async def append_triage_note_with_unknown_environment_test(self):
        ticket_id = 12345
        service_number = 'VC1234567'

        ticket_detail = {
            'ticket_id': ticket_id,
            'ticket_detail': {
                'detailID': 67890,
                'detailValue': service_number,
            },
        }

        ticket_note = 'This is the first ticket note'

        event_bus = Mock()
        logger = Mock()
        config = testconfig

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)
        bruin_repository.append_note_to_ticket = CoroutineMock()

        custom_triage_config = config.TRIAGE_CONFIG.copy()
        custom_triage_config['environment'] = 'unknown'
        with patch.dict(config.TRIAGE_CONFIG, custom_triage_config):
            await bruin_repository.append_triage_note(ticket_detail, ticket_note)

        bruin_repository.append_note_to_ticket.assert_not_awaited()
        notifications_repository.send_slack_message.assert_not_awaited()

    @pytest.mark.asyncio
    async def append_triage_note_with_triage_note_greater_than_1500_char_test(self):
        ticket_id = 12345
        service_number = 'VC1234567'

        ticket_detail = {
            'ticket_id': ticket_id,
            'ticket_detail': {
                'detailID': 67890,
                'detailValue': service_number,
            },
        }

        ticket_note = "#Automation Engine#\n" \
                      "Triage\n" \
                      "Orchestrator Instance: mettel.velocloud.net\n" \
                      "Edge Name: 540 - Gore Mountain Lodge-Active Velocloud\n" \
                      "Links: Edge - QoE - Transport - Events\n" \
                      "Edge Status: CONNECTED\n" \
                      "Serial: VC05400016539\n" \
                      "Interface GE2\n" \
                      "Interface GE2 Label: Frontier Comm - Becks TAVERN (MetTel - 10.RBCB.131243)\n" \
                      "Interface GE2 Status: STABLE\n" \
                      "Interface GE1\n" \
                      "Interface GE1 Label: MetTel WR54 4G - Gore Lodge Hotel LAN1 (Mettel - 5338765010)\n" \
                      "Interface GE1 Status: DISCONNECTED\n" \
                      "Interface SFP1\n" \
                      "Interface SFP1 Label: Frontier Comm - Gore Lodge Hotel (MetTel - 10.RBCB.131242)\n" \
                      "Interface SFP1 Status: STABLE\n" \
                      "Interface SFP2\n" \
                      "Interface SFP2 Label: MetTel WR54 4G - Gore Lodge Hotel LAN4\n" \
                      "Interface SFP2 Status: STABLE\n" \
                      "Last Edge Online: 2020-08-07 01:08:46-04:00\n" \
                      "Last Edge Offline: 2020-08-07 00:04:16-04:00\n" \
                      "Last GE2 Interface Online: 2020-08-07 10:02:22-04:00\n" \
                      "Last GE2 Interface Offline: 2020-08-07 00:02:36-04:00\n" \
                      "Last GE1 Interface Online: 2020-08-12 02:03:05-04:00\n" \
                      "Last GE1 Interface Offline: 2020-08-12 22:06:46-04:00\n" \
                      "Last SFP1 Interface Online: 2020-08-07 10:02:22-04:00\n" \
                      "Last SFP1 Interface Offline: 2020-08-07 00:02:36-04:00\n" \
                      "Last SFP2 Interface Online: 2020-08-13 14:19:04-04:00\n" \
                      "Last SFP2 Interface Online: 2020-08-13 14:19:04-04:00\n" \
                      "Last SFP2 Interface Online: 2020-08-13 14:19:04-04:00\n" \
                      "Last SFP2 Interface Online: 2020-08-13 14:19:04-04:00\n" \
                      "Last SFP2 Interface Online: 2020-08-13 14:19:04-04:00\n" \
                      "Last SFP2 Interface Online: 2020-08-13 14:19:04-04:00\n" \
                      "Last SFP2 Interface Offline: 2020-08-13 14:13:25-04:00.\n" \
                      "Last SFP2 Interface Offline: 2020-08-13 14:13:25-04:00.\n" \
                      "End"

        append_note_to_ticket_response = {
            'body': 'Note appended with success',
            'status': 200,
        }

        event_bus = Mock()
        logger = Mock()
        config = testconfig

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)
        bruin_repository.append_note_to_ticket = CoroutineMock(return_value=append_note_to_ticket_response)

        custom_triage_config = config.TRIAGE_CONFIG.copy()
        custom_triage_config['environment'] = 'production'
        with patch.dict(config.TRIAGE_CONFIG, custom_triage_config):
            await bruin_repository.append_triage_note(ticket_detail, ticket_note)

        assert len(bruin_repository.append_note_to_ticket.call_args_list) == 2

    @pytest.mark.asyncio
    async def append_triage_note_with_append_note_request_not_having_2xx_status_test(self):
        ticket_id = 12345
        service_number = 'VC1234567'

        ticket_detail = {
            'ticket_id': ticket_id,
            'ticket_detail': {
                'detailID': 67890,
                'detailValue': service_number,
            },
        }

        ticket_note = 'This is the first ticket note'

        append_note_to_ticket_response = {
            'body': 'Failed',
            'status': 400,
        }

        event_bus = Mock()
        logger = Mock()
        config = testconfig

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)
        bruin_repository.append_note_to_ticket = CoroutineMock(return_value=append_note_to_ticket_response)

        custom_triage_config = config.TRIAGE_CONFIG.copy()
        custom_triage_config['environment'] = 'production'
        with patch.dict(config.TRIAGE_CONFIG, custom_triage_config):
            note_appended = await bruin_repository.append_triage_note(ticket_detail, ticket_note)

        bruin_repository.append_note_to_ticket.assert_awaited_once_with(
            ticket_id, ticket_note, service_numbers=[service_number]
        )
        assert note_appended is None

    @pytest.mark.asyncio
    async def append_triage_note_with_append_note_request_having_503_status_test(self):
        ticket_id = 12345
        service_number = 'VC1234567'

        ticket_detail = {
            'ticket_id': ticket_id,
            'ticket_detail': {
                'detailID': 67890,
                'detailValue': service_number,
            },
        }

        ticket_note = 'This is the first ticket note'

        append_note_to_ticket_response = {
            'body': 'Failed',
            'status': 503,
        }

        event_bus = Mock()
        logger = Mock()
        config = testconfig

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)
        bruin_repository.append_note_to_ticket = CoroutineMock(return_value=append_note_to_ticket_response)

        custom_triage_config = config.TRIAGE_CONFIG.copy()
        custom_triage_config['environment'] = 'production'
        with patch.dict(config.TRIAGE_CONFIG, custom_triage_config):
            note_appended = await bruin_repository.append_triage_note(ticket_detail, ticket_note)

        bruin_repository.append_note_to_ticket.assert_awaited_once_with(
            ticket_id, ticket_note, service_numbers=[service_number]
        )
        assert note_appended == 503

    @pytest.mark.asyncio
    async def append_triage_note_with_triage_note_greater_than_1500_char_return_non_2xx_test(self):
        ticket_id = 12345
        service_number = 'VC1234567'

        ticket_detail = {
            'ticket_id': ticket_id,
            'ticket_detail': {
                'detailID': 67890,
                'detailValue': service_number,
            },
        }

        ticket_note = "#Automation Engine#\n" \
                      "Triage\n" \
                      "Orchestrator Instance: mettel.velocloud.net\n" \
                      "Edge Name: 540 - Gore Mountain Lodge-Active Velocloud\n" \
                      "Links: Edge - QoE - Transport - Events\n" \
                      "Edge Status: CONNECTED\n" \
                      "Serial: VC05400016539\n" \
                      "Interface GE2\n" \
                      "Interface GE2 Label: Frontier Comm - Becks TAVERN (MetTel - 10.RBCB.131243)\n" \
                      "Interface GE2 Status: STABLE\n" \
                      "Interface GE1\n" \
                      "Interface GE1 Label: MetTel WR54 4G - Gore Lodge Hotel LAN1 (Mettel - 5338765010)\n" \
                      "Interface GE1 Status: DISCONNECTED\n" \
                      "Interface SFP1\n" \
                      "Interface SFP1 Label: Frontier Comm - Gore Lodge Hotel (MetTel - 10.RBCB.131242)\n" \
                      "Interface SFP1 Status: STABLE\n" \
                      "Interface SFP2\n" \
                      "Interface SFP2 Label: MetTel WR54 4G - Gore Lodge Hotel LAN4\n" \
                      "Interface SFP2 Status: STABLE\n" \
                      "Last Edge Online: 2020-08-07 01:08:46-04:00\n" \
                      "Last Edge Offline: 2020-08-07 00:04:16-04:00\n" \
                      "Last GE2 Interface Online: 2020-08-07 10:02:22-04:00\n" \
                      "Last GE2 Interface Offline: 2020-08-07 00:02:36-04:00\n" \
                      "Last GE1 Interface Online: 2020-08-12 02:03:05-04:00\n" \
                      "Last GE1 Interface Offline: 2020-08-12 22:06:46-04:00\n" \
                      "Last SFP1 Interface Online: 2020-08-07 10:02:22-04:00\n" \
                      "Last SFP1 Interface Offline: 2020-08-07 00:02:36-04:00\n" \
                      "Last SFP2 Interface Online: 2020-08-13 14:19:04-04:00\n" \
                      "Last SFP2 Interface Online: 2020-08-13 14:19:04-04:00\n" \
                      "Last SFP2 Interface Online: 2020-08-13 14:19:04-04:00\n" \
                      "Last SFP2 Interface Online: 2020-08-13 14:19:04-04:00\n" \
                      "Last SFP2 Interface Online: 2020-08-13 14:19:04-04:00\n" \
                      "Last SFP2 Interface Online: 2020-08-13 14:19:04-04:00\n" \
                      "Last SFP2 Interface Offline: 2020-08-13 14:13:25-04:00.\n" \
                      "Last SFP2 Interface Offline: 2020-08-13 14:13:25-04:00.\n" \
                      "End"

        append_note_to_ticket_response = {
            'body': 'Failed',
            'status': 400,
        }

        event_bus = Mock()
        logger = Mock()
        config = testconfig

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)
        bruin_repository.append_note_to_ticket = CoroutineMock(return_value=append_note_to_ticket_response)

        custom_triage_config = config.TRIAGE_CONFIG.copy()
        custom_triage_config['environment'] = 'production'
        with patch.dict(config.TRIAGE_CONFIG, custom_triage_config):
            note_appended = await bruin_repository.append_triage_note(ticket_detail, ticket_note)

        assert note_appended is None

    @pytest.mark.asyncio
    async def append_triage_note_with_triage_note_greater_than_1500_char_return_503_test(self):
        ticket_id = 12345
        service_number = 'VC1234567'

        ticket_detail = {
            'ticket_id': ticket_id,
            'ticket_detail': {
                'detailID': 67890,
                'detailValue': service_number,
            },
        }

        ticket_note = "#Automation Engine#\n" \
                      "Triage\n" \
                      "Orchestrator Instance: mettel.velocloud.net\n" \
                      "Edge Name: 540 - Gore Mountain Lodge-Active Velocloud\n" \
                      "Links: Edge - QoE - Transport - Events\n" \
                      "Edge Status: CONNECTED\n" \
                      "Serial: VC05400016539\n" \
                      "Interface GE2\n" \
                      "Interface GE2 Label: Frontier Comm - Becks TAVERN (MetTel - 10.RBCB.131243)\n" \
                      "Interface GE2 Status: STABLE\n" \
                      "Interface GE1\n" \
                      "Interface GE1 Label: MetTel WR54 4G - Gore Lodge Hotel LAN1 (Mettel - 5338765010)\n" \
                      "Interface GE1 Status: DISCONNECTED\n" \
                      "Interface SFP1\n" \
                      "Interface SFP1 Label: Frontier Comm - Gore Lodge Hotel (MetTel - 10.RBCB.131242)\n" \
                      "Interface SFP1 Status: STABLE\n" \
                      "Interface SFP2\n" \
                      "Interface SFP2 Label: MetTel WR54 4G - Gore Lodge Hotel LAN4\n" \
                      "Interface SFP2 Status: STABLE\n" \
                      "Last Edge Online: 2020-08-07 01:08:46-04:00\n" \
                      "Last Edge Offline: 2020-08-07 00:04:16-04:00\n" \
                      "Last GE2 Interface Online: 2020-08-07 10:02:22-04:00\n" \
                      "Last GE2 Interface Offline: 2020-08-07 00:02:36-04:00\n" \
                      "Last GE1 Interface Online: 2020-08-12 02:03:05-04:00\n" \
                      "Last GE1 Interface Offline: 2020-08-12 22:06:46-04:00\n" \
                      "Last SFP1 Interface Online: 2020-08-07 10:02:22-04:00\n" \
                      "Last SFP1 Interface Offline: 2020-08-07 00:02:36-04:00\n" \
                      "Last SFP2 Interface Online: 2020-08-13 14:19:04-04:00\n" \
                      "Last SFP2 Interface Online: 2020-08-13 14:19:04-04:00\n" \
                      "Last SFP2 Interface Online: 2020-08-13 14:19:04-04:00\n" \
                      "Last SFP2 Interface Online: 2020-08-13 14:19:04-04:00\n" \
                      "Last SFP2 Interface Online: 2020-08-13 14:19:04-04:00\n" \
                      "Last SFP2 Interface Online: 2020-08-13 14:19:04-04:00\n" \
                      "Last SFP2 Interface Offline: 2020-08-13 14:13:25-04:00.\n" \
                      "Last SFP2 Interface Offline: 2020-08-13 14:13:25-04:00.\n" \
                      "End"

        append_note_to_ticket_response = {
            'body': 'Failed',
            'status': 503,
        }

        event_bus = Mock()
        logger = Mock()
        config = testconfig

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)
        bruin_repository.append_note_to_ticket = CoroutineMock(return_value=append_note_to_ticket_response)

        custom_triage_config = config.TRIAGE_CONFIG.copy()
        custom_triage_config['environment'] = 'production'
        with patch.dict(config.TRIAGE_CONFIG, custom_triage_config):
            note_appended = await bruin_repository.append_triage_note(ticket_detail, ticket_note)

        assert note_appended == 503
