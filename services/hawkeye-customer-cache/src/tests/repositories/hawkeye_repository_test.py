from unittest.mock import AsyncMock, Mock, patch

import pytest
from nats.aio.msg import Msg
from shortuuid import uuid

from application import nats_error_response
from application.repositories import hawkeye_repository as hawkeye_repository_module
from application.repositories.hawkeye_repository import HawkeyeRepository
from application.repositories.utils_repository import to_json_bytes
from config import testconfig

uuid_ = uuid()
uuid_mock = patch.object(hawkeye_repository_module, "uuid", return_value=uuid_)


class TestHawkeyeRepository:
    def instance_test(self):
        nats_client = Mock()
        config = testconfig
        notifications_repository = Mock()

        hawkeye_repository = HawkeyeRepository(nats_client, config, notifications_repository)

        assert hawkeye_repository._nats_client is nats_client
        assert hawkeye_repository._config is config
        assert hawkeye_repository._notifications_repository is notifications_repository

    @pytest.mark.asyncio
    async def get_probes_ok_test(self, hawkeye_repository, response_get_probes_down_ok):
        request = {
            "request_id": uuid_,
            "body": {},
        }

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(response_get_probes_down_ok)

        hawkeye_repository._nats_client.request = AsyncMock(return_value=response_msg)

        with uuid_mock:
            result = await hawkeye_repository.get_probes()

        hawkeye_repository._nats_client.request.assert_awaited_once_with(
            "hawkeye.probe.request", to_json_bytes(request), timeout=60
        )
        assert result == response_get_probes_down_ok

    @pytest.mark.asyncio
    async def get_probes_with_request_failing_test(self, hawkeye_repository):
        request = {
            "request_id": uuid_,
            "body": {},
        }

        hawkeye_repository._nats_client.request = AsyncMock(side_effect=Exception)

        hawkeye_repository._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await hawkeye_repository.get_probes()

        hawkeye_repository._nats_client.request.assert_awaited_once_with(
            "hawkeye.probe.request", to_json_bytes(request), timeout=60
        )
        hawkeye_repository._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_probes_with_request_returning_non_2xx_status_test(self, hawkeye_repository, response_internal_error):
        request = {
            "request_id": uuid_,
            "body": {},
        }

        response_msg = Mock(spec_set=Msg)
        response_msg.data = to_json_bytes(response_internal_error)

        hawkeye_repository._nats_client.request = AsyncMock(return_value=response_msg)

        hawkeye_repository._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await hawkeye_repository.get_probes()

        hawkeye_repository._nats_client.request.assert_awaited_once_with(
            "hawkeye.probe.request", to_json_bytes(request), timeout=60
        )
        hawkeye_repository._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == response_internal_error
