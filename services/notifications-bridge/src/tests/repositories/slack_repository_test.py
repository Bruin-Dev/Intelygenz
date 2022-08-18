from unittest.mock import AsyncMock

import pytest


class TestSlackRepository:
    def instance_test(self, slack_repository, slack_client):
        assert slack_repository._slack_client is slack_client

    @pytest.mark.asyncio
    async def send_to_slack_test(self, slack_repository):
        test_msg = "This is a dummy message"

        slack_repository._slack_client.send_to_slack = AsyncMock()

        await slack_repository.send_to_slack(test_msg)

        slack_repository._slack_client.send_to_slack.assert_called_once_with({"text": test_msg})
