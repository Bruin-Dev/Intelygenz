from unittest.mock import AsyncMock, Mock

import pytest
from nats.aio.msg import Msg

from application.actions.post_notification_email_milestone import PostNotificationEmailMilestone
from application.repositories.utils_repository import to_json_bytes


class TestPostNotificationEmailMilestone:
    def instance_test(self):
        bruin_repository = Mock()

        post_notification_email_milestone = PostNotificationEmailMilestone(bruin_repository)

        assert post_notification_email_milestone._bruin_repository is bruin_repository

    @pytest.mark.asyncio
    async def post_notification_email_milestone_200_test(self):
        post_notification_email_milestone_response = {"eventId": 12, "jobId": 5}
        msg = {
            "body": {
                "notification_type": "TicketPublicAPITest_E-mail",
                "ticket_id": 3549040,
                "service_number": "VC1234567",
            },
        }

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg)

        msg_published_in_topic = {
            "body": post_notification_email_milestone_response,
            "status": 200,
        }

        bruin_repository = Mock()
        bruin_repository.post_notification_email_milestone = AsyncMock(
            return_value={"body": post_notification_email_milestone_response, "status": 200}
        )

        post_notification_email_milestone = PostNotificationEmailMilestone(bruin_repository)
        await post_notification_email_milestone(request_msg)

        post_notification_email_milestone._bruin_repository.post_notification_email_milestone.assert_awaited_once_with(
            msg["body"]
        )
        request_msg.respond.assert_awaited_once_with(to_json_bytes(msg_published_in_topic))

    @pytest.mark.asyncio
    async def post_notification_email_milestone_not_200_test(self):
        post_notification_email_milestone_response = {"body": "Got internal error from Bruin", "status": 500}
        msg = {
            "body": {
                "notification_type": "TicketPublicAPITest_E-mail",
                "ticket_id": 3549040,
                "service_number": "VC1234567",
            },
        }

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg)

        msg_published_in_topic = {
            **post_notification_email_milestone_response,
        }

        bruin_repository = Mock()
        bruin_repository.post_notification_email_milestone = AsyncMock(
            return_value=post_notification_email_milestone_response
        )

        post_notification_email_milestone = PostNotificationEmailMilestone(bruin_repository)
        await post_notification_email_milestone(request_msg)

        post_notification_email_milestone._bruin_repository.post_notification_email_milestone.assert_awaited_once_with(
            msg["body"]
        )
        request_msg.respond.assert_awaited_once_with(to_json_bytes(msg_published_in_topic))

    @pytest.mark.asyncio
    async def post_notification_email_milestone_missing_keys_in_payload_test(self):
        msg = {
            "body": {
                "notification_type": "TicketPublicAPITest_E-mail",
                "ticket_id": 3549040,
            },
        }

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg)

        msg_published_in_topic = {
            "body": 'You must include "ticket_id", "notification_type" and "service_number"'
            ' in the "body" field of the response request',
            "status": 400,
        }

        bruin_repository = Mock()
        bruin_repository.post_notification_email_milestone = AsyncMock()

        post_notification_email_milestone = PostNotificationEmailMilestone(bruin_repository)
        await post_notification_email_milestone(request_msg)

        post_notification_email_milestone._bruin_repository.post_notification_email_milestone.assert_not_awaited()
        request_msg.respond.assert_awaited_once_with(to_json_bytes(msg_published_in_topic))

    @pytest.mark.asyncio
    async def post_notification_email_milestone_missing_payload_test(self):
        msg = {}

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg)

        msg_published_in_topic = {
            "body": 'Must include {.."body":{"ticket_id", "notification_type", "service_number"}, in request',
            "status": 400,
        }

        bruin_repository = Mock()
        bruin_repository.post_notification_email_milestone = AsyncMock()

        post_notification_email_milestone = PostNotificationEmailMilestone(bruin_repository)
        await post_notification_email_milestone(request_msg)

        post_notification_email_milestone._bruin_repository.post_notification_email_milestone.assert_not_awaited()
        request_msg.respond.assert_awaited_once_with(to_json_bytes(msg_published_in_topic))
