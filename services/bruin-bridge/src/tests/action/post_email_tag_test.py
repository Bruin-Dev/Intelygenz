from unittest.mock import AsyncMock, Mock

import pytest
from application.actions.post_email_tag import PostEmailTag
from application.repositories.utils_repository import to_json_bytes
from nats.aio.msg import Msg


class TestPostEmailTag:
    def instance_test(self):
        bruin_repository = Mock()

        post_email_tag = PostEmailTag(bruin_repository)

        assert post_email_tag._bruin_repository is bruin_repository

    @pytest.mark.asyncio
    async def post_email_tag_no_body_test(self):
        msg = {}

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg)

        msg_published_in_topic = {"body": 'Must include "body" in request', "status": 400}

        bruin_repository = Mock()
        bruin_repository.post_email_tag = AsyncMock()

        post_email_tag = PostEmailTag(bruin_repository)
        await post_email_tag(request_msg)

        post_email_tag._bruin_repository.post_email_tag.assert_not_awaited()
        request_msg.respond.assert_awaited_once_with(to_json_bytes(msg_published_in_topic))

    @pytest.mark.asyncio
    async def post_email_tag_no_email_id_or_tags_test(self):
        msg = {
            "body": {},
        }

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg)

        msg_published_in_topic = {
            "body": 'You must include "email_id" and "tag_id" in the "body" field of the response request',
            "status": 400,
        }

        bruin_repository = Mock()
        bruin_repository.post_email_tag = AsyncMock()

        post_email_tag = PostEmailTag(bruin_repository)
        await post_email_tag(request_msg)

        post_email_tag._bruin_repository.post_email_tag.assert_not_awaited()
        request_msg.respond.assert_awaited_once_with(to_json_bytes(msg_published_in_topic))

    @pytest.mark.asyncio
    async def post_email_tag_200_test(self):
        tags_added_response = {"body": "Tags added", "status": 200}
        email_id = "321"
        tag_id = "1002"
        msg = {
            "body": {"email_id": email_id, "tag_id": tag_id},
        }

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg)

        msg_published_in_topic = {"body": tags_added_response["body"], "status": 200}

        bruin_repository = Mock()
        bruin_repository.post_email_tag = AsyncMock(return_value=tags_added_response)

        post_email_tag = PostEmailTag(bruin_repository)
        await post_email_tag(request_msg)

        post_email_tag._bruin_repository.post_email_tag.assert_awaited_once_with(email_id, tag_id)
        request_msg.respond.assert_awaited_once_with(to_json_bytes(msg_published_in_topic))

    @pytest.mark.asyncio
    async def post_email_tag_status_500_test(self):
        tags_added_response = {"body": "Something broke", "status": 500}
        email_id = "321"
        tag_id = "1002"
        msg = {
            "body": {"email_id": email_id, "tag_id": tag_id},
        }

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg)

        msg_published_in_topic = {"body": tags_added_response["body"], "status": 500}

        event_bus = Mock()
        event_bus.publish_message = AsyncMock()

        bruin_repository = Mock()
        bruin_repository.post_email_tag = AsyncMock(return_value=tags_added_response)

        post_email_tag = PostEmailTag(bruin_repository)
        await post_email_tag(request_msg)

        post_email_tag._bruin_repository.post_email_tag.assert_awaited_once_with(email_id, tag_id)
        request_msg.respond.assert_awaited_once_with(to_json_bytes(msg_published_in_topic))
