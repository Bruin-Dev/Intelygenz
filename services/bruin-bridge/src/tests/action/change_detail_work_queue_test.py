from unittest.mock import AsyncMock, Mock

import pytest
from application.actions.change_detail_work_queue import ChangeDetailWorkQueue
from application.repositories.utils_repository import to_json_bytes
from nats.aio.msg import Msg


class TestChangeDetailWorkQueue:
    def instance_test(self):
        bruin_repository = Mock()

        change_detail_work_queue = ChangeDetailWorkQueue(bruin_repository)

        assert change_detail_work_queue._bruin_repository is bruin_repository

    @pytest.mark.asyncio
    async def change_detail_work_queue_ok_test(self):
        bruin_repository = Mock()

        put_response = {"body": {"message": "success"}, "status": 200}
        bruin_repository.change_detail_work_queue = AsyncMock(return_value=put_response)

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

        event_bus_request = {"body": msg_body}

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(event_bus_request)

        event_bus_response = {
            **put_response,
        }

        change_detail_work_queue = ChangeDetailWorkQueue(bruin_repository)
        await change_detail_work_queue(request_msg)
        bruin_repository.change_detail_work_queue.assert_awaited_once_with(ticket_id, filters=filters)
        request_msg.respond.assert_awaited_once_with(to_json_bytes(event_bus_response))

    @pytest.mark.asyncio
    async def change_detail_work_queue_400_no_body_test(self):
        bruin_repository = Mock()

        event_bus_request = {}

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(event_bus_request)

        event_bus_response = {
            "body": (
                'You must specify {.."body": {"service_number", "ticket_id", "detail_id", "queue_name"}..} '
                "in the request"
            ),
            "status": 400,
        }

        change_detail_work_queue = ChangeDetailWorkQueue(bruin_repository)
        await change_detail_work_queue(request_msg)
        request_msg.respond.assert_awaited_once_with(to_json_bytes(event_bus_response))

    @pytest.mark.asyncio
    async def change_detail_work_queue_400_body_with_not_all_filters_test(self):
        bruin_repository = Mock()

        filters = {
            "service_number": "VC05400002265",
            "detail_id": 4806634,
            "queue_name": "Repair Completed",
        }

        event_bus_request = {"body": filters}

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(event_bus_request)

        event_bus_response = {
            "body": (
                'You must specify {.."body": {"service_number" or "detail_id", "ticket_id", "queue_name"}..} '
                "in the request"
            ),
            "status": 400,
        }

        change_detail_work_queue = ChangeDetailWorkQueue(bruin_repository)
        await change_detail_work_queue(request_msg)
        request_msg.respond.assert_awaited_once_with(to_json_bytes(event_bus_response))
