import json
from datetime import datetime
from http import HTTPStatus
from typing import Any
from unittest.mock import AsyncMock, Mock, patch

import pytest
from nats.aio.msg import Msg
from shortuuid import uuid

from application.repositories import velocloud_repository as velocloud_repository_module
from config import testconfig

uuid_ = uuid()
uuid_mock = patch.object(velocloud_repository_module, "uuid", return_value=uuid_)


def to_json_bytes(message: dict[str, Any]):
    return json.dumps(message, default=str, separators=(",", ":")).encode()


class TestVelocloudRepository:
    def instance_test(self, velocloud_repository, nats_client, notifications_repository):
        assert velocloud_repository._nats_client is nats_client
        assert velocloud_repository._notifications_repository is notifications_repository
        assert velocloud_repository._config is testconfig

    @pytest.mark.asyncio
    async def get_network_gateway_list_test(self, velocloud_repository, make_rpc_request, make_rpc_response):
        velocloud_host = "mettel.velocloud.net"
        payload = {"host": velocloud_host}
        request = make_rpc_request(request_id=uuid_, body=payload)
        response = make_rpc_response(request_id=uuid_, body=[], status=HTTPStatus.OK)
        NATS_AIO_MSG = Msg(_client="NATS", data=to_json_bytes(response))

        velocloud_repository._nats_client.request = AsyncMock(return_value=NATS_AIO_MSG)

        with uuid_mock:
            result = await velocloud_repository.get_network_gateway_list(velocloud_host)

        velocloud_repository._nats_client.request.assert_awaited_once_with(
            "request.network.gateway.list", to_json_bytes(request), timeout=30
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
        NATS_AIO_MSG = Msg(_client="NATS", data=to_json_bytes(response))

        velocloud_repository._nats_client.request = AsyncMock(return_value=NATS_AIO_MSG)

        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=datetime(year=2022, month=1, day=1, hour=12))

        with uuid_mock:
            with patch.object(velocloud_repository_module, "datetime", new=datetime_mock):
                result = await velocloud_repository.get_gateway_status_metrics(gateway)

        velocloud_repository._nats_client.request.assert_awaited_once_with(
            "request.gateway.status.metrics", to_json_bytes(request), timeout=30
        )
        assert result == response
