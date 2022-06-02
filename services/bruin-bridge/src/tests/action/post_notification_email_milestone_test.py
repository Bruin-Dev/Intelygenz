from unittest.mock import Mock

import pytest
from application.actions.post_notification_email_milestone import PostNotificationEmailMilestone
from asynctest import CoroutineMock


class TestPostNotificationEmailMilestone:
    def instance_test(self):
        logger = Mock()
        event_bus = Mock()
        bruin_repository = Mock()
        post_notification_email_milestone = PostNotificationEmailMilestone(logger, event_bus, bruin_repository)
        assert post_notification_email_milestone._logger is logger
        assert post_notification_email_milestone._event_bus is event_bus
        assert post_notification_email_milestone._bruin_repository is bruin_repository

    @pytest.mark.asyncio
    async def post_notification_email_milestone_200_test(self):
        logger = Mock()
        logger.error = Mock()
        post_notification_email_milestone_response = {"eventId": 12, "jobId": 5}
        request_id = 123
        response_topic = "_INBOX.2007314fe0fcb2cdc2a2914c1"
        msg = {
            "request_id": request_id,
            "response_topic": response_topic,
            "body": {
                "notification_type": "TicketPublicAPITest_E-mail",
                "ticket_id": 3549040,
                "service_number": "VC1234567",
            },
        }
        msg_published_in_topic = {
            "request_id": msg["request_id"],
            "body": post_notification_email_milestone_response,
            "status": 200,
        }
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        bruin_repository = Mock()
        bruin_repository.post_notification_email_milestone = CoroutineMock(
            return_value={"body": post_notification_email_milestone_response, "status": 200}
        )

        post_notification_email_milestone = PostNotificationEmailMilestone(logger, event_bus, bruin_repository)
        await post_notification_email_milestone.post_notification_email_milestone(msg)

        logger.error.assert_not_called()
        post_notification_email_milestone._bruin_repository.post_notification_email_milestone.assert_awaited_once_with(
            msg["body"]
        )
        post_notification_email_milestone._event_bus.publish_message.assert_awaited_once_with(
            response_topic, msg_published_in_topic
        )

    @pytest.mark.asyncio
    async def post_notification_email_milestone_not_200_test(self):
        logger = Mock()
        logger.error = Mock()
        post_notification_email_milestone_response = {"body": "Got internal error from Bruin", "status": 500}
        request_id = 123
        response_topic = "_INBOX.2007314fe0fcb2cdc2a2914c1"
        msg = {
            "request_id": request_id,
            "response_topic": response_topic,
            "body": {
                "notification_type": "TicketPublicAPITest_E-mail",
                "ticket_id": 3549040,
                "service_number": "VC1234567",
            },
        }
        msg_published_in_topic = {
            "request_id": msg["request_id"],
            **post_notification_email_milestone_response,
        }
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        bruin_repository = Mock()
        bruin_repository.post_notification_email_milestone = CoroutineMock(
            return_value=post_notification_email_milestone_response
        )

        post_notification_email_milestone = PostNotificationEmailMilestone(logger, event_bus, bruin_repository)
        await post_notification_email_milestone.post_notification_email_milestone(msg)

        logger.error.assert_called()
        post_notification_email_milestone._bruin_repository.post_notification_email_milestone.assert_awaited_once_with(
            msg["body"]
        )
        post_notification_email_milestone._event_bus.publish_message.assert_awaited_once_with(
            response_topic, msg_published_in_topic
        )

    @pytest.mark.asyncio
    async def post_notification_email_milestone_missing_keys_in_payload_test(self):
        logger = Mock()
        logger.error = Mock()
        request_id = 123
        response_topic = "_INBOX.2007314fe0fcb2cdc2a2914c1"
        msg = {
            "request_id": request_id,
            "response_topic": response_topic,
            "body": {
                "notification_type": "TicketPublicAPITest_E-mail",
                "ticket_id": 3549040,
            },
        }
        msg_published_in_topic = {
            "request_id": msg["request_id"],
            "body": 'You must include "ticket_id", "notification_type" and "service_number"'
            ' in the "body" field of the response request',
            "status": 400,
        }
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        bruin_repository = Mock()
        bruin_repository.post_notification_email_milestone = CoroutineMock()

        post_notification_email_milestone = PostNotificationEmailMilestone(logger, event_bus, bruin_repository)
        await post_notification_email_milestone.post_notification_email_milestone(msg)

        post_notification_email_milestone._bruin_repository.post_notification_email_milestone.assert_not_awaited()
        post_notification_email_milestone._event_bus.publish_message.assert_awaited_once_with(
            response_topic, msg_published_in_topic
        )

    @pytest.mark.asyncio
    async def post_notification_email_milestone_missing_payload_test(self):
        logger = Mock()
        request_id = 123
        response_topic = "_INBOX.2007314fe0fcb2cdc2a2914c1"
        msg = {"request_id": request_id, "response_topic": response_topic}
        msg_published_in_topic = {
            "request_id": msg["request_id"],
            "body": 'Must include {.."body":{"ticket_id", "notification_type", "service_number"}, in request',
            "status": 400,
        }
        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()
        bruin_repository = Mock()
        bruin_repository.post_notification_email_milestone = CoroutineMock()

        post_notification_email_milestone = PostNotificationEmailMilestone(logger, event_bus, bruin_repository)
        await post_notification_email_milestone.post_notification_email_milestone(msg)

        post_notification_email_milestone._bruin_repository.post_notification_email_milestone.assert_not_awaited()
        post_notification_email_milestone._event_bus.publish_message.assert_awaited_once_with(
            response_topic, msg_published_in_topic
        )
