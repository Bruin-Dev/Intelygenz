import pytest
from asynctest import CoroutineMock
from config import testconfig as config


class TestSlackRepository:
    def instantiation_test(self, slack_repository, logger, slack_client):
        assert slack_repository._config is config
        assert slack_repository._slack_client is slack_client
        assert slack_repository._logger is logger

    @pytest.mark.asyncio
    async def send_to_slack_test(self, slack_repository):
        test_msg = "This is a dummy message"

        slack_repository._slack_client.send_to_slack = CoroutineMock()

        await slack_repository.send_to_slack(test_msg)

        slack_repository._slack_client.send_to_slack.assert_called_once_with({"text": test_msg})
