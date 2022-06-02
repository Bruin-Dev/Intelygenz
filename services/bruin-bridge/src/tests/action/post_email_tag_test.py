from unittest.mock import Mock

import pytest
from application.actions.post_email_tag import PostEmailTag
from asynctest import CoroutineMock


class TestPostEmailTag:
    def instance_test(self):
        logger = Mock()
        event_bus = Mock()
        bruin_repository = Mock()

        post_email_tag = PostEmailTag(logger, event_bus, bruin_repository)

        assert post_email_tag._logger is logger
        assert post_email_tag._event_bus is event_bus
        assert post_email_tag._bruin_repository is bruin_repository

    @pytest.mark.asyncio
    async def post_email_tag_no_body_test(self):
        logger = Mock()
        request_id = 123
        response_topic = "_INBOX.2007314fe0fcb2cdc2a2914c1"
        msg = {
            "request_id": request_id,
            "response_topic": response_topic,
        }
        msg_published_in_topic = {"request_id": request_id, "body": 'Must include "body" in request', "status": 400}

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.post_email_tag = CoroutineMock()

        post_email_tag = PostEmailTag(logger, event_bus, bruin_repository)
        await post_email_tag.post_email_tag(msg)

        post_email_tag._bruin_repository.post_email_tag.assert_not_awaited()
        post_email_tag._event_bus.publish_message.assert_awaited_once_with(response_topic, msg_published_in_topic)

    @pytest.mark.asyncio
    async def post_email_tag_no_email_id_or_tags_test(self):
        logger = Mock()
        add_tags_response = "Tags added"
        request_id = 123
        response_topic = "_INBOX.2007314fe0fcb2cdc2a2914c1"
        msg = {
            "request_id": request_id,
            "body": {},
            "response_topic": response_topic,
        }
        msg_published_in_topic = {
            "request_id": request_id,
            "body": 'You must include "email_id" and "tag_id" in the "body" field of the response request',
            "status": 400,
        }

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.post_email_tag = CoroutineMock()

        post_email_tag = PostEmailTag(logger, event_bus, bruin_repository)
        await post_email_tag.post_email_tag(msg)

        post_email_tag._bruin_repository.post_email_tag.assert_not_awaited()
        post_email_tag._event_bus.publish_message.assert_awaited_once_with(response_topic, msg_published_in_topic)

    @pytest.mark.asyncio
    async def post_email_tag_200_test(self):
        logger = Mock()
        tags_added_response = {"body": "Tags added", "status": 200}
        request_id = 123
        email_id = "321"
        tag_id = "1002"
        response_topic = "_INBOX.2007314fe0fcb2cdc2a2914c1"
        msg = {
            "request_id": request_id,
            "response_topic": response_topic,
            "body": {"email_id": email_id, "tag_id": tag_id},
        }
        msg_published_in_topic = {"request_id": request_id, "body": tags_added_response["body"], "status": 200}

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.post_email_tag = CoroutineMock(return_value=tags_added_response)

        post_email_tag = PostEmailTag(logger, event_bus, bruin_repository)
        await post_email_tag.post_email_tag(msg)

        post_email_tag._bruin_repository.post_email_tag.assert_awaited_once_with(email_id, tag_id)
        post_email_tag._event_bus.publish_message.assert_awaited_once_with(response_topic, msg_published_in_topic)

    @pytest.mark.asyncio
    async def post_email_tag_status_500_test(self):
        logger = Mock()
        logger.error = Mock()
        tags_added_response = {"body": "Something broke", "status": 500}
        request_id = 123
        email_id = "321"
        tag_id = "1002"
        response_topic = "_INBOX.2007314fe0fcb2cdc2a2914c1"
        msg = {
            "request_id": request_id,
            "response_topic": response_topic,
            "body": {"email_id": email_id, "tag_id": tag_id},
        }
        msg_published_in_topic = {"request_id": request_id, "body": tags_added_response["body"], "status": 500}

        event_bus = Mock()
        event_bus.publish_message = CoroutineMock()

        bruin_repository = Mock()
        bruin_repository.post_email_tag = CoroutineMock(return_value=tags_added_response)

        post_email_tag = PostEmailTag(logger, event_bus, bruin_repository)
        await post_email_tag.post_email_tag(msg)

        post_email_tag._bruin_repository.post_email_tag.assert_awaited_once_with(email_id, tag_id)
        post_email_tag._event_bus.publish_message.assert_awaited_once_with(response_topic, msg_published_in_topic)
        logger.error.assert_called_once_with(
            f"Error adding tags to email: Status: 500 body: " + tags_added_response["body"]
        )
