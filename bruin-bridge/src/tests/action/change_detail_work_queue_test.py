import json
from unittest.mock import Mock

import pytest
from application.actions.change_detail_work_queue import ChangeDetailWorkQueue
from asynctest import CoroutineMock


class TestChangeDetailWorkQueue:

    def instance_test(self):
        logger = Mock()
        event_bus = Mock()
        bruin_repository = Mock()

        change_detail_work_queue = ChangeDetailWorkQueue(logger, event_bus, bruin_repository)

        assert change_detail_work_queue._logger is logger
        assert change_detail_work_queue._event_bus is event_bus
        assert change_detail_work_queue._bruin_repository is bruin_repository

    @pytest.mark.asyncio
    async def change_detail_work_queue_ok_test(self):
        logger = Mock()
        logger.info = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        bruin_repository = Mock()

        put_response = {
            "body": {
                "message": "success"
            },
            "status": 200
        }
        bruin_repository.change_detail_work_queue = CoroutineMock(return_value=put_response)

        ticket_id = 4503440
        msg_body = {
            "service_number": "VC05400002265",
            "ticket_id": ticket_id,
            "detail_id": 4806634,
            "queue_name": "Repair Completed",
        }
        filters = {
            "service_number": "VC05400002265",
            "detail_id": 4806634,
            "queue_name": "Repair Completed",
        }

        event_bus_request = {
            "request_id": 19,
            "body": msg_body,
            "response_topic": "some.topic"
        }

        event_bus_response = {
            "request_id": 19,
            **put_response,
        }

        change_detail_work_queue = ChangeDetailWorkQueue(logger, event_bus, bruin_repository)
        await change_detail_work_queue.change_detail_work_queue(event_bus_request)
        bruin_repository.change_detail_work_queue.assert_awaited_once_with(ticket_id, filters=filters)
        event_bus.publish_message.assert_awaited_once_with("some.topic", event_bus_response)

    @pytest.mark.asyncio
    async def change_detail_work_queue_400_no_body_test(self):
        logger = Mock()
        logger.error = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        bruin_repository = Mock()

        event_bus_request = {
            "request_id": 19,
            "response_topic": "some.topic"
        }

        event_bus_response = {
            "request_id": 19,
            "body": (
                'You must specify {.."body": {"service_number", "ticket_id", "detail_id", "queue_name"}..} '
                'in the request'
            ),
            'status': 400
        }

        change_detail_work_queue = ChangeDetailWorkQueue(logger, event_bus, bruin_repository)
        await change_detail_work_queue.change_detail_work_queue(event_bus_request)
        event_bus.publish_message.assert_awaited_once_with("some.topic", event_bus_response)
        logger.error.assert_called()

    @pytest.mark.asyncio
    async def change_detail_work_queue_400_body_with_not_all_filters_test(self):
        logger = Mock()
        logger.error = Mock()
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        bruin_repository = Mock()

        filters = {
            "service_number": "VC05400002265",
            "detail_id": 4806634,
            "queue_name": "Repair Completed",
        }

        event_bus_request = {
            "request_id": 19,
            "body": filters,
            "response_topic": "some.topic"
        }

        event_bus_response = {
            "request_id": 19,
            "body": (
                'You must specify {.."body": {"service_number" or "detail_id", "ticket_id", "queue_name"}..} '
                'in the request'
            ),
            'status': 400
        }

        change_detail_work_queue = ChangeDetailWorkQueue(logger, event_bus, bruin_repository)
        await change_detail_work_queue.change_detail_work_queue(event_bus_request)
        event_bus.publish_message.assert_awaited_once_with("some.topic", event_bus_response)
        logger.error.assert_called()
