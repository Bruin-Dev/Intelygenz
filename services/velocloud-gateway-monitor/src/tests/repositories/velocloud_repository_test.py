from datetime import datetime, timedelta
from http import HTTPStatus
from unittest.mock import patch

import pytest
from application.repositories import velocloud_repository as velocloud_repository_module
from asynctest import CoroutineMock
from config import testconfig
from shortuuid import uuid

uuid_ = uuid()
uuid_mock = patch.object(velocloud_repository_module, "uuid", return_value=uuid_)


class TestVelocloudRepository:
    def instance_test(self, velocloud_repository, event_bus, notifications_repository):
        assert velocloud_repository._event_bus is event_bus
        assert velocloud_repository._notifications_repository is notifications_repository
        assert velocloud_repository._config is testconfig

    @pytest.mark.asyncio
    async def get_network_gateway_status_list_test(
        self,
        velocloud_repository,
        make_network_gateway_status_body,
        make_rpc_request,
        make_rpc_response,
    ):
        velocloud_host = "mettel.velocloud.net"
        metrics = ["tunnelCount"]
        since = (datetime.now() - timedelta(minutes=5)).strftime("%m/%d/%Y, %H:%M:%S")
        payload = {
            "host": velocloud_host,
            "since": since,
            "metrics": metrics,
        }
        gateway_ids = [3]
        response_status = HTTPStatus.OK
        response_body = make_network_gateway_status_body(gateway_ids=gateway_ids)
        request = make_rpc_request(request_id=uuid_, body=payload)
        expected_response = make_rpc_response(request_id=uuid_, body=response_body, status=response_status)
        velocloud_repository._event_bus.rpc_request = CoroutineMock(return_value=expected_response)

        with uuid_mock:
            response = await velocloud_repository.get_network_gateway_status_list(
                velocloud_host, since=since, metrics=metrics
            )

        velocloud_repository._event_bus.rpc_request.assert_awaited_once_with(
            "request.network.gateway.status", request, timeout=30
        )
        assert response == expected_response
