from datetime import datetime
from http import HTTPStatus
from unittest.mock import patch

import pytest
from application.repositories import velocloud_repository as velocloud_repository_module
from asynctest import CoroutineMock, Mock
from config import testconfig
from shortuuid import uuid

uuid_ = uuid()
uuid_mock = patch.object(velocloud_repository_module, "uuid", return_value=uuid_)


class TestVelocloudRepository:
    def instance_test(self, velocloud_repository, event_bus, logger, notifications_repository):
        assert velocloud_repository._event_bus is event_bus
        assert velocloud_repository._logger is logger
        assert velocloud_repository._notifications_repository is notifications_repository
        assert velocloud_repository._config is testconfig

    @pytest.mark.asyncio
    async def get_network_gateway_list_test(self, velocloud_repository, make_rpc_request, make_rpc_response):
        velocloud_host = "mettel.velocloud.net"
        payload = {"host": velocloud_host}
        request = make_rpc_request(request_id=uuid_, body=payload)
        response = make_rpc_response(request_id=uuid_, body=[], status=HTTPStatus.OK)

        velocloud_repository._event_bus.rpc_request = CoroutineMock(return_value=response)

        with uuid_mock:
            result = await velocloud_repository.get_network_gateway_list(velocloud_host)

        velocloud_repository._event_bus.rpc_request.assert_awaited_once_with(
            "request.network.gateway.list", request, timeout=30
        )
        assert result == response

    @pytest.mark.asyncio
    async def get_gateway_status_metrics_test(
        self, velocloud_repository, make_gateway, make_rpc_request, make_rpc_response
    ):
        gateway = make_gateway(id=1)
        metrics = ["tunnelCount"]

        payload = {
            "host": gateway["host"],
            "gateway_id": gateway["id"],
            "metrics": metrics,
            "interval": {
                "start": "2022-01-01T11:00:00Z",
                "end": "2022-01-01T12:00:00Z",
            },
        }

        request = make_rpc_request(request_id=uuid_, body=payload)
        response = make_rpc_response(request_id=uuid_, body={}, status=HTTPStatus.OK)

        velocloud_repository._event_bus.rpc_request = CoroutineMock(return_value=response)

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=datetime(year=2022, month=1, day=1, hour=12))

        with uuid_mock:
            with patch.object(velocloud_repository_module, "datetime", new=datetime_mock):
                result = await velocloud_repository.get_gateway_status_metrics(gateway)

        velocloud_repository._event_bus.rpc_request.assert_awaited_once_with(
            "request.gateway.status.metrics", request, timeout=30
        )
        assert result == response
