import json
from typing import Any
from unittest.mock import AsyncMock, Mock, patch

import pytest
from nats.aio.msg import Msg
from shortuuid import uuid

from application import nats_error_response
from application.repositories import hawkeye_repository as hawkeye_repository_module
from application.repositories.hawkeye_repository import HawkeyeRepository
from config import testconfig

uuid_ = uuid()
uuid_mock = patch.object(hawkeye_repository_module, "uuid", return_value=uuid_)


@pytest.fixture(scope="function")
def hawkeye_repository():
    return HawkeyeRepository(
        nats_client=Mock(),
        notifications_repository=Mock(),
    )


def to_json_bytes(message: dict[str, Any]):
    return json.dumps(message, default=str, separators=(",", ":")).encode()


class TestHawkeyeRepository:
    def instance_test(self):
        nats_client = Mock()
        notifications_repository = Mock()

        hawkeye_repository = HawkeyeRepository(nats_client, notifications_repository)

        assert hawkeye_repository._nats_client is nats_client
        assert hawkeye_repository._notifications_repository is notifications_repository

    @pytest.mark.asyncio
    async def get_probes_ok_test(self, hawkeye_repository):
        request = {
            "request_id": uuid_,
            "body": {},
        }
        response = {
            "request_id": uuid_,
            "body": [
                {
                    "probeId": "27",
                    "uid": "b8:27:eb:76:a8:de",
                    "os": "Linux ARM",
                    "name": "FIS_Demo_XrPi",
                    "testIp": "none",
                    "managementIp": "none",
                    "active": "1",
                    "type": "8",
                    "mode": "Automatic",
                    "n2nMode": "1",
                    "rsMode": "1",
                    "typeName": "xr_pi",
                    "serialNumber": "B827EB76A8DE",
                    "probeGroup": "FIS",
                    "location": "",
                    "latitude": "0",
                    "longitude": "0",
                    "endpointVersion": "9.6 SP1 build 121",
                    "xrVersion": "4.2.2.10681008",
                    "defaultInterface": "eth0",
                    "defaultGateway": "192.168.90.99",
                    "availableForMesh": "1",
                    "lastRestart": "2020-10-15T02:13:24Z",
                    "availability": {"from": 1, "to": 1, "mesh": "1"},
                    "ips": ["192.168.90.102", "192.226.111.211"],
                    "userGroups": ["1", "10"],
                    "wifi": {
                        "available": 0,
                        "associated": 0,
                        "bssid": "",
                        "ssid": "",
                        "frequency": "",
                        "level": "0",
                        "bitrate": "",
                    },
                    "nodetonode": {"status": 0, "lastUpdate": "2020-11-06T10:38:07Z"},
                    "realservice": {"status": 0, "lastUpdate": "2020-10-15T02:18:28Z"},
                }
            ],
            "status": 200,
        }
        NATS_AIO_MSG = Msg(_client="NATS", data=to_json_bytes(response))
        hawkeye_repository._nats_client.request = AsyncMock(return_value=NATS_AIO_MSG)

        with uuid_mock:
            result = await hawkeye_repository.get_probes()

        hawkeye_repository._nats_client.request.assert_awaited_once_with(
            "hawkeye.probe.request", to_json_bytes(request), timeout=60
        )
        assert result == response

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
    async def get_probes_with_request_returning_non_2xx_status_test(self, hawkeye_repository):
        request = {
            "request_id": uuid_,
            "body": {},
        }
        response = {
            "request_id": uuid_,
            "body": "Got internal error from Hawkeye",
            "status": 500,
        }
        NATS_AIO_MSG = Msg(_client="NATS", data=to_json_bytes(response))
        hawkeye_repository._nats_client.request = AsyncMock(return_value=NATS_AIO_MSG)

        hawkeye_repository._notifications_repository.send_slack_message = AsyncMock()

        with uuid_mock:
            result = await hawkeye_repository.get_probes()

        hawkeye_repository._nats_client.request.assert_awaited_once_with(
            "hawkeye.probe.request", to_json_bytes(request), timeout=60
        )
        hawkeye_repository._notifications_repository.send_slack_message.assert_awaited_once()
        assert result == response
