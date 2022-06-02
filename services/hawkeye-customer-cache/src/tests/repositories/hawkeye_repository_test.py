from unittest.mock import Mock, patch

import pytest
from application import nats_error_response
from application.repositories import hawkeye_repository as hawkeye_repository_module
from application.repositories.hawkeye_repository import HawkeyeRepository
from asynctest import CoroutineMock
from config import testconfig
from shortuuid import uuid

uuid_ = uuid()
uuid_mock = patch.object(hawkeye_repository_module, "uuid", return_value=uuid_)


class TestHawkeyeRepository:
    def instance_test(self):
        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        hawkeye_repository = HawkeyeRepository(event_bus, logger, config, notifications_repository)

        assert hawkeye_repository._event_bus is event_bus
        assert hawkeye_repository._logger is logger
        assert hawkeye_repository._config is config
        assert hawkeye_repository._notifications_repository is notifications_repository

    @pytest.mark.asyncio
    async def get_probes_ok_test(self, hawkeye_repository, response_get_probes_down_ok):
        request = {
            "request_id": uuid_,
            "body": {},
        }

        event_bus = Mock()
        hawkeye_repository._event_bus.rpc_request = CoroutineMock(return_value=response_get_probes_down_ok)

        with uuid_mock:
            result = await hawkeye_repository.get_probes()

        hawkeye_repository._event_bus.rpc_request.assert_awaited_once_with("hawkeye.probe.request", request, timeout=60)
        assert result == response_get_probes_down_ok

    @pytest.mark.asyncio
    async def get_probes_with_rpc_request_failing_test(self, hawkeye_repository):
        request = {
            "request_id": uuid_,
            "body": {},
        }

        hawkeye_repository._event_bus.rpc_request = CoroutineMock(side_effect=Exception)

        hawkeye_repository._notifications_repository.send_slack_message = CoroutineMock()

        with uuid_mock:
            result = await hawkeye_repository.get_probes()

        hawkeye_repository._event_bus.rpc_request.assert_awaited_once_with("hawkeye.probe.request", request, timeout=60)
        hawkeye_repository._notifications_repository.send_slack_message.assert_awaited_once()
        hawkeye_repository._logger.error.assert_called_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_probes_with_rpc_request_returning_non_2xx_status_test(
        self, hawkeye_repository, response_internal_error
    ):
        request = {
            "request_id": uuid_,
            "body": {},
        }

        hawkeye_repository._event_bus.rpc_request = CoroutineMock(return_value=response_internal_error)

        hawkeye_repository._notifications_repository.send_slack_message = CoroutineMock()

        with uuid_mock:
            result = await hawkeye_repository.get_probes()

        hawkeye_repository._event_bus.rpc_request.assert_awaited_once_with("hawkeye.probe.request", request, timeout=60)
        hawkeye_repository._notifications_repository.send_slack_message.assert_awaited_once()
        hawkeye_repository._logger.error.assert_called_once()
        assert result == response_internal_error
