from unittest.mock import Mock

import pytest
from nats.aio.msg import Msg

from application.actions.post_live_automation_metrics import PostLiveAutomationMetrics
from application.repositories.utils_repository import to_json_bytes


class TestPostLiveAutomationMetrics:
    def instance_test(self):
        t7_kre_repository = Mock()

        automation_metrics = PostLiveAutomationMetrics(t7_kre_repository)

        assert automation_metrics._t7_kre_repository == t7_kre_repository

    @pytest.mark.parametrize(
        "body_in_topic",
        [
            None,
            ({"some-key": "some-data"}),
            ({"asset_id": "VC00000000", "automated_successfully": False}),
            ({"ticket_id": 123, "automated_successfully": True}),
            ({"ticket_id": 123, "asset_id": "VC00000000"}),
        ],
        ids=[
            "without_body",
            "without_params",
            "without_ticket_id",
            "without_asset_id",
            "without_automated_successfully",
        ],
    )
    @pytest.mark.asyncio
    async def post_automation_metrics_error_400_test(self, body_in_topic):
        request_id = 123
        response_topic = "_INBOX.2007314fe0fcb2cdc2a2914c1"
        msg_published_in_topic = {"request_id": request_id, "response_topic": response_topic, "body": body_in_topic}

        t7_kre_repository = Mock()
        t7_kre_repository.post_live_automation_metrics = Mock()

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg_published_in_topic)

        live_automation_metrics = PostLiveAutomationMetrics(t7_kre_repository)

        await live_automation_metrics(request_msg)

        t7_kre_repository.post_live_automation_metrics.assert_not_called()
        body_msg = 'You must specify {.."body": {"ticket_id", "asset_id", "automated_successfully"}..} in the request'
        request_msg.respond.assert_awaited_once_with(
            to_json_bytes(
                {
                    "request_id": request_id,
                    "body": body_msg,
                    "status": 400,
                }
            ),
        )

    @pytest.mark.parametrize("automated_successfully", [True, False])
    @pytest.mark.asyncio
    async def post_live_automation_metrics_ok_test(self, automated_successfully):
        request_id = 123
        response_topic = "_INBOX.2007314fe0fcb2cdc2a2914c1"
        params = {"ticket_id": 123, "asset_id": "VC00000000", "automated_successfully": automated_successfully}

        msg_published_in_topic = {
            "request_id": request_id,
            "body": params,
            "response_topic": response_topic,
        }

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg_published_in_topic)

        return_value = {"body": "No content", "status": 204}

        t7_kre_repository = Mock()
        t7_kre_repository.post_live_automation_metrics = Mock(return_value=return_value)

        live_automation_metrics = PostLiveAutomationMetrics(t7_kre_repository)

        await live_automation_metrics(request_msg)

        t7_kre_repository.post_live_automation_metrics.assert_called()
        request_msg.respond.assert_awaited_once_with(
            to_json_bytes({"request_id": request_id, "body": return_value["body"], "status": return_value["status"]})
        )
