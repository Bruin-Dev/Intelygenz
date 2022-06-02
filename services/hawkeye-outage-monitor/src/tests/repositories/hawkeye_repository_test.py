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
    async def get_probes_ok_test(self):
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

        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        hawkeye_repository = HawkeyeRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await hawkeye_repository.get_probes()

        event_bus.rpc_request.assert_awaited_once_with("hawkeye.probe.request", request, timeout=60)
        assert result == response

    @pytest.mark.asyncio
    async def get_probes_with_rpc_request_failing_test(self):
        request = {
            "request_id": uuid_,
            "body": {},
        }

        logger = Mock()
        config = testconfig

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(side_effect=Exception)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        hawkeye_repository = HawkeyeRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await hawkeye_repository.get_probes()

        event_bus.rpc_request.assert_awaited_once_with("hawkeye.probe.request", request, timeout=60)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == nats_error_response

    @pytest.mark.asyncio
    async def get_probes_with_rpc_request_returning_non_2xx_status_test(self):
        request = {
            "request_id": uuid_,
            "body": {},
        }
        response = {
            "request_id": uuid_,
            "body": "Got internal error from Hawkeye",
            "status": 500,
        }

        logger = Mock()
        config = testconfig

        event_bus = Mock()
        event_bus.rpc_request = CoroutineMock(return_value=response)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        hawkeye_repository = HawkeyeRepository(event_bus, logger, config, notifications_repository)

        with uuid_mock:
            result = await hawkeye_repository.get_probes()

        event_bus.rpc_request.assert_awaited_once_with("hawkeye.probe.request", request, timeout=60)
        notifications_repository.send_slack_message.assert_awaited_once()
        logger.error.assert_called_once()
        assert result == response
