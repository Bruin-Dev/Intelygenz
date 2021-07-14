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
    async def get_tickets_with_no_service_number_specified_test(self):
        bruin_client_id = 12345
        ticket_statuses = ['New', 'InProgress', 'Draft']
        ticket_topic = "VAS"

        request = {
            'request_id': uuid_,
            'body': {
                'client_id': bruin_client_id,
                'ticket_statuses': ticket_statuses,
                'product_category': 'SD-WAN',
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
                'product_category': 'SD-WAN',
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
                'product_category': 'SD-WAN',
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
                'product_category': 'SD-WAN',
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
    async def get_affecting_tickets_with_no_service_number_specified_test(self):
        bruin_client_id = 12345
        ticket_statuses = ['New', 'InProgress', 'Draft']
        ticket_topic = "VAS"

        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)
        bruin_repository.get_tickets = CoroutineMock()

        with uuid_mock:
            await bruin_repository.get_affecting_tickets(bruin_client_id, ticket_statuses)

        bruin_repository.get_tickets.assert_awaited_once_with(
            bruin_client_id, ticket_topic, ticket_statuses, service_number=None
        )

    @pytest.mark.asyncio
    async def get_affecting_tickets_test(self):
        bruin_client_id = 12345
        service_number = 'VC1234567'
        ticket_statuses = ['New', 'InProgress', 'Draft']
        ticket_topic = "VAS"

        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)
        bruin_repository.get_tickets = CoroutineMock()

        await bruin_repository.get_affecting_tickets(bruin_client_id, ticket_statuses, service_number=service_number)

        bruin_repository.get_tickets.assert_awaited_once_with(
            bruin_client_id, ticket_topic, ticket_statuses, service_number=service_number
        )

    @pytest.mark.asyncio
    async def get_open_affecting_tickets_with_no_service_number_specified_test(self):
        bruin_client_id = 12345
        ticket_statuses = ['New', 'InProgress', 'Draft']

        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)
        bruin_repository.get_affecting_tickets = CoroutineMock()

        with uuid_mock:
            await bruin_repository.get_open_affecting_tickets(bruin_client_id)

        bruin_repository.get_affecting_tickets.assert_awaited_once_with(
            bruin_client_id, ticket_statuses, service_number=None
        )

    @pytest.mark.asyncio
    async def get_open_affecting_tickets_test(self):
        bruin_client_id = 12345
        service_number = 'VC1234567'
        ticket_statuses = ['New', 'InProgress', 'Draft']

        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)
        bruin_repository.get_affecting_tickets = CoroutineMock()

        with uuid_mock:
            await bruin_repository.get_open_affecting_tickets(bruin_client_id, service_number=service_number)

        bruin_repository.get_affecting_tickets.assert_awaited_once_with(
            bruin_client_id, ticket_statuses, service_number=service_number
        )

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
    async def unpause_ticket_detail_test(self):
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
            result = await bruin_repository.unpause_ticket_detail(ticket_id, service_number)

        bruin_repository._event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.unpause", request, timeout=30)
        assert result == response

    @pytest.mark.asyncio
    async def unpause_ticket_detail_with_rpc_request_failing_test(self):
        ticket_id = 12345
        service_number = 'VC1234567'

        request = {
            'request_id': uuid_,
            'body': {
                'ticket_id': ticket_id,
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
            result = await bruin_repository.unpause_ticket_detail(ticket_id, service_number)

        bruin_repository._event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.unpause", request, timeout=30)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def unpause_ticket_detail_with_rpc_request_returning_non_2xx_status_test(self):
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
            result = await bruin_repository.unpause_ticket_detail(ticket_id, service_number)

        bruin_repository._event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.unpause", request, timeout=30)
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
            result = await bruin_repository.change_detail_work_queue(service_number=service_number,
                                                                     ticket_id=ticket_id,
                                                                     detail_id=detail_id,
                                                                     task_result=task_result)

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.change.work", request, timeout=90)
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
            result = await bruin_repository.change_detail_work_queue(service_number=service_number,
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
            result = await bruin_repository.change_detail_work_queue(service_number=service_number,
                                                                     ticket_id=ticket_id,
                                                                     detail_id=detail_id,
                                                                     task_result=task_result)

        event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.change.work", request, timeout=90)
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
    async def change_detail_work_queue_to_hnoc_test(self):
        ticket_id = 12345
        detail_id = 67890
        task_result = "HNOC Investigate"
        service_number = 'VC1234567'

        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        bruin_repository = BruinRepository(event_bus, logger, config, notifications_repository)
        bruin_repository.change_detail_work_queue = CoroutineMock()

        await bruin_repository.change_detail_work_queue_to_hnoc(ticket_id=ticket_id,
                                                                service_number=service_number,
                                                                detail_id=detail_id)

        bruin_repository.change_detail_work_queue.assert_awaited_once_with(
            ticket_id=ticket_id, task_result=task_result, service_number=service_number, detail_id=detail_id
        )

    @pytest.mark.asyncio
    async def append_autoresolve_note_to_ticket_test(self):
        serial_number = 'VC1234567'

        current_datetime = datetime.now()
        ticket_id = 11111
        ticket_note = (
            "#*MetTel's IPA*#\n"
            'All Service Affecting conditions (Jitter, Packet Loss, Latency and Utilization) have stabilized.\n'
            f'Auto-resolving task for serial: {serial_number}\n'
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

    @pytest.mark.asyncio
    async def get_affecting_ticket_by_trouble_ok_test(self):
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
    async def get_affecting_ticket_by_trouble_error_get_tickets_details_test(self):
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

        assert affecting_ticket == {}
        assert event_bus.rpc_request.called

    @pytest.mark.asyncio
    async def get_ticket_details_test(self, service_affecting_monitor_reports, ticket_1, ticket_details_1):
        response_ticket_details_1 = {
            'body': ticket_details_1,
            'status': 200
        }
        expected_response = {
            "ticket": ticket_1,
            "ticket_details": ticket_details_1
        }
        service_affecting_monitor_reports._bruin_repository._event_bus.rpc_request = CoroutineMock(
            side_effect=[response_ticket_details_1])
        response = await service_affecting_monitor_reports._bruin_repository._get_ticket_details(ticket_1)
        assert response == expected_response

    @pytest.mark.asyncio
    async def get_ticket_details_400_test(self, service_affecting_monitor_reports, ticket_1):
        response_ticket_details_1 = {
            'body': "Some error",
            'status': 400
        }
        expected_response = None
        service_affecting_monitor_reports._bruin_repository._event_bus.rpc_request = CoroutineMock(
            side_effect=[response_ticket_details_1])
        service_affecting_monitor_reports._notifications_repository.send_slack_message = CoroutineMock()

        response = await service_affecting_monitor_reports._bruin_repository._get_ticket_details(ticket_1)

        assert response == expected_response

    @pytest.mark.asyncio
    async def get_ticket_details_401_and_or_403_test(self, service_affecting_monitor_reports, ticket_1):
        response_ticket_details_1 = {
            'body': "Some error",
            'status': 401
        }
        slack_msg = f"[service-affecting-monitor-reports]" \
                    f"Max retries reached getting ticket details {ticket_1['ticketID']}"
        expected_response = None
        service_affecting_monitor_reports._notifications_repository.send_slack_message = CoroutineMock()
        service_affecting_monitor_reports._bruin_repository.get_ticket_details = CoroutineMock(
            side_effect=[response_ticket_details_1])
        service_affecting_monitor_reports._notifications_repository.send_slack_message = CoroutineMock()

        response = await service_affecting_monitor_reports._bruin_repository._get_ticket_details(ticket_1)

        assert response == expected_response

        service_affecting_monitor_reports._notifications_repository.send_slack_message. \
            assert_awaited_once_with(slack_msg)

    @pytest.mark.asyncio
    async def get_affecting_ticket_for_report_test(self, service_affecting_monitor_reports,
                                                   response_bruin_with_all_tickets,
                                                   response_bruin_with_all_tickets_without_details, report,
                                                   ticket_1, ticket_details_1, ticket_2, ticket_details_2,
                                                   ticket_3, ticket_details_3, ticket_4, ticket_details_4):
        start_date = 'start_date'
        end_date = 'end_date'
        ticket_statuses = ['New', 'InProgress', 'Draft', 'Resolved', 'Closed']
        responses_get_ticket_details = [
            {
                "ticket": ticket_1,
                "ticket_details": ticket_details_1
            },
            {
                "ticket": ticket_2,
                "ticket_details": ticket_details_2
            },
            {
                "ticket": ticket_3,
                "ticket_details": ticket_details_3
            },
            {
                "ticket": ticket_4,
                "ticket_details": ticket_details_4
            }
        ]
        service_affecting_monitor_reports._bruin_repository.get_all_affecting_tickets = CoroutineMock(
            side_effect=[response_bruin_with_all_tickets_without_details])

        with uuid_mock:
            with patch.object(asyncio, 'gather', new=CoroutineMock(side_effect=[responses_get_ticket_details])):
                response = await service_affecting_monitor_reports._bruin_repository.get_affecting_ticket_for_report(
                    report['client_id'], start_date, end_date)

        assert response == response_bruin_with_all_tickets

        service_affecting_monitor_reports._bruin_repository.get_all_affecting_tickets.assert_has_awaits([
            call(client_id=report['client_id'], end_date=end_date, start_date=start_date,
                 ticket_statuses=ticket_statuses)
        ])

    @pytest.mark.asyncio
    async def get_affecting_ticket_for_report_no_tickets_test(self, service_affecting_monitor_reports, report,
                                                              response_bruin_with_no_tickets):
        start_date = 'start_date'
        end_date = 'end_date'
        ticket_statuses = ['New', 'InProgress', 'Draft', 'Resolved', 'Closed']
        ticket_request_msg = {
            'request_id': uuid_,
            'body': {
                'client_id': report['client_id'],
                'category': 'SD-WAN',
                'ticket_topic': 'VAS',
                'start_date': start_date,
                'end_date': end_date,
                'ticket_status': ticket_statuses
            }
        }

        responses_get_ticket_details = []
        service_affecting_monitor_reports._bruin_repository._event_bus.rpc_request = CoroutineMock(
            side_effect=[response_bruin_with_no_tickets])

        with uuid_mock:
            with patch.object(asyncio, 'gather', new=CoroutineMock(side_effect=[responses_get_ticket_details])):
                response = await service_affecting_monitor_reports._bruin_repository.get_affecting_ticket_for_report(
                    report['client_id'], start_date, end_date)

        assert response is None

        service_affecting_monitor_reports._bruin_repository._event_bus.rpc_request.assert_has_awaits([
            call("bruin.ticket.request", ticket_request_msg, timeout=90)
        ])

    @pytest.mark.asyncio
    async def get_affecting_ticket_for_report_retries_test(self, service_affecting_monitor_reports, report,
                                                           response_bruin_401, response_bruin_403):
        start_date = 'start_date'
        end_date = 'end_date'
        ticket_statuses = ['New', 'InProgress', 'Draft', 'Resolved', 'Closed']
        ticket_request_msg = {
            'request_id': uuid_,
            'body': {
                'client_id': report['client_id'],
                'category': 'SD-WAN',
                'ticket_topic': 'VAS',
                'start_date': start_date,
                'end_date': end_date,
                'ticket_status': ticket_statuses
            }
        }
        slack_msg = f"Max retries reached getting all tickets for the service affecting monitor process."

        responses_get_ticket_details = []
        service_affecting_monitor_reports._bruin_repository._event_bus.rpc_request = CoroutineMock(
            side_effect=[response_bruin_403, response_bruin_401, response_bruin_403])
        service_affecting_monitor_reports._notifications_repository.send_slack_message = CoroutineMock()

        with uuid_2_mock:
            with uuid_mock:
                with patch.object(asyncio, 'gather', new=CoroutineMock(side_effect=[responses_get_ticket_details])):
                    response = \
                        await service_affecting_monitor_reports._bruin_repository.get_affecting_ticket_for_report(
                            report['client_id'], start_date, end_date)

        assert response is None

        service_affecting_monitor_reports._bruin_repository._event_bus.rpc_request.assert_has_awaits([
            call("bruin.ticket.request", ticket_request_msg, timeout=90),
            call("bruin.ticket.request", ticket_request_msg, timeout=90)
        ])
        service_affecting_monitor_reports._notifications_repository.send_slack_message.assert_awaited_once_with(
            slack_msg)

    @pytest.mark.asyncio
    async def get_affecting_ticket_for_report_with_error_test(self, bruin_repository, report,
                                                              response_bruin_with_error):
        start_date = 'start_date'
        end_date = 'end_date'
        ticket_statuses = ['New', 'InProgress', 'Draft', 'Resolved', 'Closed']
        ticket_request_msg = {
            'request_id': uuid_,
            'body': {
                'client_id': report['client_id'],
                'category': 'SD-WAN',
                'ticket_topic': 'VAS',
                'start_date': start_date,
                'end_date': end_date,
                'ticket_status': ticket_statuses
            }
        }
        responses_get_ticket_details = []
        bruin_repository._event_bus.rpc_request = CoroutineMock(
            side_effect=[response_bruin_with_error])

        with uuid_mock:
            with patch.object(asyncio, 'gather', new=CoroutineMock(side_effect=[responses_get_ticket_details])):
                response = await bruin_repository.get_affecting_ticket_for_report(report['client_id'], start_date,
                                                                                  end_date)

        assert response is None

        bruin_repository._event_bus.rpc_request.assert_has_awaits([
            call("bruin.ticket.request", ticket_request_msg, timeout=90)
        ])
