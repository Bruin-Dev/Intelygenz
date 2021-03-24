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
    def instance_test(self, bruin_repository, event_bus, logger, notifications_repository):
        assert bruin_repository._event_bus is event_bus
        assert bruin_repository._logger is logger
        assert bruin_repository._config is testconfig
        assert bruin_repository._notifications_repository is notifications_repository

    @pytest.mark.asyncio
    async def get_tickets_test(self, bruin_repository, make_rpc_request, make_rpc_response, open_affecting_ticket):
        bruin_client_id = 12345
        ticket_statuses = ['New', 'InProgress', 'Draft']
        ticket_topic = "VAS"

        request = make_rpc_request(
            request_id=uuid_,
            client_id=bruin_client_id,
            ticket_status=ticket_statuses,
            category='SD-WAN',
            ticket_topic=ticket_topic,
        )
        response = make_rpc_response(request_id=uuid_, body=[open_affecting_ticket], status=200)

        bruin_repository._event_bus.rpc_request.return_value = response

        with uuid_mock:
            result = await bruin_repository.get_tickets(bruin_client_id, ticket_topic, ticket_statuses)

        bruin_repository._event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.request", request, timeout=90)
        assert result == response

    @pytest.mark.asyncio
    async def get_tickets_with_rpc_request_failing_test(self, bruin_repository, make_rpc_request):
        bruin_client_id = 12345
        ticket_statuses = ['New', 'InProgress', 'Draft']
        ticket_topic = "VAS"

        request = make_rpc_request(
            request_id=uuid_,
            client_id=bruin_client_id,
            ticket_status=ticket_statuses,
            category='SD-WAN',
            ticket_topic=ticket_topic,
        )

        bruin_repository._event_bus.rpc_request.side_effect = Exception
        bruin_repository._notifications_repository.send_slack_message = CoroutineMock()

        with uuid_mock:
            result = await bruin_repository.get_tickets(bruin_client_id, ticket_topic, ticket_statuses)

        bruin_repository._event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.request", request, timeout=90)
        bruin_repository._notifications_repository.send_slack_message.assert_awaited_once()
        bruin_repository._logger.error.assert_called_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_tickets_with_rpc_request_returning_non_2xx_status_test(self, bruin_repository, make_rpc_request,
                                                                         make_rpc_response):
        bruin_client_id = 12345
        ticket_statuses = ['New', 'InProgress', 'Draft']
        ticket_topic = "VAS"

        request = make_rpc_request(
            request_id=uuid_,
            client_id=bruin_client_id,
            ticket_status=ticket_statuses,
            category='SD-WAN',
            ticket_topic=ticket_topic,
        )
        response = make_rpc_response(
            request_id=uuid_,
            body='Got internal error from Bruin',
            status=500,
        )

        bruin_repository._event_bus.rpc_request.return_value = response
        bruin_repository._notifications_repository.send_slack_message = CoroutineMock()

        with uuid_mock:
            result = await bruin_repository.get_tickets(bruin_client_id, ticket_topic, ticket_statuses)

        bruin_repository._event_bus.rpc_request.assert_awaited_once_with("bruin.ticket.request", request, timeout=90)
        bruin_repository._notifications_repository.send_slack_message.assert_awaited_once()
        bruin_repository._logger.error.assert_called_once()
        assert result == response

    @pytest.mark.asyncio
    async def get_ticket_details_test(self, bruin_repository, make_rpc_request, make_rpc_response,
                                      make_in_progress_ticket_detail, make_ticket_note, serial_number_1):
        ticket_id = 11111

        request = make_rpc_request(request_id=uuid_, ticket_id=ticket_id)

        ticket_detail_1 = make_in_progress_ticket_detail(serial_number=serial_number_1)
        ticket_note_1 = make_ticket_note(serial_number=serial_number_1)
        ticket_note_2 = make_ticket_note(serial_number=serial_number_1)
        response = make_rpc_response(
            request_id=uuid_,
            body={
                'ticketDetails': [ticket_detail_1],
                'ticketNotes': [ticket_note_1, ticket_note_2]
            },
            status=200,
        )

        bruin_repository._event_bus.rpc_request.return_value = response

        with uuid_mock:
            result = await bruin_repository.get_ticket_details(ticket_id)

        bruin_repository._event_bus.rpc_request.assert_awaited_once_with(
            "bruin.ticket.details.request", request, timeout=15
        )
        assert result == response

    @pytest.mark.asyncio
    async def get_ticket_details_with_rpc_request_failing_test(self, bruin_repository, make_rpc_request):
        ticket_id = 11111
        request = make_rpc_request(request_id=uuid_, ticket_id=ticket_id)

        bruin_repository._event_bus.rpc_request.side_effect = Exception
        bruin_repository._notifications_repository.send_slack_message = CoroutineMock()

        with uuid_mock:
            result = await bruin_repository.get_ticket_details(ticket_id)

        bruin_repository._event_bus.rpc_request.assert_awaited_once_with(
            "bruin.ticket.details.request", request, timeout=15
        )
        bruin_repository._notifications_repository.send_slack_message.assert_awaited_once()
        bruin_repository._logger.error.assert_called_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_ticket_details_with_rpc_request_returning_non_2xx_status_test(self, bruin_repository,
                                                                                make_rpc_request, make_rpc_response):
        ticket_id = 11111

        request = make_rpc_request(request_id=uuid_, ticket_id=ticket_id)
        response = make_rpc_response(
            request_id=uuid_,
            body='Got internal error from Bruin',
            status=500,
        )

        bruin_repository._event_bus.rpc_request.return_value = response
        bruin_repository._notifications_repository.send_slack_message = CoroutineMock()

        with uuid_mock:
            result = await bruin_repository.get_ticket_details(ticket_id)

        bruin_repository._event_bus.rpc_request.assert_awaited_once_with(
            "bruin.ticket.details.request", request, timeout=15
        )
        bruin_repository._notifications_repository.send_slack_message.assert_awaited_once()
        bruin_repository._logger.error.assert_called_once()
        assert result == response

    @pytest.mark.asyncio
    async def get_ticket_task_history_test(self, bruin_repository, make_task_history_item, make_task_history,
                                           make_rpc_request, make_rpc_response, serial_number_1, serial_number_2):
        ticket_id = 11111

        request = make_rpc_request(request_id=uuid_, ticket_id=ticket_id)

        task_history_item_1 = make_task_history_item(serial_number=serial_number_1)
        task_history_item_2 = make_task_history_item(serial_number=serial_number_2)
        task_history = make_task_history(task_history_item_1, task_history_item_2)
        response = make_rpc_response(
            request_id=uuid_,
            body=task_history,
            status=200,
        )

        bruin_repository._event_bus.rpc_request.return_value = response

        with uuid_mock:
            result = await bruin_repository.get_ticket_task_history(ticket_id)

        bruin_repository._event_bus.rpc_request.assert_awaited_once_with(
            "bruin.ticket.get.task.history", request, timeout=15
        )
        assert result == response

    @pytest.mark.asyncio
    async def get_ticket_task_history_with_rpc_request_failing_test(self, bruin_repository, make_rpc_request):
        ticket_id = 11111
        request = make_rpc_request(request_id=uuid_, ticket_id=ticket_id)

        bruin_repository._event_bus.rpc_request.side_effect = Exception
        bruin_repository._notifications_repository.send_slack_message = CoroutineMock()

        with uuid_mock:
            result = await bruin_repository.get_ticket_task_history(ticket_id)

        bruin_repository._event_bus.rpc_request.assert_awaited_once_with(
            "bruin.ticket.get.task.history", request, timeout=15
        )
        bruin_repository._notifications_repository.send_slack_message.assert_awaited_once()
        bruin_repository._logger.error.assert_called_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_ticket_task_history_with_rpc_request_returning_non_2xx_status_test(self, bruin_repository,
                                                                                     make_rpc_request,
                                                                                     make_rpc_response):
        ticket_id = 11111

        request = make_rpc_request(request_id=uuid_, ticket_id=ticket_id)
        response = make_rpc_response(
            request_id=uuid_,
            body='Got internal error from Bruin',
            status=500,
        )

        bruin_repository._event_bus.rpc_request.return_value = response
        bruin_repository._notifications_repository.send_slack_message = CoroutineMock()

        with uuid_mock:
            result = await bruin_repository.get_ticket_task_history(ticket_id)

        bruin_repository._event_bus.rpc_request.assert_awaited_once_with(
            "bruin.ticket.get.task.history", request, timeout=15
        )
        bruin_repository._notifications_repository.send_slack_message.assert_awaited_once()
        bruin_repository._logger.error.assert_called_once()
        assert result == response

    @pytest.mark.asyncio
    async def get_next_results_for_ticket_detail_test(self, bruin_repository, make_rpc_request, make_rpc_response,
                                                      make_next_result_item, make_next_results, serial_number_1):
        ticket_id = 12345
        detail_id = 67890

        request = make_rpc_request(
            request_id=uuid_,
            ticket_id=ticket_id,
            detail_id=detail_id,
            service_number=serial_number_1
        )

        next_result_1 = make_next_result_item(result_name='Holmdel NOC Investigate')
        next_result_2 = make_next_result_item(result_name='No Trouble Found')
        next_results = make_next_results(next_result_1, next_result_2)
        response = make_rpc_response(request_id=uuid_, body=next_results, status=200)

        bruin_repository._event_bus.rpc_request.return_value = response

        with uuid_mock:
            result = await bruin_repository.get_next_results_for_ticket_detail(ticket_id, detail_id, serial_number_1)

        bruin_repository._event_bus.rpc_request.assert_awaited_once_with(
            "bruin.ticket.detail.get.next.results", request, timeout=15
        )
        assert result == response

    @pytest.mark.asyncio
    async def get_next_results_for_ticket_detail_with_rpc_request_failing_test(self, bruin_repository, make_rpc_request,
                                                                               serial_number_1):
        ticket_id = 12345
        detail_id = 67890

        request = make_rpc_request(
            request_id=uuid_,
            ticket_id=ticket_id,
            detail_id=detail_id,
            service_number=serial_number_1
        )

        bruin_repository._event_bus.rpc_request.side_effect = Exception
        bruin_repository._notifications_repository.send_slack_message = CoroutineMock()

        with uuid_mock:
            result = await bruin_repository.get_next_results_for_ticket_detail(ticket_id, detail_id, serial_number_1)

        bruin_repository._event_bus.rpc_request.assert_awaited_once_with(
            "bruin.ticket.detail.get.next.results", request, timeout=15
        )
        bruin_repository._notifications_repository.send_slack_message.assert_awaited_once()
        bruin_repository._logger.error.assert_called_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_next_results_for_ticket_detail_with_rpc_request_returning_non_2xx_status_test(self, bruin_repository,
                                                                                                make_rpc_request,
                                                                                                make_rpc_response,
                                                                                                serial_number_1):
        ticket_id = 12345
        detail_id = 67890

        request = make_rpc_request(
            request_id=uuid_,
            ticket_id=ticket_id,
            detail_id=detail_id,
            service_number=serial_number_1
        )
        response = make_rpc_response(
            request_id=uuid_,
            body='Got internal error from Bruin',
            status=500,
        )

        bruin_repository._event_bus.rpc_request.return_value = response
        bruin_repository._notifications_repository.send_slack_message = CoroutineMock()

        with uuid_mock:
            result = await bruin_repository.get_next_results_for_ticket_detail(ticket_id, detail_id, serial_number_1)

        bruin_repository._event_bus.rpc_request.assert_awaited_once_with(
            "bruin.ticket.detail.get.next.results", request, timeout=15
        )
        bruin_repository._notifications_repository.send_slack_message.assert_awaited_once()
        bruin_repository._logger.error.assert_called_once()
        assert result == response

    @pytest.mark.asyncio
    async def append_multiple_notes_to_ticket_test(self, bruin_repository, make_rpc_request, make_rpc_response,
                                                   make_payload_for_note_append, serial_number_1):
        ticket_id = 12345
        note_1 = make_payload_for_note_append(text='This is ticket note 1', detail_id=123)
        note_2 = make_payload_for_note_append(text='This is ticket note 1', serial_number=serial_number_1)
        note_3 = make_payload_for_note_append(
            text='This is ticket note 1', detail_id=123, serial_number=serial_number_1
        )
        notes = [
            note_1,
            note_2,
            note_3,
        ]

        request = make_rpc_request(request_id=uuid_, ticket_id=ticket_id, notes=notes)
        response = make_rpc_response(request_id=uuid_, body={'ticketNotes': notes}, status=200)

        bruin_repository._event_bus.rpc_request.return_value = response

        with uuid_mock:
            result = await bruin_repository.append_multiple_notes_to_ticket(ticket_id, notes)

        bruin_repository._event_bus.rpc_request.assert_awaited_once_with(
            "bruin.ticket.multiple.notes.append.request", request, timeout=15
        )
        assert result == response

    @pytest.mark.asyncio
    async def append_multiple_notes_to_ticket_with_rpc_request_failing_test(self, bruin_repository, make_rpc_request,
                                                                            make_payload_for_note_append,
                                                                            serial_number_1):
        ticket_id = 12345
        note_1 = make_payload_for_note_append(text='This is ticket note 1', detail_id=123)
        note_2 = make_payload_for_note_append(text='This is ticket note 1', serial_number=serial_number_1)
        note_3 = make_payload_for_note_append(
            text='This is ticket note 1', detail_id=123, serial_number=serial_number_1
        )
        notes = [
            note_1,
            note_2,
            note_3,
        ]

        request = make_rpc_request(request_id=uuid_, ticket_id=ticket_id, notes=notes)

        bruin_repository._event_bus.rpc_request.side_effect = Exception
        bruin_repository._notifications_repository.send_slack_message = CoroutineMock()

        with uuid_mock:
            result = await bruin_repository.append_multiple_notes_to_ticket(ticket_id, notes)

        bruin_repository._event_bus.rpc_request.assert_awaited_once_with(
            "bruin.ticket.multiple.notes.append.request", request, timeout=15
        )
        bruin_repository._notifications_repository.send_slack_message.assert_awaited_once()
        bruin_repository._logger.error.assert_called_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def append_multiple_notes_to_ticket_with_rpc_request_returning_non_2xx_status_test(
            self, bruin_repository, make_rpc_request, make_rpc_response, make_payload_for_note_append, serial_number_1):
        ticket_id = 12345
        note_1 = make_payload_for_note_append(text='This is ticket note 1', detail_id=123)
        note_2 = make_payload_for_note_append(text='This is ticket note 1', serial_number=serial_number_1)
        note_3 = make_payload_for_note_append(
            text='This is ticket note 1', detail_id=123, serial_number=serial_number_1
        )
        notes = [
            note_1,
            note_2,
            note_3,
        ]

        request = make_rpc_request(request_id=uuid_, ticket_id=ticket_id, notes=notes)
        response = make_rpc_response(
            request_id=uuid_,
            body='Got internal error from Bruin',
            status=500,
        )

        bruin_repository._event_bus.rpc_request.return_value = response
        bruin_repository._notifications_repository.send_slack_message = CoroutineMock()

        with uuid_mock:
            result = await bruin_repository.append_multiple_notes_to_ticket(ticket_id, notes)

        bruin_repository._event_bus.rpc_request.assert_awaited_once_with(
            "bruin.ticket.multiple.notes.append.request", request, timeout=15
        )
        bruin_repository._notifications_repository.send_slack_message.assert_awaited_once()
        bruin_repository._logger.error.assert_called_once()
        assert result == response

    @pytest.mark.asyncio
    async def resolve_ticket_detail_test(self, bruin_repository, make_rpc_request, make_rpc_response):
        ticket_id = 12345
        detail_id = 67890

        request = make_rpc_request(request_id=uuid_, ticket_id=ticket_id, detail_id=detail_id)
        response = make_rpc_response(request_id=uuid_, body='ok', status=200)

        bruin_repository._event_bus.rpc_request.return_value = response

        with uuid_mock:
            result = await bruin_repository.resolve_ticket_detail(ticket_id, detail_id)

        bruin_repository._event_bus.rpc_request.assert_awaited_once_with(
            "bruin.ticket.status.resolve", request, timeout=15
        )
        assert result == response

    @pytest.mark.asyncio
    async def resolve_ticket_detail_with_rpc_request_failing_test(self, bruin_repository, make_rpc_request):
        ticket_id = 12345
        detail_id = 67890

        request = make_rpc_request(request_id=uuid_, ticket_id=ticket_id, detail_id=detail_id)

        bruin_repository._event_bus.rpc_request.side_effect = Exception
        bruin_repository._notifications_repository.send_slack_message = CoroutineMock()

        with uuid_mock:
            result = await bruin_repository.resolve_ticket_detail(ticket_id, detail_id)

        bruin_repository._event_bus.rpc_request.assert_awaited_once_with(
            "bruin.ticket.status.resolve", request, timeout=15
        )
        bruin_repository._notifications_repository.send_slack_message.assert_awaited_once()
        bruin_repository._logger.error.assert_called_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def resolve_ticket_detail_with_rpc_request_returning_non_2xx_status_test(self, bruin_repository,
                                                                                   make_rpc_request, make_rpc_response):
        ticket_id = 12345
        detail_id = 67890

        request = make_rpc_request(request_id=uuid_, ticket_id=ticket_id, detail_id=detail_id)
        response = make_rpc_response(
            request_id=uuid_,
            body='Got internal error from Bruin',
            status=500,
        )

        bruin_repository._event_bus.rpc_request.return_value = response
        bruin_repository._notifications_repository.send_slack_message = CoroutineMock()

        with uuid_mock:
            result = await bruin_repository.resolve_ticket_detail(ticket_id, detail_id)

        bruin_repository._event_bus.rpc_request.assert_awaited_once_with(
            "bruin.ticket.status.resolve", request, timeout=15
        )
        bruin_repository._notifications_repository.send_slack_message.assert_awaited_once()
        bruin_repository._logger.error.assert_called_once()
        assert result == response

    @pytest.mark.asyncio
    async def change_detail_work_queue_ok_test(self, bruin_repository, make_rpc_request, make_rpc_response,
                                               serial_number_1):
        ticket_id = 12345
        detail_id = 67890
        task_result = 'Holmdel NOC Investigate'
        serial_number = serial_number_1
        request = make_rpc_request(request_id=uuid_, service_number=serial_number, ticket_id=ticket_id,
                                   detail_id=detail_id, queue_name=task_result)
        response = make_rpc_response(
            request_id=uuid_,
            body='',
            status=200,
        )

        bruin_repository._event_bus.rpc_request.return_value = response
        bruin_repository._notifications_repository.send_slack_message = CoroutineMock()

        with uuid_mock:
            result = await bruin_repository.change_detail_work_queue(serial_number, ticket_id, detail_id, task_result)

        bruin_repository._event_bus.rpc_request.assert_awaited_once_with(
            "bruin.ticket.change.work", request, timeout=90
        )
        bruin_repository._notifications_repository.send_slack_message.assert_not_awaited()
        assert result == response

    @pytest.mark.asyncio
    async def change_detail_work_queue_500_test(self, bruin_repository, make_rpc_request, make_rpc_response,
                                                serial_number_1):
        ticket_id = 12345
        detail_id = 67890
        task_result = 'Holmdel NOC Investigate'
        serial_number = serial_number_1
        request = make_rpc_request(request_id=uuid_, service_number=serial_number, ticket_id=ticket_id,
                                   detail_id=detail_id, queue_name=task_result)
        response = make_rpc_response(
            request_id=uuid_,
            body='',
            status=500,
        )

        bruin_repository._event_bus.rpc_request.return_value = response
        bruin_repository._notifications_repository.send_slack_message = CoroutineMock()

        with uuid_mock:
            result = await bruin_repository.change_detail_work_queue(serial_number, ticket_id, detail_id, task_result)

        bruin_repository._event_bus.rpc_request.assert_awaited_once_with(
            "bruin.ticket.change.work", request, timeout=90
        )
        bruin_repository._notifications_repository.send_slack_message.assert_awaited()
        bruin_repository._logger.error.assert_called()
        assert result == response

    @pytest.mark.asyncio
    async def change_detail_work_queue_exception_test(self, bruin_repository, make_rpc_request, serial_number_1):
        ticket_id = 12345
        detail_id = 67890
        task_result = 'Holmdel NOC Investigate'
        serial_number = serial_number_1
        request = make_rpc_request(request_id=uuid_, service_number=serial_number, ticket_id=ticket_id,
                                   detail_id=detail_id, queue_name=task_result)

        bruin_repository._event_bus.rpc_request.side_effect = Exception
        bruin_repository._notifications_repository.send_slack_message = CoroutineMock()

        with uuid_mock:
            result = await bruin_repository.change_detail_work_queue(serial_number, ticket_id, detail_id, task_result)

        bruin_repository._event_bus.rpc_request.assert_awaited_once_with(
            "bruin.ticket.change.work", request, timeout=90
        )
        bruin_repository._notifications_repository.send_slack_message.assert_awaited()
        bruin_repository._logger.error.assert_called()

    @pytest.mark.asyncio
    async def get_outage_tickets_test(self, bruin_repository):
        bruin_client_id = 12345
        ticket_statuses = ['New', 'InProgress', 'Draft']
        ticket_topic = "VOO"

        bruin_repository.get_tickets = CoroutineMock()

        await bruin_repository.get_outage_tickets(bruin_client_id, ticket_statuses)

        bruin_repository.get_tickets.assert_awaited_once_with(bruin_client_id, ticket_topic, ticket_statuses)

    @pytest.mark.asyncio
    async def get_open_outage_tickets_test(self, bruin_repository):
        bruin_client_id = 12345
        ticket_statuses = ['New', 'InProgress', 'Draft']
        ticket_topic = "VOO"

        bruin_repository.get_tickets = CoroutineMock()

        await bruin_repository.get_open_outage_tickets(bruin_client_id)

        bruin_repository.get_tickets.assert_awaited_once_with(bruin_client_id, ticket_topic, ticket_statuses)

    @pytest.mark.asyncio
    async def get_affecting_tickets_test(self, bruin_repository):
        bruin_client_id = 12345
        ticket_statuses = ['New', 'InProgress', 'Draft']
        ticket_topic = "VAS"

        bruin_repository.get_tickets = CoroutineMock()

        await bruin_repository.get_affecting_tickets(bruin_client_id, ticket_statuses)

        bruin_repository.get_tickets.assert_awaited_once_with(bruin_client_id, ticket_topic, ticket_statuses)

    @pytest.mark.asyncio
    async def get_open_affecting_tickets_test(self, bruin_repository):
        bruin_client_id = 12345
        ticket_statuses = ['New', 'InProgress', 'Draft']
        ticket_topic = "VAS"

        bruin_repository.get_tickets = CoroutineMock()

        await bruin_repository.get_open_affecting_tickets(bruin_client_id)

        bruin_repository.get_tickets.assert_awaited_once_with(bruin_client_id, ticket_topic, ticket_statuses)
