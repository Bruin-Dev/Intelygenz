from unittest.mock import AsyncMock, Mock

import pytest
from nats.aio.msg import Msg

from application.actions.mark_email_as_done import MarkEmailAsDone
from application.repositories.utils_repository import to_json_bytes


class TestMarkEmailAsDone:
    def instance_test(self):
        bruin_repo = Mock()

        mark_email_as_done = MarkEmailAsDone(bruin_repo)

        assert mark_email_as_done._bruin_repository == bruin_repo

    @pytest.mark.asyncio
    async def mark_email_as_done_no_body_test(self):
        msg = {}

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg)

        bruin_repository = Mock()
        bruin_repository.mark_email_as_done = AsyncMock(return_value={})

        mark_email_as_done = MarkEmailAsDone(bruin_repository)
        await mark_email_as_done(request_msg)

        bruin_repository.mark_email_as_done.assert_not_awaited()
        request_msg.respond.assert_awaited_once_with(
            to_json_bytes({"body": 'Must include "body" in request', "status": 400})
        )

    @pytest.mark.asyncio
    async def mark_email_as_done_no_email_id(self):
        msg = {"body": {}}

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg)

        bruin_repository = Mock()
        bruin_repository.mark_email_as_done = AsyncMock(return_value={})

        mark_email_as_done = MarkEmailAsDone(bruin_repository)
        await mark_email_as_done(request_msg)

        bruin_repository.mark_email_as_done.assert_not_awaited()
        request_msg.respond.assert_awaited_once_with(
            to_json_bytes({"body": "You must include email_id in the request", "status": 400})
        )

    @pytest.mark.asyncio
    async def mark_email_as_done_200_test(self):
        email_id = 1234
        msg = {"body": {"email_id": email_id}}

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg)

        response_body = {"success": True, "email_id": email_id}

        bruin_repository = Mock()
        bruin_repository.mark_email_as_done = AsyncMock(return_value={"body": response_body, "status": 200})

        mark_email_as_done = MarkEmailAsDone(bruin_repository)
        await mark_email_as_done(request_msg)

        bruin_repository.mark_email_as_done.assert_awaited_once_with(email_id)
        request_msg.respond.assert_awaited_once_with(to_json_bytes({"body": response_body, "status": 200}))
