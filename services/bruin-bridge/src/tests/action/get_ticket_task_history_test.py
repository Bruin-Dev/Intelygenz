from unittest.mock import AsyncMock, Mock

import pytest
from application.actions.get_ticket_task_history import GetTicketTaskHistory
from application.repositories.utils_repository import to_json_bytes
from nats.aio.msg import Msg


class TestGetTicketTaskHistory:
    def instance_test(self):
        bruin_repository = Mock()

        bruin_ticket_task_history = GetTicketTaskHistory(bruin_repository)

        assert bruin_ticket_task_history._bruin_repository is bruin_repository

    @pytest.mark.asyncio
    async def get_ticket_task_history_ok_test(self):
        return_body = {"results": ["Good"]}
        return_status = 200
        bruin_repository_task_history_return = {"body": return_body, "status": return_status}
        bruin_repository = Mock()
        bruin_repository.get_ticket_task_history = AsyncMock(return_value=bruin_repository_task_history_return)

        ticket_id = 321

        msg = {"body": {"ticket_id": ticket_id}}

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg)

        bruin_ticket_task_history = GetTicketTaskHistory(bruin_repository)

        await bruin_ticket_task_history(request_msg)

        request_msg.respond.assert_awaited_once_with(to_json_bytes({"body": return_body, "status": return_status}))

    @pytest.mark.asyncio
    async def get_ticket_task_history_ko_no_ticket_id_test(self):
        return_body = 'You must specify "ticket_id" in the body'
        return_status = 400

        bruin_repository = Mock()
        bruin_repository.get_ticket_task_history = AsyncMock()

        msg = {"body": {}}

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg)

        bruin_ticket_task_history = GetTicketTaskHistory(bruin_repository)

        await bruin_ticket_task_history(request_msg)

        request_msg.respond.assert_awaited_once_with(to_json_bytes({"body": return_body, "status": return_status}))

    @pytest.mark.asyncio
    async def get_ticket_task_history_ko_no_body_test(self):
        return_body = 'You must specify {.."body":{"ticket_id"}...} in the request'
        return_status = 400

        bruin_repository = Mock()
        bruin_repository.get_ticket_task_history = AsyncMock()

        msg = {}

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg)

        bruin_ticket_task_history = GetTicketTaskHistory(bruin_repository)

        await bruin_ticket_task_history(request_msg)

        request_msg.respond.assert_awaited_once_with(to_json_bytes({"body": return_body, "status": return_status}))
