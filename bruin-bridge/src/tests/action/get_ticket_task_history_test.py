from unittest.mock import Mock

import pytest
from application.actions.get_ticket_task_history import GetTicketTaskHistory
from asynctest import CoroutineMock


class TestGetTicketTaskHistory:

    def instance_test(self):
        logger = Mock()
        event_bus = Mock()
        bruin_repository = Mock()

        bruin_ticket_task_history = GetTicketTaskHistory(logger, event_bus, bruin_repository)

        assert bruin_ticket_task_history._logger is logger
        assert bruin_ticket_task_history._event_bus is event_bus
        assert bruin_ticket_task_history._bruin_repository is bruin_repository

    @pytest.mark.asyncio
    async def get_ticket_task_history_ok_test(self):
        logger = Mock()

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        return_body = {'results': ['Good']}
        return_status = 200
        bruin_repository_task_history_return = {'body': return_body,
                                                'status': return_status}
        bruin_repository = Mock()
        bruin_repository.get_ticket_task_history = Mock(return_value=bruin_repository_task_history_return)

        request_id = "123"
        response_topic = "_INBOX.2007314fe0fcb2cdc2a2914c1"
        ticket_id = 321

        msg = {
                'request_id': request_id,
                'body': {'ticket_id': ticket_id},
                'response_topic': response_topic
        }
        bruin_ticket_task_history = GetTicketTaskHistory(logger, event_bus, bruin_repository)

        await bruin_ticket_task_history.get_ticket_task_history(msg)

        event_bus.publish_message.assert_awaited_once_with(response_topic, dict(request_id=request_id,
                                                                                body=return_body,
                                                                                status=return_status))

    @pytest.mark.asyncio
    async def get_ticket_task_history_ko_no_ticket_id_test(self):
        logger = Mock()

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        return_body = 'You must specify "ticket_id" in the body'
        return_status = 400

        bruin_repository = Mock()
        bruin_repository.get_ticket_task_history = Mock()

        request_id = "123"
        response_topic = "_INBOX.2007314fe0fcb2cdc2a2914c1"

        msg = {
                'request_id': request_id,
                'body': {},
                'response_topic': response_topic
        }
        bruin_ticket_task_history = GetTicketTaskHistory(logger, event_bus, bruin_repository)

        await bruin_ticket_task_history.get_ticket_task_history(msg)

        event_bus.publish_message.assert_awaited_once_with(response_topic, dict(request_id=request_id,
                                                                                body=return_body,
                                                                                status=return_status))

    @pytest.mark.asyncio
    async def get_ticket_task_history_ko_no_body_test(self):
        logger = Mock()

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        return_body = 'You must specify {.."body":{"ticket_id"}...} in the request'
        return_status = 400

        bruin_repository = Mock()
        bruin_repository.get_ticket_task_history = Mock()

        request_id = "123"
        response_topic = "_INBOX.2007314fe0fcb2cdc2a2914c1"

        msg = {
                'request_id': request_id,
                'response_topic': response_topic
        }
        bruin_ticket_task_history = GetTicketTaskHistory(logger, event_bus, bruin_repository)

        await bruin_ticket_task_history.get_ticket_task_history(msg)

        event_bus.publish_message.assert_awaited_once_with(response_topic, dict(request_id=request_id,
                                                                                body=return_body,
                                                                                status=return_status))
