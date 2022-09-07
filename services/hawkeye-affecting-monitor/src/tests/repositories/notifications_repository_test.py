from unittest.mock import patch

import pytest
from application.repositories import notifications_repository as notifications_repository_module
from shortuuid import uuid

uuid_ = uuid()
uuid_mock = patch.object(notifications_repository_module, "uuid", return_value=uuid_)


class TestNotificationsRepository:
    def instance_test(self, notifications_repository, event_bus):
        assert notifications_repository._event_bus is event_bus

    @pytest.mark.asyncio
    async def send_slack_message_test(self, notifications_repository, event_bus):
        message = "Some message"

        with uuid_mock:
            await notifications_repository.send_slack_message(message)

        event_bus.rpc_request.assert_awaited_once_with(
            "notification.slack.request",
            {
                "request_id": uuid_,
                "body": {"message": message},
            },
            timeout=10,
        )

    @pytest.mark.asyncio
    async def notify_ticket_creation_test(self, notifications_repository):
        ticket_id = 12345
        serial_number = "B827EB76A8DE"

        message = (
            f"Service Affecting ticket created for Ixia device {serial_number}: https://app.bruin.com/t/{ticket_id}"
        )

        with uuid_mock:
            await notifications_repository.notify_ticket_creation(ticket_id, serial_number)

        notifications_repository.send_slack_message.assert_awaited_once_with(message)

    @pytest.mark.asyncio
    async def notify_ticket_detail_was_unresolved_test(self, notifications_repository):
        ticket_id = 12345
        serial_number = "B827EB76A8DE"

        message = (
            f"Detail corresponding to Ixia device {serial_number} in Service Affecting ticket {ticket_id} has been "
            f"unresolved: https://app.bruin.com/t/{ticket_id}"
        )

        with uuid_mock:
            await notifications_repository.notify_ticket_detail_was_unresolved(ticket_id, serial_number)

        notifications_repository.send_slack_message.assert_awaited_once_with(message)

    @pytest.mark.asyncio
    async def notify_multiple_notes_were_posted_to_ticket_test(self, notifications_repository):
        ticket_id = 12345
        serial_number = "B827EB76A8DE"

        message = (
            f"Multiple Affecting notes related to Ixia device {serial_number} were posted to Service Affecting ticket "
            f"{ticket_id}: https://app.bruin.com/t/{ticket_id}"
        )

        with uuid_mock:
            await notifications_repository.notify_multiple_notes_were_posted_to_ticket(ticket_id, serial_number)

        notifications_repository.send_slack_message.assert_awaited_once_with(message)
