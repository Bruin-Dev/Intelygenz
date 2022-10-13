from unittest.mock import AsyncMock, Mock

import pytest
from nats.aio.msg import Msg

from application.actions.link_ticket_to_email import LinkTicketToEmail
from application.repositories.utils_repository import to_json_bytes


class TestLinkTicketToEmail:
    def instance_test(self):
        bruin_repo = Mock()
        resolve_ticket = LinkTicketToEmail(bruin_repo)

        assert resolve_ticket._bruin_repository == bruin_repo

    @pytest.mark.asyncio
    async def link_ticket_to_email_no_body_test(self):
        msg = {}

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg)

        bruin_repository = Mock()
        bruin_repository.link_ticket_to_email = AsyncMock(return_value={})

        link_ticket_to_email = LinkTicketToEmail(bruin_repository)
        await link_ticket_to_email(request_msg)

        bruin_repository.link_ticket_to_email.assert_not_awaited()
        request_msg.respond.assert_awaited_once_with(
            to_json_bytes({"body": 'Must include "body" in request', "status": 400})
        )

    @pytest.mark.asyncio
    async def link_ticket_to_email_no_ticket_id(self):
        msg = {"body": {"email_id": 1234}}

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg)

        bruin_repository = Mock()
        bruin_repository.link_ticket_to_email = AsyncMock(return_value={})

        link_ticket_to_email = LinkTicketToEmail(bruin_repository)
        await link_ticket_to_email(request_msg)

        bruin_repository.link_ticket_to_email.assert_not_awaited()
        request_msg.respond.assert_awaited_once_with(
            to_json_bytes({"body": "You must include email_id in the request", "status": 400})
        )

    @pytest.mark.asyncio
    async def link_ticket_to_email_200_test(self):
        email_id = 1234
        ticket_id = 5678
        msg = {
            "body": {"email_id": email_id, "ticket_id": ticket_id},
        }

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg)

        response_body = {
            "Success": True,
            "EmailId": email_id,
            "TicketId": ticket_id,
            "TotalEmailAffected": 3,
            "Warnings": [],
        }

        bruin_repository = Mock()
        bruin_repository.link_ticket_to_email = AsyncMock(return_value={"body": response_body, "status": 200})

        link_ticket_to_email = LinkTicketToEmail(bruin_repository)
        await link_ticket_to_email(request_msg)

        bruin_repository.link_ticket_to_email.assert_awaited_once_with(ticket_id, email_id)
        request_msg.respond.assert_awaited_once_with(to_json_bytes({"body": response_body, "status": 200}))
