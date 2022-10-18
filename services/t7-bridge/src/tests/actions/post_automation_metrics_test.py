from unittest.mock import Mock

import pytest
from nats.aio.msg import Msg

from application.actions.post_automation_metrics import PostAutomationMetrics
from application.repositories.utils_repository import to_json_bytes


class TestPostAutomationMetrics:
    def instance_test(self):
        t7_kre_repository = Mock()

        automation_metrics = PostAutomationMetrics(t7_kre_repository)

        assert automation_metrics._t7_kre_repository == t7_kre_repository

    @pytest.mark.parametrize(
        "body_in_topic",
        [
            None,
            ({"some-key": "some-data"}),
            ({"ticket_id": 12345}),
            ({"ticket_rows": [{"asset": "7627627"}]}),
        ],
        ids=["without_body", "without_params", "without_ticket_rows", "without_ticket_id"],
    )
    @pytest.mark.asyncio
    async def post_automation_metrics_error_400_test(self, body_in_topic):
        request_id = 123
        response_topic = "_INBOX.2007314fe0fcb2cdc2a2914c1"
        msg_published_in_topic = {"request_id": request_id, "response_topic": response_topic, "body": body_in_topic}

        t7_kre_repository = Mock()
        t7_kre_repository.post_automation_metrics = Mock()

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg_published_in_topic)

        automation_metrics = PostAutomationMetrics(t7_kre_repository)

        await automation_metrics(request_msg)

        t7_kre_repository.post_automation_metrics.assert_not_called()
        request_msg.respond.assert_awaited_once_with(
            to_json_bytes(
                {
                    "request_id": request_id,
                    "body": 'You must specify {.."body": {"ticket_id", "ticket_rows"}..} in the request',
                    "status": 400,
                }
            ),
        )

    @pytest.mark.asyncio
    async def post_automation_metrics_ok_test(self):
        request_id = 123
        response_topic = "_INBOX.2007314fe0fcb2cdc2a2914c1"
        params = {"ticket_id": 123, "ticket_rows": []}

        msg_published_in_topic = {
            "request_id": request_id,
            "body": params,
            "response_topic": response_topic,
        }

        request_msg = Mock(spec_set=Msg)
        request_msg.data = to_json_bytes(msg_published_in_topic)

        return_value = {"body": "No content", "status": 204}

        t7_kre_repository = Mock()
        t7_kre_repository.post_automation_metrics = Mock(return_value=return_value)

        automation_metrics = PostAutomationMetrics(t7_kre_repository)

        await automation_metrics(request_msg)

        t7_kre_repository.post_automation_metrics.assert_called()
        request_msg.respond.assert_awaited_once_with(
            to_json_bytes({"request_id": request_id, "body": return_value["body"], "status": return_value["status"]})
        )
