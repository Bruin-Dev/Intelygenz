import os
from datetime import datetime
from unittest.mock import Mock
from unittest.mock import patch

import pytest
from application.repositories.bruin_repository import BruinRepository
from asynctest import CoroutineMock
from shortuuid import uuid

from application.repositories import bruin_repository as bruin_repository_module
from application.repositories import nats_error_response
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
                'ticket_statuses': ticket_statuses,
                'product_category': testconfig.PRODUCT_CATEGORY,
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

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.basic.request", request, timeout=90)
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
                'ticket_statuses': ticket_statuses,
                'product_category': testconfig.PRODUCT_CATEGORY,
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

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.basic.request", request, timeout=90)
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
                'ticket_statuses': ticket_statuses,
                'product_category': testconfig.PRODUCT_CATEGORY,
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

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.basic.request", request, timeout=90)
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
                'ticket_statuses': ticket_statuses,
                'product_category': testconfig.PRODUCT_CATEGORY,
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

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.basic.request", request, timeout=90)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == response

    @pytest.mark.asyncio
    async def get_ticket_test(self):
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
                "clientID": 83109,
                "ticketID": ticket_id,
                "ticketStatus": "Resolved",
                "address": {
                    "address": "323 Marble Mill Rd NW",
                    "city": "Marietta",
                    "state": "GA",
                    "zip": "30060-1037",
                    "country": "USA",
                },
                "createDate": "9/8/2020 11:40:11 PM",
                "createdBy": "Intelygenz Ai",
                "callType": "REP",
                "category": "VOO",
                "severity": 3,
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
            result = await bruin_repository.get_ticket(ticket_id)

        event_bus.rpc_request.assert_awaited_once_with("bruin.single_ticket.basic.request", request, timeout=15)
        assert result == response

    @pytest.mark.asyncio
    async def get_ticket_with_rpc_request_failing_test(self):
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
            result = await bruin_repository.get_ticket(ticket_id)

        event_bus.rpc_request.assert_awaited_once_with("bruin.single_ticket.basic.request", request, timeout=15)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_ticket_with_rpc_request_returning_non_2xx_status_test(self):
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
            result = await bruin_repository.get_ticket(ticket_id)

        event_bus.rpc_request.assert_awaited_once_with("bruin.single_ticket.basic.request", request, timeout=15)
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
                        "noteValue": f"#*MetTel's IPA*#\nTriage (VeloCloud)\nTimeStamp: 2019-07-30 06:38:00+00:00",
                        "createdDate": "2020-02-24T10:07:13.503-05:00",
                    },
                    {
                        "noteId": 41894044,
                        "noteValue": f"#*MetTel's IPA*#\nTriage (VeloCloud)\nTimeStamp: 2019-07-30 06:38:00+00:00",
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
    async def change_detail_work_queue_test(self):
        ticket_id = 12345
        detail_id = 67890
        task_result = "Wireless Repair Intervention Needed"
        service_number = 'VC1234567'

        request = {
            'request_id': uuid_,
            'body': {
                "service_number": service_number,
                "ticket_id": ticket_id,
                "detail_id": detail_id,
                "queue_name": task_result
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
            result = await bruin_repository.change_detail_work_queue(serial_number=service_number,
                                                                     ticket_id=ticket_id,
                                                                     detail_id=detail_id,
                                                                     task_result=task_result)

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.change.work", request, timeout=90)
        assert result == response

    @pytest.mark.asyncio
    async def get_ticket_overview_test(self):
        ticket_id = 12345

        request = {
            'request_id': uuid_,
            'body': {
                "ticket_id": ticket_id,
            },
        }
        response = {
            'request_id': uuid_,
            'body': {
                "clientID": 9994,
                "clientName": 'METTEL/NEW YORK',
                "ticketID": ticket_id,
                "category": "SD-WAN",
                "topic": "Service Outage Trouble",
                "referenceTicketNumber": 0,
                "ticketStatus": "In-Progress",
                "address": {
                    "address": "55 Water St Fl 32",
                    "city": "New York",
                    "state": "NY",
                    "zip": "10041-3299",
                    "country": "USA"
                },
                "createDate": "1/21/2021 4:02:30 PM",
                "createdBy": "Intelygenz Ai",
                "creationNote": None,
                "resolveDate": "",
                "resolvedby": None,
                "closeDate": None,
                "closedBy": None,
                "lastUpdate": None,
                "updatedBy": None,
                "mostRecentNote": "1/21/2021 4:06:56 PM Intelygenz Ai",
                "nextScheduledDate": "1/28/2021 5:00:00 AM",
                "flags": "",
                "severity": "2"
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
            result = await bruin_repository.get_ticket_overview(ticket_id)

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.overview.request", request, timeout=30)
        assert result == response

    @pytest.mark.asyncio
    async def get_ticket_overview_rpc_request_failing_test(self):
        ticket_id = 12345

        request = {
            'request_id': uuid_,
            'body': {
                "ticket_id": ticket_id,
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
            result = await bruin_repository.get_ticket_overview(ticket_id=ticket_id)

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.overview.request", request, timeout=30)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_ticket_overview_with_rpc_request_returning_non_2xx_status_test(self):
        ticket_id = 12345

        request = {
            'request_id': uuid_,
            'body': {
                "ticket_id": ticket_id,
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
            result = await bruin_repository.get_ticket_overview(ticket_id)

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.overview.request", request, timeout=30)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == response

    @pytest.mark.asyncio
    async def change_detail_work_queue_rpc_request_failing_test(self):
        ticket_id = 12345
        detail_id = 67890
        task_result = "Wireless Repair Intervention Needed"
        service_number = 'VC1234567'

        request = {
            'request_id': uuid_,
            'body': {
                "service_number": service_number,
                "ticket_id": ticket_id,
                "detail_id": detail_id,
                "queue_name": task_result
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
            result = await bruin_repository.change_detail_work_queue(serial_number=service_number,
                                                                     ticket_id=ticket_id,
                                                                     detail_id=detail_id,
                                                                     task_result=task_result)

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.change.work", request, timeout=90)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def change_detail_work_queue_with_rpc_request_returning_non_2xx_status_test(self):
        ticket_id = 12345
        detail_id = 67890
        task_result = "Wireless Repair Intervention Needed"
        service_number = 'VC1234567'

        request = {
            'request_id': uuid_,
            'body': {
                "service_number": service_number,
                "ticket_id": ticket_id,
                "detail_id": detail_id,
                "queue_name": task_result
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
            result = await bruin_repository.change_detail_work_queue(serial_number=service_number,
                                                                     ticket_id=ticket_id,
                                                                     detail_id=detail_id,
                                                                     task_result=task_result)

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.change.work", request, timeout=90)
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
    async def create_outage_ticket_returning_472_status_test(self):
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
            'status': 472,
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
    async def create_outage_ticket_returning_473_status_test(self):
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
            'status': 473,
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
    async def unpause_ticket_detail_with_only_detail_id_specified_test(self):
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
            result = await bruin_repository.unpause_ticket_detail(ticket_id, detail_id=detail_id)

        bruin_repository._event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.unpause", request, timeout=30)
        assert result == response

    @pytest.mark.asyncio
    async def unpause_ticket_detail_with_only_service_number_specified_test(self):
        ticket_id = 12345
        service_number = 'VC1234567'

        request = {
            'request_id': uuid_,
            'body': {
                'ticket_id': ticket_id,
                'service_number': service_number,
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
            result = await bruin_repository.unpause_ticket_detail(ticket_id, service_number=service_number)

        bruin_repository._event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.unpause", request, timeout=30)
        assert result == response

    @pytest.mark.asyncio
    async def unpause_ticket_detail_with_detail_id_and_service_number_specified_test(self):
        ticket_id = 12345
        detail_id = 67890
        service_number = 'VC1234567'

        request = {
            'request_id': uuid_,
            'body': {
                'ticket_id': ticket_id,
                'detail_id': detail_id,
                'service_number': service_number,
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
            result = await bruin_repository.unpause_ticket_detail(
                ticket_id, detail_id=detail_id, service_number=service_number
            )

        bruin_repository._event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.unpause", request, timeout=30)
        assert result == response

    @pytest.mark.asyncio
    async def unpause_ticket_detail_with_rpc_request_failing_test(self):
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
            result = await bruin_repository.unpause_ticket_detail(ticket_id, detail_id=detail_id)

        bruin_repository._event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.unpause", request, timeout=30)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def unpause_ticket_detail_with_rpc_request_returning_non_2xx_status_test(self):
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
            result = await bruin_repository.unpause_ticket_detail(ticket_id, detail_id=detail_id)

        bruin_repository._event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.unpause", request, timeout=30)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == response

    @pytest.mark.asyncio
    async def change_ticket_severity_test(self):
        ticket_id = 12345
        severity_level = 2
        reason_for_change = os.linesep.join([
            'Changing to Severity 2',
            'Edge Status: Offline',
        ])

        request = {
            'request_id': uuid_,
            'body': {
                'ticket_id': ticket_id,
                'severity': severity_level,
                'reason': reason_for_change,
            },
        }
        response = {
            'request_id': uuid_,
            'body': {
                'TicketId': ticket_id,
                'Result': True,
            },
            'status': 200,
        }

        logger = Mock()
        config = testconfig

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await bruin_repository.change_ticket_severity(ticket_id, severity_level, reason_for_change)

        event_bus.rpc_request.assert_awaited_once_with("bruin.change.ticket.severity", request, timeout=45)
        notifications_repository.send_slack_message.assert_awaited_once()
        assert result == response

    @pytest.mark.asyncio
    async def change_ticket_severity_with_rpc_request_failing_test(self):
        ticket_id = 12345
        severity_level = 2
        reason_for_change = os.linesep.join([
            'Changing to Severity 2',
            'Edge Status: Offline',
        ])

        request = {
            'request_id': uuid_,
            'body': {
                'ticket_id': ticket_id,
                'severity': severity_level,
                'reason': reason_for_change,
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
            result = await bruin_repository.change_ticket_severity(ticket_id, severity_level, reason_for_change)

        event_bus.rpc_request.assert_awaited_once_with("bruin.change.ticket.severity", request, timeout=45)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def change_ticket_severity_with_rpc_request_returning_non_2xx_status_test(self):
        ticket_id = 12345
        severity_level = 2
        reason_for_change = os.linesep.join([
            'Changing to Severity 2',
            'Edge Status: Offline',
        ])

        request = {
            'request_id': uuid_,
            'body': {
                'ticket_id': ticket_id,
                'severity': severity_level,
                'reason': reason_for_change,
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
            result = await bruin_repository.change_ticket_severity(ticket_id, severity_level, reason_for_change)

        event_bus.rpc_request.assert_awaited_once_with("bruin.change.ticket.severity", request, timeout=45)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == response

    @pytest.mark.asyncio
    async def append_autoresolve_note_to_ticket_test(self):
        serial_number = 'VC1234567'

        current_datetime = datetime.now()
        ticket_id = 11111
        ticket_note = (
            "#*MetTel's IPA*#\n"
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

        bruin_repository.append_note_to_ticket.assert_awaited_once_with(
            ticket_id, ticket_note, service_numbers=[serial_number]
        )
        assert result == response

    @pytest.mark.asyncio
    async def append_reopening_note_to_ticket_test(self):
        current_datetime = datetime.now()
        ticket_id = 11111
        service_number = 'VC1234567'
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

        with patch.object(config, 'CURRENT_ENVIRONMENT', 'production'):
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

        with patch.object(config, 'CURRENT_ENVIRONMENT', 'unknown'):
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

        ticket_note = "#MetTel's IPA#\n" \
                      "Triage (VeloCloud)\n" \
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

        with patch.object(config, 'CURRENT_ENVIRONMENT', 'production'):
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

        with patch.object(config, 'CURRENT_ENVIRONMENT', 'production'):
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

        with patch.object(config, 'CURRENT_ENVIRONMENT', 'production'):
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

        ticket_note = "#MetTel's IPA#\n" \
                      "Triage (VeloCloud)\n" \
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

        with patch.object(config, 'CURRENT_ENVIRONMENT', 'production'):
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

        ticket_note = "#MetTel's IPA#\n" \
                      "Triage (VeloCloud)\n" \
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

        with patch.object(config, 'CURRENT_ENVIRONMENT', 'production'):
            note_appended = await bruin_repository.append_triage_note(ticket_detail, ticket_note)

        assert note_appended == 503

    @pytest.mark.asyncio
    async def append_digi_reboot_note_test(self):
        current_datetime = datetime.now()
        ticket_id = 11111
        service_number = 'VC1234567'
        outage_causes = "Some causes of the outage"
        interface = 'GE1'
        ticket_note = os.linesep.join([
            "#*MetTel's IPA*#",
            f'Offline DiGi interface identified for serial: {service_number}',
            f'Interface: {interface}',
            f'Automatic reboot attempt started.',
            f'TimeStamp: {current_datetime}'
        ])

        return_body = {
                        'body': 'Success',
                        'status': 200
        }
        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)
        bruin_repository.append_note_to_ticket = CoroutineMock(return_value=return_body)

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)
        with patch.object(bruin_repository_module, 'datetime', new=datetime_mock):
            results = await bruin_repository.append_digi_reboot_note(ticket_id, service_number, interface)

        bruin_repository.append_note_to_ticket.assert_awaited_once_with(ticket_id, ticket_note,
                                                                        service_numbers=[service_number])
        assert results == return_body

    @pytest.mark.asyncio
    async def append_task_result_change_note_test(self):
        current_datetime = datetime.now()
        ticket_id = 11111
        task_result = "Wireless Repair Intervention Needed"
        ticket_note = os.linesep.join([
            f"#*MetTel's IPA*#",
            f'DiGi reboot failed',
            f'Moving task to: {task_result}',
            f'TimeStamp: {current_datetime}'
        ])

        return_body = {
                        'body': 'Success',
                        'status': 200
        }
        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)
        bruin_repository.append_note_to_ticket = CoroutineMock(return_value=return_body)

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)
        with patch.object(bruin_repository_module, 'datetime', new=datetime_mock):
            results = await bruin_repository.append_task_result_change_note(ticket_id, task_result)

        bruin_repository.append_note_to_ticket.assert_awaited_once_with(ticket_id, ticket_note)

        assert results == return_body

    @pytest.mark.asyncio
    async def append_asr_forwarding_note_test(self):
        current_datetime = datetime.now()
        ticket_id = 11111
        serial_number = 'VC1234567'

        links = [
            {
                'displayName': 'Travis Touchdown',
                'interface': 'GE1',
                'linkState': 'DISCONNECTED',
                'linkId': 5293,
            },
            {
                'displayName': 'Claire Redfield',
                'interface': 'GE2',
                'linkState': 'DISCONNECTED',
                'linkId': 5294,
            },
        ]
        task_result_note = os.linesep.join([
            f"#*MetTel's IPA*#",
            f'Status of Wired Link GE1 (Travis Touchdown) is DISCONNECTED.',
            f'Status of Wired Link GE2 (Claire Redfield) is DISCONNECTED.',
            f'Moving task to: ASR Investigate',
            f'TimeStamp: {current_datetime}'
        ])
        return_body = {
            'body': 'Success',
            'status': 200
        }
        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)
        bruin_repository.append_note_to_ticket = CoroutineMock(return_value=return_body)

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)
        with patch.object(bruin_repository_module, 'datetime', new=datetime_mock):
            results = await bruin_repository.append_asr_forwarding_note(ticket_id, links, serial_number)

        bruin_repository.append_note_to_ticket.assert_awaited_once_with(
            ticket_id, task_result_note, service_numbers=[serial_number]
        )
        assert results == return_body

    @pytest.mark.asyncio
    async def change_ticket_severity_for_offline_edge_test(self):
        ticket_id = 12345
        severity_level = testconfig.MONITOR_CONFIG['severity_by_outage_type']['edge_down']
        reason_for_change = os.linesep.join([
            "#*MetTel's IPA*#",
            f'Changing to Severity {severity_level}',
            'Edge Status: Offline',
        ])

        logger = Mock()
        config = testconfig
        notifications_repository = Mock()
        event_bus = Mock()

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)
        bruin_repository.change_ticket_severity = CoroutineMock()

        await bruin_repository.change_ticket_severity_for_offline_edge(ticket_id)

        bruin_repository.change_ticket_severity.assert_awaited_once_with(ticket_id, severity_level, reason_for_change)

    @pytest.mark.asyncio
    async def change_ticket_severity_for_disconnected_links_test(self):
        link_1_interface = 'REX'
        link_2_interface = 'RAY'
        links = [
            link_1_interface,
            link_2_interface,
        ]

        ticket_id = 12345
        severity_level = testconfig.MONITOR_CONFIG['severity_by_outage_type']['link_down']
        reason_for_change = os.linesep.join([
            "#*MetTel's IPA*#",
            f'Changing to Severity {severity_level}',
            'Edge Status: Online',
            'Interface REX Status: Disconnected',
            'Interface RAY Status: Disconnected',
        ])

        logger = Mock()
        config = testconfig
        notifications_repository = Mock()
        event_bus = Mock()

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)
        bruin_repository.change_ticket_severity = CoroutineMock()

        await bruin_repository.change_ticket_severity_for_disconnected_links(ticket_id, links)

        bruin_repository.change_ticket_severity.assert_awaited_once_with(ticket_id, severity_level, reason_for_change)
