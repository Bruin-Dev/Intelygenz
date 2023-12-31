import os
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, Mock, call, patch

import pytest
from application.actions import outage_monitoring as outage_monitoring_module
from application.actions.outage_monitoring import OutageMonitor
from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.util import undefined
from config import testconfig
from dateutil.parser import parse
from pytz import timezone, utc
from shortuuid import uuid

uuid_ = uuid()
uuid_mock = patch.object(outage_monitoring_module, "uuid", return_value=uuid_)


@pytest.fixture(scope="function")
def outage_monitor_instance():
    return OutageMonitor(
        nats_client=Mock(),
        scheduler=Mock(),
        config=testconfig,
        metrics_repository=Mock(),
        bruin_repository=Mock(),
        hawkeye_repository=Mock(),
        notifications_repository=Mock(),
        customer_cache_repository=Mock(),
        utils_repository=Mock(),
    )


class TestServiceOutageMonitor:
    def instance_test(self, outage_monitor_instance):
        nats_client = Mock()
        scheduler = Mock()
        metrics_repository = Mock()
        bruin_repository = Mock()
        hawkeye_repository = Mock()
        notifications_repository = Mock()
        customer_cache_repository = Mock()
        utils_repository = Mock()
        outage_monitor = OutageMonitor(
            nats_client=nats_client,
            scheduler=scheduler,
            config=testconfig,
            metrics_repository=metrics_repository,
            bruin_repository=bruin_repository,
            hawkeye_repository=hawkeye_repository,
            notifications_repository=notifications_repository,
            customer_cache_repository=customer_cache_repository,
            utils_repository=utils_repository,
        )

        assert outage_monitor._nats_client is nats_client
        assert outage_monitor._scheduler is scheduler
        assert outage_monitor._config is testconfig
        assert outage_monitor._metrics_repository is metrics_repository
        assert outage_monitor._bruin_repository is bruin_repository
        assert outage_monitor._hawkeye_repository is hawkeye_repository
        assert outage_monitor._notifications_repository is notifications_repository
        assert outage_monitor._customer_cache_repository is customer_cache_repository

    @pytest.mark.asyncio
    async def start_hawkeye_outage_monitoring_with_exec_on_start_test(self, outage_monitor_instance):

        next_run_time = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)
        with patch.object(outage_monitoring_module, "datetime", new=datetime_mock):
            with patch.object(outage_monitoring_module, "timezone", new=Mock()):
                await outage_monitor_instance.start_hawkeye_outage_monitoring(exec_on_start=True)

        outage_monitor_instance._scheduler.add_job.assert_called_once_with(
            outage_monitor_instance._outage_monitoring_process,
            "interval",
            seconds=outage_monitor_instance._config.MONITOR_CONFIG["jobs_intervals"]["outage_monitor"],
            next_run_time=next_run_time,
            replace_existing=False,
            id="_hawkeye_outage_monitor_process",
        )

    @pytest.mark.asyncio
    async def start_hawkeye_outage_monitoring_with_no_exec_on_start_test(self, outage_monitor_instance):

        await outage_monitor_instance.start_hawkeye_outage_monitoring(exec_on_start=False)

        outage_monitor_instance._scheduler.add_job.assert_called_once_with(
            outage_monitor_instance._outage_monitoring_process,
            "interval",
            seconds=outage_monitor_instance._config.MONITOR_CONFIG["jobs_intervals"]["outage_monitor"],
            next_run_time=undefined,
            replace_existing=False,
            id="_hawkeye_outage_monitor_process",
        )

    @pytest.mark.asyncio
    async def start_hawkeye_outage_monitoring_with_job_id_already_executing_test(self, outage_monitor_instance):
        job_id = "some-duplicated-id"
        exception_instance = ConflictingIdError(job_id)

        outage_monitor_instance._scheduler.add_job = Mock(side_effect=exception_instance)

        try:
            await outage_monitor_instance.start_hawkeye_outage_monitoring(exec_on_start=False)
            # TODO: The test should fail at this point if no exception was raised
        except ConflictingIdError:
            outage_monitor_instance._scheduler.add_job.assert_called_once_with(
                outage_monitor_instance._outage_monitoring_process,
                "interval",
                seconds=outage_monitor_instance._config.MONITOR_CONFIG["jobs_intervals"]["outage_monitor"],
                next_run_time=undefined,
                replace_existing=False,
                id="_hawkeye_outage_monitor_process",
            )

    @pytest.mark.asyncio
    async def outage_monitoring_process_ok_test(self, outage_monitor_instance):
        device_1_cached_info = {
            "serial_number": "B827EB76A8DE",
            "last_contact": "2020-01-16T14:59:56.245Z",
            "bruin_client_info": {
                "client_id": 9994,
                "client_name": "METTEL/NEW YORK",
            },
        }
        device_2_cached_info = {
            "serial_number": "C827FC76B8EF",
            "last_contact": "2020-01-16T14:59:56.245Z",
            "bruin_client_info": {
                "client_id": 9994,
                "client_name": "METTEL/NEW YORK",
            },
        }
        device_3_cached_info = {
            "serial_number": "D827GD76C8FG",
            "last_contact": "2020-01-16T14:59:56.245Z",
            "bruin_client_info": {
                "client_id": 9994,
                "client_name": "METTEL/NEW YORK",
            },
        }
        customer_cache = [
            device_1_cached_info,
            device_2_cached_info,
            device_3_cached_info,
        ]
        customer_cache_response = {
            "body": customer_cache,
            "status": 200,
        }

        probe_1_info = {
            "probeId": "1",
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
            "nodetonode": {"status": 1, "lastUpdate": "2020-11-11T13:00:11Z"},
            "realservice": {"status": 1, "lastUpdate": "2020-10-15T02:18:28Z"},
        }
        probe_2_info = {
            "probeId": "2",
            "uid": "b8:27:eb:76:a8:de",
            "os": "Linux ARM",
            "name": "FIS_Demo_XrPi",
            "testIp": "none",
            "managementIp": "none",
            "active": "0",
            "type": "8",
            "mode": "Automatic",
            "n2nMode": "1",
            "rsMode": "1",
            "typeName": "xr_pi",
            "serialNumber": "C827FC76B8EF",
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
            "nodetonode": {"status": 1, "lastUpdate": "2020-11-11T13:00:11Z"},
            "realservice": {"status": 1, "lastUpdate": "2020-10-15T02:18:28Z"},
        }
        probe_3_info = {
            "probeId": "3",
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
            "serialNumber": "D827GD76C8FG",
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
            "nodetonode": {"status": 0, "lastUpdate": "2020-11-11T13:00:11Z"},
            "realservice": {"status": 0, "lastUpdate": "2020-10-15T02:18:28Z"},
        }
        probes = [
            probe_1_info,
            probe_2_info,
            probe_3_info,
        ]
        probes_response = {
            "body": probes,
            "status": 200,
        }

        active_probes = [
            probe_1_info,
            probe_3_info,
        ]

        active_probe_with_cached_info_1 = {
            "device_info": probe_1_info,
            "cached_info": device_1_cached_info,
        }
        active_probe_with_cached_info_3 = {
            "device_info": probe_3_info,
            "cached_info": device_3_cached_info,
        }
        active_probes_with_customer_cache_info = [
            active_probe_with_cached_info_1,
            active_probe_with_cached_info_3,
        ]

        healthy_devices_info = [
            active_probe_with_cached_info_1,
        ]
        outage_devices_info = [
            active_probe_with_cached_info_3,
        ]

        outage_monitor_instance._customer_cache_repository.get_cache_for_outage_monitoring = AsyncMock(
            return_value=customer_cache_response
        )

        outage_monitor_instance._hawkeye_repository.get_probes = AsyncMock(return_value=probes_response)

        outage_monitor_instance._map_probes_info_with_customer_cache = Mock(
            return_value=active_probes_with_customer_cache_info
        )
        outage_monitor_instance._schedule_recheck_job_for_devices = Mock()
        outage_monitor_instance._run_ticket_autoresolve = AsyncMock()

        await outage_monitor_instance._outage_monitoring_process()

        outage_monitor_instance._customer_cache_repository.get_cache_for_outage_monitoring.assert_awaited_once()
        outage_monitor_instance._hawkeye_repository.get_probes.assert_awaited_once()
        outage_monitor_instance._map_probes_info_with_customer_cache.assert_called_once_with(
            active_probes, customer_cache
        )
        outage_monitor_instance._schedule_recheck_job_for_devices.assert_called_once_with(outage_devices_info)
        outage_monitor_instance._run_ticket_autoresolve.assert_awaited_once_with(healthy_devices_info[0])

    @pytest.mark.asyncio
    async def outage_monitoring_process_with_customer_cache_response_having_202_status_test(
        self, outage_monitor_instance
    ):
        customer_cache_response = {
            "body": "Cache is still being built",
            "status": 202,
        }

        outage_monitor_instance._customer_cache_repository.get_cache_for_outage_monitoring = AsyncMock(
            return_value=customer_cache_response
        )

        outage_monitor_instance._hawkeye_repository.get_probes = AsyncMock()

        outage_monitor_instance._map_probes_info_with_customer_cache = Mock()
        outage_monitor_instance._schedule_recheck_job_for_devices = Mock()
        outage_monitor_instance._run_ticket_autoresolve = AsyncMock()

        await outage_monitor_instance._outage_monitoring_process()

        outage_monitor_instance._customer_cache_repository.get_cache_for_outage_monitoring.assert_awaited_once()
        outage_monitor_instance._hawkeye_repository.get_probes.assert_not_awaited()
        outage_monitor_instance._map_probes_info_with_customer_cache.assert_not_called()
        outage_monitor_instance._schedule_recheck_job_for_devices.assert_not_called()
        outage_monitor_instance._run_ticket_autoresolve.assert_not_awaited()

    @pytest.mark.asyncio
    async def outage_monitoring_process_with_customer_cache_response_having_non_2xx_status_test(
        self, outage_monitor_instance
    ):
        customer_cache_response = {
            "body": "No devices were found for the specified filters",
            "status": 404,
        }

        outage_monitor_instance._customer_cache_repository.get_cache_for_outage_monitoring = AsyncMock(
            return_value=customer_cache_response
        )

        outage_monitor_instance._hawkeye_repository.get_probes = AsyncMock()

        outage_monitor_instance._map_probes_info_with_customer_cache = Mock()
        outage_monitor_instance._schedule_recheck_job_for_devices = Mock()
        outage_monitor_instance._run_ticket_autoresolve = AsyncMock()

        await outage_monitor_instance._outage_monitoring_process()

        outage_monitor_instance._customer_cache_repository.get_cache_for_outage_monitoring.assert_awaited_once()
        outage_monitor_instance._hawkeye_repository.get_probes.assert_not_awaited()
        outage_monitor_instance._map_probes_info_with_customer_cache.assert_not_called()
        outage_monitor_instance._schedule_recheck_job_for_devices.assert_not_called()
        outage_monitor_instance._run_ticket_autoresolve.assert_not_awaited()

    @pytest.mark.asyncio
    async def outage_monitoring_process_with_get_probes_response_having_non_2xx_status_test(
        self, outage_monitor_instance
    ):
        device_1_cached_info = {
            "serial_number": "B827EB76A8DE",
            "last_contact": "2020-01-16T14:59:56.245Z",
            "bruin_client_info": {
                "client_id": 9994,
                "client_name": "METTEL/NEW YORK",
            },
        }
        device_2_cached_info = {
            "serial_number": "C827FC76B8EF",
            "last_contact": "2020-01-16T14:59:56.245Z",
            "bruin_client_info": {
                "client_id": 9994,
                "client_name": "METTEL/NEW YORK",
            },
        }
        device_3_cached_info = {
            "serial_number": "D827GD76C8FG",
            "last_contact": "2020-01-16T14:59:56.245Z",
            "bruin_client_info": {
                "client_id": 9994,
                "client_name": "METTEL/NEW YORK",
            },
        }
        customer_cache = [
            device_1_cached_info,
            device_2_cached_info,
            device_3_cached_info,
        ]
        customer_cache_response = {
            "body": customer_cache,
            "status": 200,
        }

        probes_response = {
            "body": "Got internal error from Hawkeye",
            "status": 500,
        }

        outage_monitor_instance._customer_cache_repository.get_cache_for_outage_monitoring = AsyncMock(
            return_value=customer_cache_response
        )

        outage_monitor_instance._hawkeye_repository.get_probes = AsyncMock(return_value=probes_response)

        outage_monitor_instance._map_probes_info_with_customer_cache = Mock()
        outage_monitor_instance._schedule_recheck_job_for_devices = Mock()
        outage_monitor_instance._run_ticket_autoresolve = AsyncMock()

        await outage_monitor_instance._outage_monitoring_process()

        outage_monitor_instance._customer_cache_repository.get_cache_for_outage_monitoring.assert_awaited_once()
        outage_monitor_instance._hawkeye_repository.get_probes.assert_awaited_once()
        outage_monitor_instance._map_probes_info_with_customer_cache.assert_not_called()
        outage_monitor_instance._schedule_recheck_job_for_devices.assert_not_called()
        outage_monitor_instance._run_ticket_autoresolve.assert_not_awaited()

    @pytest.mark.asyncio
    async def outage_monitoring_process_with_empty_list_of_probes_test(self, outage_monitor_instance):
        device_1_cached_info = {
            "serial_number": "B827EB76A8DE",
            "last_contact": "2020-01-16T14:59:56.245Z",
            "bruin_client_info": {
                "client_id": 9994,
                "client_name": "METTEL/NEW YORK",
            },
        }
        device_2_cached_info = {
            "serial_number": "C827FC76B8EF",
            "last_contact": "2020-01-16T14:59:56.245Z",
            "bruin_client_info": {
                "client_id": 9994,
                "client_name": "METTEL/NEW YORK",
            },
        }
        device_3_cached_info = {
            "serial_number": "D827GD76C8FG",
            "last_contact": "2020-01-16T14:59:56.245Z",
            "bruin_client_info": {
                "client_id": 9994,
                "client_name": "METTEL/NEW YORK",
            },
        }
        customer_cache = [
            device_1_cached_info,
            device_2_cached_info,
            device_3_cached_info,
        ]
        customer_cache_response = {
            "body": customer_cache,
            "status": 200,
        }

        probes_response = {
            "body": [],
            "status": 200,
        }

        outage_monitor_instance._customer_cache_repository.get_cache_for_outage_monitoring = AsyncMock(
            return_value=customer_cache_response
        )

        outage_monitor_instance._hawkeye_repository.get_probes = AsyncMock(return_value=probes_response)
        outage_monitor_instance._map_probes_info_with_customer_cache = Mock()
        outage_monitor_instance._schedule_recheck_job_for_devices = Mock()
        outage_monitor_instance._run_ticket_autoresolve = AsyncMock()

        await outage_monitor_instance._outage_monitoring_process()

        outage_monitor_instance._customer_cache_repository.get_cache_for_outage_monitoring.assert_awaited_once()
        outage_monitor_instance._hawkeye_repository.get_probes.assert_awaited_once()
        outage_monitor_instance._map_probes_info_with_customer_cache.assert_not_called()
        outage_monitor_instance._schedule_recheck_job_for_devices.assert_not_called()
        outage_monitor_instance._run_ticket_autoresolve.assert_not_awaited()

    @pytest.mark.asyncio
    async def outage_monitoring_process_with_no_active_probes_test(self, outage_monitor_instance):
        device_1_cached_info = {
            "serial_number": "B827EB76A8DE",
            "last_contact": "2020-01-16T14:59:56.245Z",
            "bruin_client_info": {
                "client_id": 9994,
                "client_name": "METTEL/NEW YORK",
            },
        }
        device_2_cached_info = {
            "serial_number": "C827FC76B8EF",
            "last_contact": "2020-01-16T14:59:56.245Z",
            "bruin_client_info": {
                "client_id": 9994,
                "client_name": "METTEL/NEW YORK",
            },
        }
        device_3_cached_info = {
            "serial_number": "D827GD76C8FG",
            "last_contact": "2020-01-16T14:59:56.245Z",
            "bruin_client_info": {
                "client_id": 9994,
                "client_name": "METTEL/NEW YORK",
            },
        }
        customer_cache = [
            device_1_cached_info,
            device_2_cached_info,
            device_3_cached_info,
        ]
        customer_cache_response = {
            "body": customer_cache,
            "status": 200,
        }

        probes_response = {
            "body": [
                {
                    "probeId": "1",
                    "uid": "b8:27:eb:76:a8:de",
                    "os": "Linux ARM",
                    "name": "FIS_Demo_XrPi",
                    "testIp": "none",
                    "managementIp": "none",
                    "active": "0",
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
                    "nodetonode": {"status": 1, "lastUpdate": "2020-11-11T13:00:11Z"},
                    "realservice": {"status": 1, "lastUpdate": "2020-10-15T02:18:28Z"},
                }
            ],
            "status": 200,
        }

        outage_monitor_instance._customer_cache_repository.get_cache_for_outage_monitoring = AsyncMock(
            return_value=customer_cache_response
        )

        outage_monitor_instance._hawkeye_repository.get_probes = AsyncMock(return_value=probes_response)

        outage_monitor_instance._map_probes_info_with_customer_cache = Mock()
        outage_monitor_instance._schedule_recheck_job_for_devices = Mock()
        outage_monitor_instance._run_ticket_autoresolve = AsyncMock()

        await outage_monitor_instance._outage_monitoring_process()

        outage_monitor_instance._customer_cache_repository.get_cache_for_outage_monitoring.assert_awaited_once()
        outage_monitor_instance._hawkeye_repository.get_probes.assert_awaited_once()
        outage_monitor_instance._map_probes_info_with_customer_cache.assert_not_called()
        outage_monitor_instance._schedule_recheck_job_for_devices.assert_not_called()
        outage_monitor_instance._run_ticket_autoresolve.assert_not_awaited()

    def is_active_probe_test(self, outage_monitor_instance):
        probe = {
            "probeId": "1",
            "uid": "b8:27:eb:76:a8:de",
            "os": "Linux ARM",
            "name": "FIS_Demo_XrPi",
            "testIp": "none",
            "managementIp": "none",
            "active": "1",
            # Omitting a few keys for simplicity
        }
        result = OutageMonitor._is_active_probe(probe)
        assert result is True

        probe = {
            "probeId": "1",
            "uid": "b8:27:eb:76:a8:de",
            "os": "Linux ARM",
            "name": "FIS_Demo_XrPi",
            "testIp": "none",
            "managementIp": "none",
            "active": "0",
            # Omitting a few keys for simplicity
        }
        result = OutageMonitor._is_active_probe(probe)
        assert result is False

    def is_there_an_outage_test(self, outage_monitor_instance):

        probe = {
            "probeId": "1",
            "uid": "b8:27:eb:76:a8:de",
            "os": "Linux ARM",
            "name": "FIS_Demo_XrPi",
            "testIp": "none",
            "managementIp": "none",
            "active": "1",
            # Omitting a few keys for simplicity
            "nodetonode": {"status": 1, "lastUpdate": "2020-11-11T13:00:11Z"},
            "realservice": {"status": 1, "lastUpdate": "2020-10-15T02:18:28Z"},
        }
        result = outage_monitor_instance._is_there_an_outage(probe)
        assert result is False

        probe = {
            "probeId": "1",
            "uid": "b8:27:eb:76:a8:de",
            "os": "Linux ARM",
            "name": "FIS_Demo_XrPi",
            "testIp": "none",
            "managementIp": "none",
            "active": "1",
            # Omitting a few keys for simplicity
            "nodetonode": {"status": 0, "lastUpdate": "2020-11-11T13:00:11Z"},
            "realservice": {"status": 1, "lastUpdate": "2020-10-15T02:18:28Z"},
        }
        result = outage_monitor_instance._is_there_an_outage(probe)
        assert result is True

        probe = {
            "probeId": "1",
            "uid": "b8:27:eb:76:a8:de",
            "os": "Linux ARM",
            "name": "FIS_Demo_XrPi",
            "testIp": "none",
            "managementIp": "none",
            "active": "1",
            # Omitting a few keys for simplicity
            "nodetonode": {"status": 1, "lastUpdate": "2020-11-11T13:00:11Z"},
            "realservice": {"status": 0, "lastUpdate": "2020-10-15T02:18:28Z"},
        }
        result = outage_monitor_instance._is_there_an_outage(probe)
        assert result is True

        probe = {
            "probeId": "1",
            "uid": "b8:27:eb:76:a8:de",
            "os": "Linux ARM",
            "name": "FIS_Demo_XrPi",
            "testIp": "none",
            "managementIp": "none",
            "active": "1",
            # Omitting a few keys for simplicity
            "nodetonode": {"status": 0, "lastUpdate": "2020-11-11T13:00:11Z"},
            "realservice": {"status": 0, "lastUpdate": "2020-10-15T02:18:28Z"},
        }
        result = outage_monitor_instance._is_there_an_outage(probe)
        assert result is True

    def map_probes_info_with_customer_cache_test(self, outage_monitor_instance):
        serial_number_1 = "B827EB76A8DE"
        serial_number_2 = "C827FC76B8EF"
        serial_number_3 = "D827GD76C8FG"
        serial_number_4 = "E827HE76D8GH"
        serial_number_5 = "F827IF76E8HI"

        probe_1 = {
            "probeId": "1",
            "uid": "b8:27:eb:76:a8:de",
            "os": "Linux ARM",
            "name": "FIS_Demo_XrPi",
            "testIp": "none",
            "managementIp": "none",
            "active": "1",
            "serialNumber": serial_number_1,
            # Omitting a few keys for simplicity
        }
        probe_2 = {
            "probeId": "2",
            "uid": "b8:27:eb:76:a8:de",
            "os": "Linux ARM",
            "name": "FIS_Demo_XrPi",
            "testIp": "none",
            "managementIp": "none",
            "active": "1",
            "serialNumber": serial_number_3,
            # Omitting a few keys for simplicity
        }
        probe_3 = {
            "probeId": "3",
            "uid": "b8:27:eb:76:a8:de",
            "os": "Linux ARM",
            "name": "FIS_Demo_XrPi",
            "testIp": "none",
            "managementIp": "none",
            "active": "1",
            "serialNumber": serial_number_5,
            # Omitting a few keys for simplicity
        }
        probes = [
            probe_1,
            probe_2,
            probe_3,
        ]

        device_1_cached_info = {
            "serial_number": serial_number_1,
            "last_contact": "2020-01-16T14:59:56.245Z",
            "bruin_client_info": {
                "client_id": 9994,
                "client_name": "METTEL/NEW YORK",
            },
        }
        device_2_cached_info = {
            "serial_number": serial_number_2,
            "last_contact": "2020-01-16T14:59:56.245Z",
            "bruin_client_info": {
                "client_id": 9994,
                "client_name": "METTEL/NEW YORK",
            },
        }
        device_3_cached_info = {
            "serial_number": serial_number_3,
            "last_contact": "2020-01-16T14:59:56.245Z",
            "bruin_client_info": {
                "client_id": 9994,
                "client_name": "METTEL/NEW YORK",
            },
        }
        device_4_cached_info = {
            "serial_number": serial_number_4,
            "last_contact": "2020-01-16T14:59:56.245Z",
            "bruin_client_info": {
                "client_id": 9994,
                "client_name": "METTEL/NEW YORK",
            },
        }
        customer_cache = [
            device_1_cached_info,
            device_2_cached_info,
            device_3_cached_info,
            device_4_cached_info,
        ]

        result = outage_monitor_instance._map_probes_info_with_customer_cache(probes, customer_cache)

        expected = [
            {
                "device_info": probe_1,
                "cached_info": device_1_cached_info,
            },
            {
                "device_info": probe_2,
                "cached_info": device_3_cached_info,
            },
        ]
        assert result == expected

    def schedule_recheck_job_for_devices_test(self, outage_monitor_instance):
        devices = [
            {
                "cached_info": {
                    "serial_number": "B827EB76A8DE",
                    "last_contact": "2020-08-17T02:23:59",
                    "bruin_client_info": {
                        "client_id": 9994,
                        "client_name": "METTEL/NEW YORK",
                    },
                },
                "device_info": [
                    {
                        "probeId": "3",
                        "uid": "b8:27:eb:76:a8:de",
                        "os": "Linux ARM",
                        "name": "FIS_Demo_XrPi",
                        "testIp": "none",
                        "managementIp": "none",
                        "active": "1",
                        "serialNumber": "B827EB76A8DE",
                        # Omitting a few keys for simplicity
                    }
                ],
            }
        ]

        next_run_time = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)
        with patch.object(outage_monitoring_module, "datetime", new=datetime_mock):
            with patch.object(outage_monitoring_module, "timezone", new=Mock()):
                outage_monitor_instance._schedule_recheck_job_for_devices(devices)

        expected_run_date = next_run_time + timedelta(
            seconds=outage_monitor_instance._config.MONITOR_CONFIG["jobs_intervals"]["quarantine"]
        )
        outage_monitor_instance._scheduler.add_job.assert_called_once_with(
            outage_monitor_instance._recheck_devices_for_ticket_creation,
            "date",
            args=[devices],
            run_date=expected_run_date,
            replace_existing=False,
            misfire_grace_time=9999,
            id=f"_ticket_creation_recheck",
        )

    @pytest.mark.asyncio
    async def recheck_devices_with_just_devices_in_outage_state_and_creation_response_having_2xx_status_test(
        self, outage_monitor_instance
    ):
        serial_number_1 = "B827EB76A8DE"
        serial_number_2 = "D827GD76C8FG"

        probe_1_info = {
            "probeId": "1",
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
            "serialNumber": serial_number_1,
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
            "nodetonode": {"status": 0, "lastUpdate": "2020-11-11T13:00:11Z"},
            "realservice": {"status": 1, "lastUpdate": "2020-10-15T02:18:28Z"},
        }
        probe_2_info = {
            "probeId": "3",
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
            "serialNumber": serial_number_2,
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
            "nodetonode": {"status": 0, "lastUpdate": "2020-11-11T13:00:11Z"},
            "realservice": {"status": 1, "lastUpdate": "2020-10-15T02:18:28Z"},
        }

        bruin_client_id = 9994
        device_1_cached_info = {
            "serial_number": serial_number_1,
            "last_contact": "2020-01-16T14:59:56.245Z",
            "bruin_client_info": {
                "client_id": bruin_client_id,
                "client_name": "METTEL/NEW YORK",
            },
        }
        device_2_cached_info = {
            "serial_number": serial_number_2,
            "last_contact": "2020-01-16T14:59:56.245Z",
            "bruin_client_info": {
                "client_id": bruin_client_id,
                "client_name": "METTEL/NEW YORK",
            },
        }
        devices_cached_info = [
            device_1_cached_info,
            device_2_cached_info,
        ]

        device_1_info = {
            "device_info": probe_1_info,
            "cached_info": device_1_cached_info,
        }
        device_2_info = {
            "device_info": probe_2_info,
            "cached_info": device_2_cached_info,
        }
        devices_info = [
            device_1_info,
            device_2_info,
        ]

        probes = [
            probe_1_info,
            probe_2_info,
        ]
        probes_response = {
            "body": probes,
            "status": 200,
        }

        ticket_id = 12345
        create_ticket_response = {
            "body": ticket_id,
            "status": 200,
        }

        triage_note = "This is Hawkeye's triage note"

        outage_monitor_instance._bruin_repository.create_outage_ticket = AsyncMock(return_value=create_ticket_response)
        outage_monitor_instance._bruin_repository.append_triage_note_to_ticket = AsyncMock()

        outage_monitor_instance._hawkeye_repository.get_probes = AsyncMock(return_value=probes_response)

        outage_monitor_instance._notifications_repository.send_slack_message = AsyncMock()

        outage_monitor_instance._map_probes_info_with_customer_cache = Mock(return_value=devices_info)
        outage_monitor_instance._build_triage_note = Mock(return_value=triage_note)
        outage_monitor_instance._run_ticket_autoresolve = AsyncMock()

        with patch.object(outage_monitor_instance._config, "CURRENT_ENVIRONMENT", "production"):
            await outage_monitor_instance._recheck_devices_for_ticket_creation(devices_info)

        outage_monitor_instance._hawkeye_repository.get_probes.assert_awaited_once()
        outage_monitor_instance._map_probes_info_with_customer_cache.assert_called_once_with(
            probes, devices_cached_info
        )
        outage_monitor_instance._bruin_repository.create_outage_ticket.assert_has_awaits(
            [
                call(bruin_client_id, serial_number_1),
                call(bruin_client_id, serial_number_2),
            ]
        )
        outage_monitor_instance._build_triage_note.assert_has_calls(
            [
                call(probe_1_info),
                call(probe_2_info),
            ]
        )
        outage_monitor_instance._bruin_repository.append_triage_note_to_ticket.assert_has_awaits(
            [
                call(ticket_id, serial_number_1, triage_note),
                call(ticket_id, serial_number_2, triage_note),
            ]
        )
        outage_monitor_instance._run_ticket_autoresolve.assert_not_awaited()

    @pytest.mark.asyncio
    async def recheck_devices_with_just_devices_in_outage_state_and_creation_response_having_409_status_test(
        self, outage_monitor_instance
    ):
        serial_number_1 = "B827EB76A8DE"
        serial_number_2 = "D827GD76C8FG"

        probe_1_info = {
            "probeId": "1",
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
            "serialNumber": serial_number_1,
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
            "nodetonode": {"status": 0, "lastUpdate": "2020-11-11T13:00:11Z"},
            "realservice": {"status": 1, "lastUpdate": "2020-10-15T02:18:28Z"},
        }
        probe_2_info = {
            "probeId": "3",
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
            "serialNumber": serial_number_2,
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
            "nodetonode": {"status": 0, "lastUpdate": "2020-11-11T13:00:11Z"},
            "realservice": {"status": 1, "lastUpdate": "2020-10-15T02:18:28Z"},
        }

        bruin_client_id = 9994
        device_1_cached_info = {
            "serial_number": serial_number_1,
            "last_contact": "2020-01-16T14:59:56.245Z",
            "bruin_client_info": {
                "client_id": bruin_client_id,
                "client_name": "METTEL/NEW YORK",
            },
        }
        device_2_cached_info = {
            "serial_number": serial_number_2,
            "last_contact": "2020-01-16T14:59:56.245Z",
            "bruin_client_info": {
                "client_id": bruin_client_id,
                "client_name": "METTEL/NEW YORK",
            },
        }
        devices_cached_info = [
            device_1_cached_info,
            device_2_cached_info,
        ]

        device_1_info = {
            "device_info": probe_1_info,
            "cached_info": device_1_cached_info,
        }
        device_2_info = {
            "device_info": probe_2_info,
            "cached_info": device_2_cached_info,
        }
        devices_info = [
            device_1_info,
            device_2_info,
        ]

        probes = [
            probe_1_info,
            probe_2_info,
        ]
        probes_response = {
            "body": probes,
            "status": 200,
        }

        ticket_id = 12345
        create_ticket_response = {
            "body": ticket_id,
            "status": 409,
        }

        outage_monitor_instance._bruin_repository.create_outage_ticket = AsyncMock(return_value=create_ticket_response)
        outage_monitor_instance._bruin_repository.append_triage_note_to_ticket = AsyncMock()

        outage_monitor_instance._hawkeye_repository.get_probes = AsyncMock(return_value=probes_response)

        outage_monitor_instance._notifications_repository.send_slack_message = AsyncMock()

        outage_monitor_instance._map_probes_info_with_customer_cache = Mock(return_value=devices_info)
        outage_monitor_instance._build_triage_note = Mock()
        outage_monitor_instance._append_triage_note_if_needed = AsyncMock()
        outage_monitor_instance._run_ticket_autoresolve = AsyncMock()

        with patch.object(outage_monitor_instance._config, "CURRENT_ENVIRONMENT", "production"):
            await outage_monitor_instance._recheck_devices_for_ticket_creation(devices_info)

        outage_monitor_instance._hawkeye_repository.get_probes.assert_awaited_once()
        outage_monitor_instance._map_probes_info_with_customer_cache.assert_called_once_with(
            probes, devices_cached_info
        )
        outage_monitor_instance._bruin_repository.create_outage_ticket.assert_has_awaits(
            [
                call(bruin_client_id, serial_number_1),
                call(bruin_client_id, serial_number_2),
            ]
        )
        outage_monitor_instance._append_triage_note_if_needed.assert_has_awaits(
            [
                call(ticket_id, probe_1_info),
                call(ticket_id, probe_2_info),
            ]
        )
        outage_monitor_instance._run_ticket_autoresolve.assert_not_awaited()

    @pytest.mark.asyncio
    async def recheck_devices_with_just_devices_in_outage_state_and_creation_response_having_471_status_test(
        self, outage_monitor_instance
    ):
        serial_number_1 = "B827EB76A8DE"
        serial_number_2 = "D827GD76C8FG"

        probe_1_info = {
            "probeId": "1",
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
            "serialNumber": serial_number_1,
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
            "nodetonode": {"status": 0, "lastUpdate": "2020-11-11T13:00:11Z"},
            "realservice": {"status": 1, "lastUpdate": "2020-10-15T02:18:28Z"},
        }
        probe_2_info = {
            "probeId": "3",
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
            "serialNumber": serial_number_2,
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
            "nodetonode": {"status": 0, "lastUpdate": "2020-11-11T13:00:11Z"},
            "realservice": {"status": 1, "lastUpdate": "2020-10-15T02:18:28Z"},
        }

        bruin_client_id = 9994
        device_1_cached_info = {
            "serial_number": serial_number_1,
            "last_contact": "2020-01-16T14:59:56.245Z",
            "bruin_client_info": {
                "client_id": bruin_client_id,
                "client_name": "METTEL/NEW YORK",
            },
        }
        device_2_cached_info = {
            "serial_number": serial_number_2,
            "last_contact": "2020-01-16T14:59:56.245Z",
            "bruin_client_info": {
                "client_id": bruin_client_id,
                "client_name": "METTEL/NEW YORK",
            },
        }
        devices_cached_info = [
            device_1_cached_info,
            device_2_cached_info,
        ]

        device_1_info = {
            "device_info": probe_1_info,
            "cached_info": device_1_cached_info,
        }
        device_2_info = {
            "device_info": probe_2_info,
            "cached_info": device_2_cached_info,
        }
        devices_info = [
            device_1_info,
            device_2_info,
        ]

        probes = [
            probe_1_info,
            probe_2_info,
        ]
        probes_response = {
            "body": probes,
            "status": 200,
        }

        ticket_id = 12345
        create_ticket_response = {
            "body": ticket_id,
            "status": 471,
        }

        outage_monitor_instance._bruin_repository.create_outage_ticket = AsyncMock(return_value=create_ticket_response)
        outage_monitor_instance._bruin_repository.append_triage_note_to_ticket = AsyncMock()

        outage_monitor_instance._hawkeye_repository.get_probes = AsyncMock(return_value=probes_response)

        outage_monitor_instance._notifications_repository.send_slack_message = AsyncMock()

        outage_monitor_instance._map_probes_info_with_customer_cache = Mock(return_value=devices_info)
        outage_monitor_instance._build_triage_note = Mock()
        outage_monitor_instance._reopen_outage_ticket = AsyncMock()
        outage_monitor_instance._run_ticket_autoresolve = AsyncMock()

        with patch.object(outage_monitor_instance._config, "CURRENT_ENVIRONMENT", "production"):
            await outage_monitor_instance._recheck_devices_for_ticket_creation(devices_info)

        outage_monitor_instance._hawkeye_repository.get_probes.assert_awaited_once()
        outage_monitor_instance._map_probes_info_with_customer_cache.assert_called_once_with(
            probes, devices_cached_info
        )
        outage_monitor_instance._bruin_repository.create_outage_ticket.assert_has_awaits(
            [
                call(bruin_client_id, serial_number_1),
                call(bruin_client_id, serial_number_2),
            ]
        )
        outage_monitor_instance._build_triage_note.assert_not_called()
        outage_monitor_instance._bruin_repository.append_triage_note_to_ticket.assert_not_awaited()
        outage_monitor_instance._run_ticket_autoresolve.assert_not_awaited()
        outage_monitor_instance._reopen_outage_ticket.assert_has_awaits(
            [
                call(ticket_id, device_1_info),
                call(ticket_id, device_2_info),
            ]
        )

    @pytest.mark.asyncio
    async def recheck_devices_with_just_devices_in_outage_state_and_creation_response_having_472_status_test(
        self, outage_monitor_instance
    ):
        serial_number_1 = "B827EB76A8DE"
        serial_number_2 = "D827GD76C8FG"

        probe_1_info = {
            "probeId": "1",
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
            "serialNumber": serial_number_1,
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
            "nodetonode": {"status": 0, "lastUpdate": "2020-11-11T13:00:11Z"},
            "realservice": {"status": 1, "lastUpdate": "2020-10-15T02:18:28Z"},
        }
        probe_2_info = {
            "probeId": "3",
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
            "serialNumber": serial_number_2,
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
            "nodetonode": {"status": 0, "lastUpdate": "2020-11-11T13:00:11Z"},
            "realservice": {"status": 1, "lastUpdate": "2020-10-15T02:18:28Z"},
        }

        bruin_client_id = 9994
        device_1_cached_info = {
            "serial_number": serial_number_1,
            "last_contact": "2020-01-16T14:59:56.245Z",
            "bruin_client_info": {
                "client_id": bruin_client_id,
                "client_name": "METTEL/NEW YORK",
            },
        }
        device_2_cached_info = {
            "serial_number": serial_number_2,
            "last_contact": "2020-01-16T14:59:56.245Z",
            "bruin_client_info": {
                "client_id": bruin_client_id,
                "client_name": "METTEL/NEW YORK",
            },
        }
        devices_cached_info = [
            device_1_cached_info,
            device_2_cached_info,
        ]

        device_1_info = {
            "device_info": probe_1_info,
            "cached_info": device_1_cached_info,
        }
        device_2_info = {
            "device_info": probe_2_info,
            "cached_info": device_2_cached_info,
        }
        devices_info = [
            device_1_info,
            device_2_info,
        ]

        probes = [
            probe_1_info,
            probe_2_info,
        ]
        probes_response = {
            "body": probes,
            "status": 200,
        }

        ticket_id = 12345
        create_ticket_response = {
            "body": ticket_id,
            "status": 472,
        }

        reopen_note = "#*MetTel's IPA*#\nRe-opening task"

        outage_monitor_instance._bruin_repository.create_outage_ticket = AsyncMock(return_value=create_ticket_response)
        outage_monitor_instance._bruin_repository.append_triage_note_to_ticket = AsyncMock()
        outage_monitor_instance._bruin_repository.append_note_to_ticket = AsyncMock()

        outage_monitor_instance._hawkeye_repository.get_probes = AsyncMock(return_value=probes_response)

        outage_monitor_instance._notifications_repository.send_slack_message = AsyncMock()

        outage_monitor_instance._map_probes_info_with_customer_cache = Mock(return_value=devices_info)
        outage_monitor_instance._build_triage_note = Mock()
        outage_monitor_instance._run_ticket_autoresolve = AsyncMock()
        outage_monitor_instance._build_triage_note = Mock(return_value=reopen_note)

        with patch.object(outage_monitor_instance._config, "CURRENT_ENVIRONMENT", "production"):
            await outage_monitor_instance._recheck_devices_for_ticket_creation(devices_info)

        outage_monitor_instance._hawkeye_repository.get_probes.assert_awaited_once()
        outage_monitor_instance._map_probes_info_with_customer_cache.assert_called_once_with(
            probes, devices_cached_info
        )
        outage_monitor_instance._bruin_repository.create_outage_ticket.assert_has_awaits(
            [
                call(bruin_client_id, serial_number_1),
                call(bruin_client_id, serial_number_2),
            ]
        )
        outage_monitor_instance._build_triage_note.assert_has_calls(
            [
                call(device_1_info["device_info"], is_reopen_note=True),
                call(device_2_info["device_info"], is_reopen_note=True),
            ]
        )
        outage_monitor_instance._bruin_repository.append_note_to_ticket.assert_has_awaits(
            [
                call(ticket_id, reopen_note, service_numbers=[serial_number_1]),
                call(ticket_id, reopen_note, service_numbers=[serial_number_2]),
            ]
        )
        outage_monitor_instance._run_ticket_autoresolve.assert_not_awaited()

    @pytest.mark.asyncio
    async def recheck_devices_with_just_devices_in_outage_state_and_creation_response_having_473_status_test(
        self, outage_monitor_instance
    ):
        serial_number_1 = "B827EB76A8DE"
        serial_number_2 = "D827GD76C8FG"

        probe_1_info = {
            "probeId": "1",
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
            "serialNumber": serial_number_1,
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
            "nodetonode": {"status": 0, "lastUpdate": "2020-11-11T13:00:11Z"},
            "realservice": {"status": 1, "lastUpdate": "2020-10-15T02:18:28Z"},
        }
        probe_2_info = {
            "probeId": "3",
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
            "serialNumber": serial_number_2,
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
            "nodetonode": {"status": 0, "lastUpdate": "2020-11-11T13:00:11Z"},
            "realservice": {"status": 1, "lastUpdate": "2020-10-15T02:18:28Z"},
        }

        bruin_client_id = 9994
        device_1_cached_info = {
            "serial_number": serial_number_1,
            "last_contact": "2020-01-16T14:59:56.245Z",
            "bruin_client_info": {
                "client_id": bruin_client_id,
                "client_name": "METTEL/NEW YORK",
            },
        }
        device_2_cached_info = {
            "serial_number": serial_number_2,
            "last_contact": "2020-01-16T14:59:56.245Z",
            "bruin_client_info": {
                "client_id": bruin_client_id,
                "client_name": "METTEL/NEW YORK",
            },
        }
        devices_cached_info = [
            device_1_cached_info,
            device_2_cached_info,
        ]

        device_1_info = {
            "device_info": probe_1_info,
            "cached_info": device_1_cached_info,
        }
        device_2_info = {
            "device_info": probe_2_info,
            "cached_info": device_2_cached_info,
        }
        devices_info = [
            device_1_info,
            device_2_info,
        ]

        probes = [
            probe_1_info,
            probe_2_info,
        ]
        probes_response = {
            "body": probes,
            "status": 200,
        }

        ticket_id = 12345
        create_ticket_response = {
            "body": ticket_id,
            "status": 473,
        }

        triage_note = "This is a triage note"

        outage_monitor_instance._bruin_repository.create_outage_ticket = AsyncMock(return_value=create_ticket_response)
        outage_monitor_instance._bruin_repository.append_triage_note_to_ticket = AsyncMock()
        outage_monitor_instance._bruin_repository.append_note_to_ticket = AsyncMock()

        outage_monitor_instance._hawkeye_repository.get_probes = AsyncMock(return_value=probes_response)

        outage_monitor_instance._notifications_repository.send_slack_message = AsyncMock()

        outage_monitor_instance._map_probes_info_with_customer_cache = Mock(return_value=devices_info)
        outage_monitor_instance._build_triage_note = Mock(return_value=triage_note)
        outage_monitor_instance._run_ticket_autoresolve = AsyncMock()
        outage_monitor_instance._reopen_outage_ticket = AsyncMock()

        with patch.object(outage_monitor_instance._config, "CURRENT_ENVIRONMENT", "production"):
            await outage_monitor_instance._recheck_devices_for_ticket_creation(devices_info)

        outage_monitor_instance._hawkeye_repository.get_probes.assert_awaited_once()
        outage_monitor_instance._map_probes_info_with_customer_cache.assert_called_once_with(
            probes, devices_cached_info
        )
        outage_monitor_instance._bruin_repository.create_outage_ticket.assert_has_awaits(
            [
                call(bruin_client_id, serial_number_1),
                call(bruin_client_id, serial_number_2),
            ]
        )
        outage_monitor_instance._build_triage_note.assert_has_calls(
            [
                call(probe_1_info),
                call(probe_2_info),
            ]
        )
        outage_monitor_instance._bruin_repository.append_triage_note_to_ticket.assert_has_awaits(
            [
                call(ticket_id, serial_number_1, triage_note),
                call(ticket_id, serial_number_2, triage_note),
            ]
        )
        outage_monitor_instance._reopen_outage_ticket.assert_not_awaited()
        outage_monitor_instance._run_ticket_autoresolve.assert_not_awaited()

    @pytest.mark.asyncio
    async def recheck_devices_with_just_devices_in_healthy_state_test(self, outage_monitor_instance):
        serial_number_1 = "B827EB76A8DE"
        serial_number_2 = "D827GD76C8FG"

        probe_1_info = {
            "probeId": "1",
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
            "serialNumber": serial_number_1,
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
            "nodetonode": {"status": 0, "lastUpdate": "2020-11-11T13:00:11Z"},
            "realservice": {"status": 1, "lastUpdate": "2020-10-15T02:18:28Z"},
        }
        probe_2_info = {
            "probeId": "3",
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
            "serialNumber": serial_number_2,
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
            "nodetonode": {"status": 0, "lastUpdate": "2020-11-11T13:00:11Z"},
            "realservice": {"status": 1, "lastUpdate": "2020-10-15T02:18:28Z"},
        }

        fresh_probe_1_info = {
            "probeId": "1",
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
            "serialNumber": serial_number_1,
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
            "nodetonode": {"status": 1, "lastUpdate": "2020-11-11T13:00:11Z"},
            "realservice": {"status": 1, "lastUpdate": "2020-10-15T02:18:28Z"},
        }
        fresh_probe_2_info = {
            "probeId": "3",
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
            "serialNumber": serial_number_2,
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
            "nodetonode": {"status": 1, "lastUpdate": "2020-11-11T13:00:11Z"},
            "realservice": {"status": 1, "lastUpdate": "2020-10-15T02:18:28Z"},
        }

        bruin_client_id = 9994
        device_1_cached_info = {
            "serial_number": serial_number_1,
            "last_contact": "2020-01-16T14:59:56.245Z",
            "bruin_client_info": {
                "client_id": bruin_client_id,
                "client_name": "METTEL/NEW YORK",
            },
        }
        device_2_cached_info = {
            "serial_number": serial_number_2,
            "last_contact": "2020-01-16T14:59:56.245Z",
            "bruin_client_info": {
                "client_id": bruin_client_id,
                "client_name": "METTEL/NEW YORK",
            },
        }
        devices_cached_info = [
            device_1_cached_info,
            device_2_cached_info,
        ]

        device_1_info = {
            "device_info": probe_1_info,
            "cached_info": device_1_cached_info,
        }
        device_2_info = {
            "device_info": probe_2_info,
            "cached_info": device_2_cached_info,
        }
        devices_info = [
            device_1_info,
            device_2_info,
        ]

        fresh_probes = [
            fresh_probe_1_info,
            fresh_probe_2_info,
        ]
        probes_response = {
            "body": fresh_probes,
            "status": 200,
        }

        fresh_device_1_info = {
            "device_info": fresh_probe_1_info,
            "cached_info": device_1_cached_info,
        }
        fresh_device_2_info = {
            "device_info": fresh_probe_2_info,
            "cached_info": device_2_cached_info,
        }
        fresh_devices_info = [
            fresh_device_1_info,
            fresh_device_2_info,
        ]

        outage_monitor_instance._bruin_repository.create_outage_ticket = AsyncMock()
        outage_monitor_instance._bruin_repository.append_triage_note_to_ticket = AsyncMock()

        outage_monitor_instance._hawkeye_repository.get_probes = AsyncMock(return_value=probes_response)

        outage_monitor_instance._notifications_repository.send_slack_message = AsyncMock()

        outage_monitor_instance._map_probes_info_with_customer_cache = Mock(return_value=fresh_devices_info)
        outage_monitor_instance._build_triage_note = Mock()
        outage_monitor_instance._run_ticket_autoresolve = AsyncMock()

        with patch.object(outage_monitor_instance._config, "CURRENT_ENVIRONMENT", "production"):
            await outage_monitor_instance._recheck_devices_for_ticket_creation(devices_info)

        outage_monitor_instance._hawkeye_repository.get_probes.assert_awaited_once()
        outage_monitor_instance._map_probes_info_with_customer_cache.assert_called_once_with(
            fresh_probes, devices_cached_info
        )
        outage_monitor_instance._bruin_repository.create_outage_ticket.assert_not_awaited()
        outage_monitor_instance._build_triage_note.assert_not_called()
        outage_monitor_instance._bruin_repository.append_triage_note_to_ticket.assert_not_awaited()
        outage_monitor_instance._run_ticket_autoresolve.assert_has_awaits(
            [
                call(fresh_device_1_info),
                call(fresh_device_2_info),
            ],
            any_order=True,
        )

    @pytest.mark.asyncio
    async def recheck_devices_with_get_probes_response_having_non_2xx_status_test(self, outage_monitor_instance):
        serial_number_1 = "B827EB76A8DE"
        serial_number_2 = "D827GD76C8FG"

        probe_1_info = {
            "probeId": "1",
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
            "serialNumber": serial_number_1,
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
            "nodetonode": {"status": 1, "lastUpdate": "2020-11-11T13:00:11Z"},
            "realservice": {"status": 1, "lastUpdate": "2020-10-15T02:18:28Z"},
        }
        probe_2_info = {
            "probeId": "3",
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
            "serialNumber": serial_number_2,
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
            "nodetonode": {"status": 0, "lastUpdate": "2020-11-11T13:00:11Z"},
            "realservice": {"status": 1, "lastUpdate": "2020-10-15T02:18:28Z"},
        }

        bruin_client_id = 9994
        device_1_cached_info = {
            "serial_number": serial_number_1,
            "last_contact": "2020-01-16T14:59:56.245Z",
            "bruin_client_info": {
                "client_id": bruin_client_id,
                "client_name": "METTEL/NEW YORK",
            },
        }
        device_2_cached_info = {
            "serial_number": serial_number_2,
            "last_contact": "2020-01-16T14:59:56.245Z",
            "bruin_client_info": {
                "client_id": bruin_client_id,
                "client_name": "METTEL/NEW YORK",
            },
        }

        device_1_info = {
            "device_info": probe_1_info,
            "cached_info": device_1_cached_info,
        }
        device_2_info = {
            "device_info": probe_2_info,
            "cached_info": device_2_cached_info,
        }
        devices_info = [
            device_1_info,
            device_2_info,
        ]

        probes_response = {
            "body": "Got internal error from Hawkeye",
            "status": 500,
        }

        outage_monitor_instance._bruin_repository.create_outage_ticket = AsyncMock()
        outage_monitor_instance._bruin_repository.append_triage_note_to_ticket = AsyncMock()

        outage_monitor_instance._hawkeye_repository.get_probes = AsyncMock(return_value=probes_response)

        outage_monitor_instance._notifications_repository.send_slack_message = AsyncMock()

        outage_monitor_instance._map_probes_info_with_customer_cache = Mock()
        outage_monitor_instance._build_triage_note = Mock()

        await outage_monitor_instance._recheck_devices_for_ticket_creation(devices_info)

        outage_monitor_instance._hawkeye_repository.get_probes.assert_awaited_once()
        outage_monitor_instance._map_probes_info_with_customer_cache.assert_not_called()
        outage_monitor_instance._bruin_repository.create_outage_ticket.assert_not_awaited()
        outage_monitor_instance._build_triage_note.assert_not_called()
        outage_monitor_instance._bruin_repository.append_triage_note_to_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def recheck_devices_with_empty_list_of_probes_test(self, outage_monitor_instance):
        serial_number_1 = "B827EB76A8DE"
        serial_number_2 = "D827GD76C8FG"

        probe_1_info = {
            "probeId": "1",
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
            "serialNumber": serial_number_1,
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
            "nodetonode": {"status": 1, "lastUpdate": "2020-11-11T13:00:11Z"},
            "realservice": {"status": 1, "lastUpdate": "2020-10-15T02:18:28Z"},
        }
        probe_2_info = {
            "probeId": "3",
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
            "serialNumber": serial_number_2,
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
            "nodetonode": {"status": 0, "lastUpdate": "2020-11-11T13:00:11Z"},
            "realservice": {"status": 1, "lastUpdate": "2020-10-15T02:18:28Z"},
        }

        bruin_client_id = 9994
        device_1_cached_info = {
            "serial_number": serial_number_1,
            "last_contact": "2020-01-16T14:59:56.245Z",
            "bruin_client_info": {
                "client_id": bruin_client_id,
                "client_name": "METTEL/NEW YORK",
            },
        }
        device_2_cached_info = {
            "serial_number": serial_number_2,
            "last_contact": "2020-01-16T14:59:56.245Z",
            "bruin_client_info": {
                "client_id": bruin_client_id,
                "client_name": "METTEL/NEW YORK",
            },
        }

        device_1_info = {
            "device_info": probe_1_info,
            "cached_info": device_1_cached_info,
        }
        device_2_info = {
            "device_info": probe_2_info,
            "cached_info": device_2_cached_info,
        }
        devices_info = [
            device_1_info,
            device_2_info,
        ]

        probes_response = {
            "body": [],
            "status": 200,
        }

        outage_monitor_instance._bruin_repository.create_outage_ticket = AsyncMock()
        outage_monitor_instance._bruin_repository.append_triage_note_to_ticket = AsyncMock()

        outage_monitor_instance._hawkeye_repository.get_probes = AsyncMock(return_value=probes_response)

        outage_monitor_instance._notifications_repository.send_slack_message = AsyncMock()

        outage_monitor_instance._map_probes_info_with_customer_cache = Mock()
        outage_monitor_instance._build_triage_note = Mock()

        await outage_monitor_instance._recheck_devices_for_ticket_creation(devices_info)

        outage_monitor_instance._hawkeye_repository.get_probes.assert_awaited_once()
        outage_monitor_instance._map_probes_info_with_customer_cache.assert_not_called()
        outage_monitor_instance._bruin_repository.create_outage_ticket.assert_not_awaited()
        outage_monitor_instance._build_triage_note.assert_not_called()
        outage_monitor_instance._bruin_repository.append_triage_note_to_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def recheck_devices_with_no_active_probes_test(self, outage_monitor_instance):
        serial_number_1 = "B827EB76A8DE"
        serial_number_2 = "D827GD76C8FG"

        probe_1_info = {
            "probeId": "1",
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
            "serialNumber": serial_number_1,
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
            "nodetonode": {"status": 1, "lastUpdate": "2020-11-11T13:00:11Z"},
            "realservice": {"status": 1, "lastUpdate": "2020-10-15T02:18:28Z"},
        }
        probe_2_info = {
            "probeId": "3",
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
            "serialNumber": serial_number_2,
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
            "nodetonode": {"status": 0, "lastUpdate": "2020-11-11T13:00:11Z"},
            "realservice": {"status": 1, "lastUpdate": "2020-10-15T02:18:28Z"},
        }

        bruin_client_id = 9994
        device_1_cached_info = {
            "serial_number": serial_number_1,
            "last_contact": "2020-01-16T14:59:56.245Z",
            "bruin_client_info": {
                "client_id": bruin_client_id,
                "client_name": "METTEL/NEW YORK",
            },
        }
        device_2_cached_info = {
            "serial_number": serial_number_2,
            "last_contact": "2020-01-16T14:59:56.245Z",
            "bruin_client_info": {
                "client_id": bruin_client_id,
                "client_name": "METTEL/NEW YORK",
            },
        }

        device_1_info = {
            "device_info": probe_1_info,
            "cached_info": device_1_cached_info,
        }
        device_2_info = {
            "device_info": probe_2_info,
            "cached_info": device_2_cached_info,
        }
        devices_info = [
            device_1_info,
            device_2_info,
        ]

        probes = [
            {
                "probeId": "1",
                "uid": "b8:27:eb:76:a8:de",
                "os": "Linux ARM",
                "name": "FIS_Demo_XrPi",
                "testIp": "none",
                "managementIp": "none",
                "active": "0",
                "type": "8",
                "mode": "Automatic",
                "n2nMode": "1",
                "rsMode": "1",
                "typeName": "xr_pi",
                "serialNumber": serial_number_1,
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
                "nodetonode": {"status": 1, "lastUpdate": "2020-11-11T13:00:11Z"},
                "realservice": {"status": 1, "lastUpdate": "2020-10-15T02:18:28Z"},
            }
        ]
        probes_response = {
            "body": probes,
            "status": 200,
        }

        outage_monitor_instance._bruin_repository.create_outage_ticket = AsyncMock()
        outage_monitor_instance._bruin_repository.append_triage_note_to_ticket = AsyncMock()

        outage_monitor_instance._hawkeye_repository.get_probes = AsyncMock(return_value=probes_response)

        outage_monitor_instance._notifications_repository.send_slack_message = AsyncMock()

        outage_monitor_instance._map_probes_info_with_customer_cache = Mock()
        outage_monitor_instance._build_triage_note = Mock()

        await outage_monitor_instance._recheck_devices_for_ticket_creation(devices_info)

        outage_monitor_instance._hawkeye_repository.get_probes.assert_awaited_once()
        outage_monitor_instance._map_probes_info_with_customer_cache.assert_not_called()
        outage_monitor_instance._bruin_repository.create_outage_ticket.assert_not_awaited()
        outage_monitor_instance._build_triage_note.assert_not_called()
        outage_monitor_instance._bruin_repository.append_triage_note_to_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def recheck_devices_with_environment_other_than_production_test(self, outage_monitor_instance):
        serial_number_1 = "B827EB76A8DE"
        serial_number_2 = "D827GD76C8FG"

        probe_1_info = {
            "probeId": "1",
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
            "serialNumber": serial_number_1,
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
            "nodetonode": {"status": 1, "lastUpdate": "2020-11-11T13:00:11Z"},
            "realservice": {"status": 1, "lastUpdate": "2020-10-15T02:18:28Z"},
        }
        probe_2_info = {
            "probeId": "3",
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
            "serialNumber": serial_number_2,
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
            "nodetonode": {"status": 0, "lastUpdate": "2020-11-11T13:00:11Z"},
            "realservice": {"status": 1, "lastUpdate": "2020-10-15T02:18:28Z"},
        }

        bruin_client_id = 9994
        device_1_cached_info = {
            "serial_number": serial_number_1,
            "last_contact": "2020-01-16T14:59:56.245Z",
            "bruin_client_info": {
                "client_id": bruin_client_id,
                "client_name": "METTEL/NEW YORK",
            },
        }
        device_2_cached_info = {
            "serial_number": serial_number_2,
            "last_contact": "2020-01-16T14:59:56.245Z",
            "bruin_client_info": {
                "client_id": bruin_client_id,
                "client_name": "METTEL/NEW YORK",
            },
        }
        devices_cached_info = [
            device_1_cached_info,
            device_2_cached_info,
        ]

        device_1_info = {
            "device_info": probe_1_info,
            "cached_info": device_1_cached_info,
        }
        device_2_info = {
            "device_info": probe_2_info,
            "cached_info": device_2_cached_info,
        }
        devices_info = [
            device_1_info,
            device_2_info,
        ]

        probes = [
            probe_1_info,
            probe_2_info,
        ]
        probes_response = {
            "body": probes,
            "status": 200,
        }

        ticket_id = 12345
        create_ticket_response = {
            "body": ticket_id,
            "status": 200,
        }

        triage_note = "This is Hawkeye's triage note"

        outage_monitor_instance._bruin_repository.create_outage_ticket = AsyncMock(return_value=create_ticket_response)
        outage_monitor_instance._bruin_repository.append_triage_note_to_ticket = AsyncMock()

        outage_monitor_instance._hawkeye_repository.get_probes = AsyncMock(return_value=probes_response)

        outage_monitor_instance._notifications_repository.send_slack_message = AsyncMock()

        outage_monitor_instance._map_probes_info_with_customer_cache = Mock(return_value=devices_info)
        outage_monitor_instance._build_triage_note = Mock(return_value=triage_note)

        with patch.object(outage_monitor_instance._config, "CURRENT_ENVIRONMENT", "dev"):
            await outage_monitor_instance._recheck_devices_for_ticket_creation(devices_info)

        outage_monitor_instance._hawkeye_repository.get_probes.assert_awaited_once()
        outage_monitor_instance._map_probes_info_with_customer_cache.assert_called_once_with(
            probes, devices_cached_info
        )
        outage_monitor_instance._bruin_repository.create_outage_ticket.assert_not_awaited()
        outage_monitor_instance._build_triage_note.assert_not_called()
        outage_monitor_instance._bruin_repository.append_triage_note_to_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def reopen_outage_ticket_test(
        self, probes_response, outage_monitor_instance, devices_info, ticket_response_reopen, bruin_response_ok
    ):
        outage_monitor_instance._bruin_repository.create_outage_ticket = AsyncMock(return_value=ticket_response_reopen)
        outage_monitor_instance._bruin_repository.append_note_to_ticket = AsyncMock()
        outage_monitor_instance._bruin_repository.get_ticket_details = AsyncMock(return_value=bruin_response_ok)
        outage_monitor_instance._bruin_repository.open_ticket = AsyncMock(return_value={"status": 200, "body": None})

        outage_monitor_instance._hawkeye_repository.get_probes = AsyncMock(return_value=probes_response)

        outage_monitor_instance._notifications_repository.send_slack_message = AsyncMock()

        outage_monitor_instance._map_probes_info_with_customer_cache = Mock(return_value=devices_info)
        with patch.object(outage_monitor_instance._config, "CURRENT_ENVIRONMENT", "production"):
            await outage_monitor_instance._recheck_devices_for_ticket_creation(devices_info)

        outage_monitor_instance._hawkeye_repository.get_probes.assert_awaited_once()
        outage_monitor_instance._map_probes_info_with_customer_cache.assert_called()
        outage_monitor_instance._bruin_repository.create_outage_ticket.assert_awaited()

    @pytest.mark.asyncio
    async def reopen_outage_ticket_bad_get_ticket_detail_test(
        self, device_1_info, ticket_id, bruin_exception_response, outage_monitor_instance
    ):
        outage_monitor_instance._bruin_repository.get_ticket_details = AsyncMock(return_value=bruin_exception_response)
        outage_monitor_instance._bruin_repository.open_ticket = AsyncMock()

        outage_monitor_instance._notifications_repository.send_slack_message = AsyncMock()

        await outage_monitor_instance._reopen_outage_ticket(ticket_id, device_1_info)

        outage_monitor_instance._bruin_repository.get_ticket_details.assert_awaited_once_with(ticket_id)
        outage_monitor_instance._bruin_repository.open_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def reopen_outage_ticket_with_reopen_request_having_non_2xx_status_test(
        self,
        device_1_info,
        ticket_id,
        ticket_detail_for_serial_1,
        bruin_response_ok,
        bruin_exception_response,
        outage_monitor_instance,
    ):
        ticket_detail_for_serial_1_id = ticket_detail_for_serial_1["detailID"]

        outage_monitor_instance._bruin_repository.get_ticket_details = AsyncMock(return_value=bruin_response_ok)
        outage_monitor_instance._bruin_repository.open_ticket = AsyncMock(return_value=bruin_exception_response)
        outage_monitor_instance._bruin_repository.append_note_to_ticket = AsyncMock()

        await outage_monitor_instance._reopen_outage_ticket(ticket_id, device_1_info)

        outage_monitor_instance._bruin_repository.get_ticket_details.assert_awaited_once_with(ticket_id)
        outage_monitor_instance._bruin_repository.open_ticket.assert_awaited_once_with(
            ticket_id, ticket_detail_for_serial_1_id
        )
        outage_monitor_instance._bruin_repository.append_note_to_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def reopen_outage_ticket_ok_test(
        self,
        device_1_info,
        ticket_id,
        ticket_detail_for_serial_1,
        bruin_response_ok,
        bruin_reopen_response_ok,
        outage_monitor_instance,
    ):
        ticket_detail_for_serial_1_id = ticket_detail_for_serial_1["detailID"]
        serial_number = ticket_detail_for_serial_1["detailValue"]
        reopen_note = "#*MetTel's IPA*#\nRe-opening task"

        outage_monitor_instance._bruin_repository.get_ticket_details = AsyncMock(return_value=bruin_response_ok)
        outage_monitor_instance._bruin_repository.open_ticket = AsyncMock(return_value=bruin_reopen_response_ok)
        outage_monitor_instance._build_triage_note = Mock(return_value=reopen_note)
        outage_monitor_instance._bruin_repository.append_note_to_ticket = AsyncMock()
        outage_monitor_instance._notifications_repository.send_slack_message = AsyncMock()

        await outage_monitor_instance._reopen_outage_ticket(ticket_id, device_1_info)

        outage_monitor_instance._bruin_repository.get_ticket_details.assert_awaited_once_with(ticket_id)
        outage_monitor_instance._bruin_repository.open_ticket.assert_awaited_once_with(
            ticket_id, ticket_detail_for_serial_1_id
        )
        outage_monitor_instance._build_triage_note.assert_called_once_with(
            device_1_info["device_info"], is_reopen_note=True
        )
        outage_monitor_instance._bruin_repository.append_note_to_ticket.assert_awaited_once_with(
            ticket_id, reopen_note, service_numbers=[serial_number]
        )
        outage_monitor_instance._notifications_repository.send_slack_message.assert_awaited()

    def build_reopen_note_test(self, device_1_info, outage_monitor_instance):
        device_info = device_1_info["device_info"]
        tz_object = timezone(outage_monitor_instance._config.TIMEZONE)
        current_datetime = datetime.now(utc).astimezone(tz_object)
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)
        node_last_update = str(parse(device_info["nodetonode"]["lastUpdate"]).astimezone(tz_object))
        service_last_update = str(parse(device_info["realservice"]["lastUpdate"]).astimezone(tz_object))
        expected = os.linesep.join(
            [
                "#*MetTel's IPA*#",
                f"Re-opening task",
                "",
                "Hawkeye Instance: https://ixia.metconnect.net/",
                "Links: [Dashboard|https://ixia.metconnect.net/ixrr_main.php?type=ProbesManagement] - "
                f"[Probe|https://ixia.metconnect.net/probeinformation.php?probeid={device_info['probeId']}]",
                f"Device Name: {device_info['name']}",
                f"Device Type: {device_info['typeName']}",
                f"Device Group(s): {device_info['probeGroup']}",
                f"Serial: {device_info['serialNumber']}",
                f"Hawkeye ID: {device_info['probeId']}",
                "",
                f"Device Node to Node Status: UP",
                f"Node to Node Last Update: {node_last_update}",
                f"Device Real Service Status: DOWN",
                f"Real Service Last Update: {service_last_update}",
                "",
                f"TimeStamp: {str(current_datetime)}",
            ]
        )

        with patch.object(outage_monitoring_module, "datetime", new=datetime_mock):
            result = outage_monitor_instance._build_triage_note(device_1_info["device_info"], is_reopen_note=True)

            assert result == expected

    @pytest.mark.asyncio
    async def append_triage_note_if_needed_with_ticket_details_response_having_non_2xx_status_test(
        self, outage_monitor_instance
    ):
        ticket_id = 12345

        serial_number = "B827EB92EB72"
        device_info = {
            "probeId": "1",
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
            "serialNumber": serial_number,
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
            "nodetonode": {"status": 1, "lastUpdate": "2020-11-11T13:00:11Z"},
            "realservice": {"status": 1, "lastUpdate": "2020-10-15T02:18:28Z"},
        }

        ticket_details_response = {
            "body": "Got internal error from Bruin",
            "status": 500,
        }

        outage_monitor_instance._bruin_repository.get_ticket_details = AsyncMock(return_value=ticket_details_response)
        outage_monitor_instance._bruin_repository.append_triage_note_to_ticket = AsyncMock()

        outage_monitor_instance._build_triage_note = Mock()
        outage_monitor_instance._get_triage_note = Mock()

        await outage_monitor_instance._append_triage_note_if_needed(ticket_id, device_info)

        outage_monitor_instance._bruin_repository.get_ticket_details.assert_awaited_once_with(ticket_id)
        outage_monitor_instance._get_triage_note.assert_not_called()
        outage_monitor_instance._build_triage_note.assert_not_called()
        outage_monitor_instance._bruin_repository.append_triage_note_to_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def append_triage_note_if_needed_with_triage_note_found_in_ticket_test(self, outage_monitor_instance):
        ticket_id = 12345

        serial_number = "B827EB92EB72"
        device_info = {
            "probeId": "1",
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
            "serialNumber": serial_number,
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
            "nodetonode": {"status": 1, "lastUpdate": "2020-11-11T13:00:11Z"},
            "realservice": {"status": 1, "lastUpdate": "2020-10-15T02:18:28Z"},
        }

        ticket_detail_1 = {
            "detailID": 12345,
            "detailValue": serial_number,
        }

        ticket_notes = [
            {
                "noteId": 41894041,
                "noteValue": f"#*MetTel's IPA*#\nTriage (Ixia)\nTimeStamp: 2020-02-24 10:07:12+00:00",
                "createdDate": "2020-02-24T10:07:13.503-05:00",
                "serviceNumber": [
                    serial_number,
                ],
            },
        ]
        ticket_details_response = {
            "body": {
                "ticketDetails": [
                    ticket_detail_1,
                ],
                "ticketNotes": ticket_notes,
            },
            "status": 200,
        }

        outage_monitor_instance._bruin_repository.get_ticket_details = AsyncMock(return_value=ticket_details_response)
        outage_monitor_instance._bruin_repository.append_triage_note_to_ticket = AsyncMock()

        outage_monitor_instance._build_triage_note = Mock()
        outage_monitor_instance._get_triage_note = Mock(return_value={"noteValue": "Some irrelevant note"})

        await outage_monitor_instance._append_triage_note_if_needed(ticket_id, device_info)

        outage_monitor_instance._bruin_repository.get_ticket_details.assert_awaited_once_with(ticket_id)
        outage_monitor_instance._get_triage_note.assert_called_once_with(ticket_notes)
        outage_monitor_instance._build_triage_note.assert_not_called()
        outage_monitor_instance._bruin_repository.append_triage_note_to_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def append_triage_note_if_needed_with_triage_note_not_found_in_ticket_test(self, outage_monitor_instance):
        ticket_id = 12345

        serial_number = "B827EB92EB72"
        device_info = {
            "probeId": "1",
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
            "serialNumber": serial_number,
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
            "nodetonode": {"status": 1, "lastUpdate": "2020-11-11T13:00:11Z"},
            "realservice": {"status": 1, "lastUpdate": "2020-10-15T02:18:28Z"},
        }

        ticket_detail_1 = {
            "detailID": 12345,
            "detailValue": serial_number,
        }

        ticket_notes = []
        ticket_details_response = {
            "body": {
                "ticketDetails": [
                    ticket_detail_1,
                ],
                "ticketNotes": ticket_notes,
            },
            "status": 200,
        }

        triage_note = "This is a triage note"

        outage_monitor_instance._bruin_repository.get_ticket_details = AsyncMock(return_value=ticket_details_response)
        outage_monitor_instance._bruin_repository.append_triage_note_to_ticket = AsyncMock()

        outage_monitor_instance._build_triage_note = Mock(return_value=triage_note)
        outage_monitor_instance._get_triage_note = Mock(return_value=None)

        await outage_monitor_instance._append_triage_note_if_needed(ticket_id, device_info)

        outage_monitor_instance._bruin_repository.get_ticket_details.assert_awaited_once_with(ticket_id)
        outage_monitor_instance._get_triage_note.assert_called_once_with(ticket_notes)
        outage_monitor_instance._build_triage_note.assert_called_once_with(device_info)
        outage_monitor_instance._bruin_repository.append_triage_note_to_ticket.assert_awaited_once_with(
            ticket_id, serial_number, triage_note
        )

    def get_triage_note_test(self, outage_monitor_instance):

        ticket_notes = []
        triage_note = outage_monitor_instance._get_triage_note(ticket_notes)
        assert triage_note is None

        ticket_notes = [
            {
                "noteId": 41894041,
                "noteValue": f"#*MetTel's IPA*#\nAI\nTimeStamp: 2020-02-24 10:07:12+00:00",
                "createdDate": "2020-02-24T10:07:13.503-05:00",
                "serviceNumber": [
                    "B827EB92EB72",
                ],
            },
        ]
        triage_note = outage_monitor_instance._get_triage_note(ticket_notes)
        assert triage_note is None

        ticket_notes = [
            {
                "noteId": 41894041,
                "noteValue": f"#*Automation Engine*#\nTriage (Ixia)\nTimeStamp: 2020-02-24 10:07:12+00:00",
                "createdDate": "2020-02-24T10:07:13.503-05:00",
                "serviceNumber": [
                    "B827EB92EB72",
                ],
            },
        ]
        triage_note = outage_monitor_instance._get_triage_note(ticket_notes)
        assert triage_note is ticket_notes[0]

        ticket_notes = [
            {
                "noteId": 41894041,
                "noteValue": f"#*MetTel's IPA*#\nTriage (Ixia)\nTimeStamp: 2020-02-24 10:07:12+00:00",
                "createdDate": "2020-02-24T10:07:13.503-05:00",
                "serviceNumber": [
                    "B827EB92EB72",
                ],
            },
        ]
        triage_note = outage_monitor_instance._get_triage_note(ticket_notes)
        assert triage_note is ticket_notes[0]

    def build_triage_note_test(self, outage_monitor_instance):
        device_info = {
            "probeId": "1",
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
            "nodetonode": {"status": 0, "lastUpdate": "never"},
            "realservice": {"status": 1, "lastUpdate": "2020-11-15T10:18:28Z"},
        }

        current_datetime = datetime.now(utc)
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)
        with patch.object(outage_monitoring_module, "datetime", new=datetime_mock):
            triage_note = outage_monitor_instance._build_triage_note(device_info)

        expected_note = os.linesep.join(
            [
                "#*MetTel's IPA*#",
                "Triage (Ixia)",
                "",
                "Hawkeye Instance: https://ixia.metconnect.net/",
                "Links: [Dashboard|https://ixia.metconnect.net/ixrr_main.php?type=ProbesManagement] - "
                "[Probe|https://ixia.metconnect.net/probeinformation.php?probeid=1]",
                "Device Name: FIS_Demo_XrPi",
                "Device Type: xr_pi",
                "Device Group(s): FIS",
                "Serial: B827EB76A8DE",
                "Hawkeye ID: 1",
                "",
                "Device Node to Node Status: DOWN",
                "Node to Node Last Update: never",
                "Device Real Service Status: UP",
                "Real Service Last Update: 2020-11-15 05:18:28-05:00",
                "",
                f"TimeStamp: {str(current_datetime.astimezone(timezone(outage_monitor_instance._config.TIMEZONE)))}",
            ]
        )
        assert triage_note == expected_note

    @pytest.mark.asyncio
    async def run_ticket_autoresolve_with_retrieval_of_ticket_returning_non_2xx_status_test(
        self, outage_monitor_instance
    ):
        serial_number = "B827EB92EB72"
        client_id = 9994

        device = {
            "cached_info": {
                "serial_number": serial_number,
                "last_contact": "2020-01-16T14:59:56.245Z",
                "bruin_client_info": {
                    "client_id": 9994,
                    "client_name": "METTEL/NEW YORK",
                },
            },
            "device_info": {
                "probeId": "1",
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
                "nodetonode": {"status": 1, "lastUpdate": "2020-11-11T13:00:11Z"},
                "realservice": {"status": 1, "lastUpdate": "2020-10-15T02:18:28Z"},
            },
        }

        outage_ticket_response = {
            "body": "Invalid parameters",
            "status": 400,
        }

        outage_monitor_instance._bruin_repository.get_open_outage_tickets = AsyncMock(
            return_value=outage_ticket_response
        )
        outage_monitor_instance._bruin_repository.get_ticket_details = AsyncMock()

        await outage_monitor_instance._run_ticket_autoresolve(device)

        outage_monitor_instance._bruin_repository.get_open_outage_tickets.assert_awaited_once_with(
            client_id, service_number=serial_number
        )
        outage_monitor_instance._bruin_repository.get_ticket_details.assert_not_awaited()

    @pytest.mark.asyncio
    async def run_ticket_autoresolve_with_no_open_outage_ticket_found_test(self, outage_monitor_instance):
        serial_number = "B827EB92EB72"
        client_id = 9994

        device = {
            "cached_info": {
                "serial_number": serial_number,
                "last_contact": "2020-01-16T14:59:56.245Z",
                "bruin_client_info": {
                    "client_id": 9994,
                    "client_name": "METTEL/NEW YORK",
                },
            },
            "device_info": {
                "probeId": "1",
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
                "nodetonode": {"status": 1, "lastUpdate": "2020-11-11T13:00:11Z"},
                "realservice": {"status": 1, "lastUpdate": "2020-10-15T02:18:28Z"},
            },
        }

        outage_ticket_response = {
            "body": [],
            "status": 200,
        }

        outage_monitor_instance._bruin_repository.get_open_outage_tickets = AsyncMock(
            return_value=outage_ticket_response
        )
        outage_monitor_instance._bruin_repository.get_ticket_details = AsyncMock()

        await outage_monitor_instance._run_ticket_autoresolve(device)

        outage_monitor_instance._bruin_repository.get_open_outage_tickets.assert_awaited_once_with(
            client_id, service_number=serial_number
        )
        outage_monitor_instance._bruin_repository.get_ticket_details.assert_not_awaited()

    @pytest.mark.asyncio
    async def run_ticket_autoresolve_with_ticket_not_created_by_automation_engine_test(self, outage_monitor_instance):
        serial_number = "B827EB92EB72"
        client_id = 9994

        device = {
            "cached_info": {
                "serial_number": serial_number,
                "last_contact": "2020-01-16T14:59:56.245Z",
                "bruin_client_info": {
                    "client_id": client_id,
                    "client_name": "METTEL/NEW YORK",
                },
            },
            "device_info": {
                "probeId": "1",
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
                "nodetonode": {"status": 1, "lastUpdate": "2020-11-11T13:00:11Z"},
                "realservice": {"status": 1, "lastUpdate": "2020-10-15T02:18:28Z"},
            },
        }

        ticket_id = 99999
        ticket = {
            "clientID": client_id,
            "clientName": "Aperture Science",
            "ticketID": ticket_id,
            "category": "Network Scout",
            "topic": "Service Outage Trouble",
            "ticketStatus": "New",
            "createDate": "9/25/2020 6:31:54 AM",
            "createdBy": "InterMapper Service",
        }
        outage_ticket_response = {
            "body": [ticket],
            "status": 200,
        }

        outage_monitor_instance._bruin_repository.get_open_outage_tickets = AsyncMock(
            return_value=outage_ticket_response
        )
        outage_monitor_instance._bruin_repository.get_ticket_details = AsyncMock()

        outage_monitor_instance._was_ticket_created_by_automation_engine = Mock(return_value=False)

        await outage_monitor_instance._run_ticket_autoresolve(device)

        outage_monitor_instance._bruin_repository.get_open_outage_tickets.assert_awaited_once_with(
            client_id, service_number=serial_number
        )
        outage_monitor_instance._was_ticket_created_by_automation_engine.assert_called_once_with(ticket)
        outage_monitor_instance._bruin_repository.get_ticket_details.assert_not_awaited()

    @pytest.mark.asyncio
    async def run_ticket_autoresolve_with_retrieval_of_ticket_details_returning_non_2xx_status_test(
        self, outage_monitor_instance
    ):
        serial_number = "B827EB92EB72"
        client_id = 9994

        device = {
            "cached_info": {
                "serial_number": serial_number,
                "last_contact": "2020-01-16T14:59:56.245Z",
                "bruin_client_info": {
                    "client_id": client_id,
                    "client_name": "METTEL/NEW YORK",
                },
            },
            "device_info": {
                "probeId": "1",
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
                "nodetonode": {"status": 1, "lastUpdate": "2020-11-11T13:00:11Z"},
                "realservice": {"status": 1, "lastUpdate": "2020-10-15T02:18:28Z"},
            },
        }

        ticket_id = 99999
        ticket = {
            "clientID": client_id,
            "clientName": "Aperture Science",
            "ticketID": ticket_id,
            "category": "Network Scout",
            "topic": "Service Outage Trouble",
            "ticketStatus": "New",
            "createDate": "9/25/2020 6:31:54 AM",
            "createdBy": "Intelygenz Ai",
        }
        outage_ticket_response = {
            "body": [ticket],
            "status": 200,
        }

        ticket_details_response = {
            "body": "Got internal error from Bruin",
            "status": 500,
        }

        outage_monitor_instance._bruin_repository.get_open_outage_tickets = AsyncMock(
            return_value=outage_ticket_response
        )
        outage_monitor_instance._bruin_repository.get_ticket_details = AsyncMock(return_value=ticket_details_response)

        outage_monitor_instance._was_ticket_created_by_automation_engine = Mock(return_value=True)
        outage_monitor_instance._was_last_outage_detected_recently = Mock()

        await outage_monitor_instance._run_ticket_autoresolve(device)

        outage_monitor_instance._bruin_repository.get_open_outage_tickets.assert_awaited_once_with(
            client_id, service_number=serial_number
        )
        outage_monitor_instance._bruin_repository.get_ticket_details.assert_awaited_once_with(ticket_id)
        outage_monitor_instance._was_last_outage_detected_recently.assert_not_called()

    @pytest.mark.asyncio
    async def run_ticket_autoresolve_with_retrieval_of_ticket_details_returning_non_2xx_status_2_test(
        self, outage_monitor_instance
    ):
        serial_number = "B827EB92EB72"
        client_id = 9994

        device = {
            "cached_info": {
                "serial_number": serial_number,
                "last_contact": "2020-01-16T14:59:56.245Z",
                "bruin_client_info": {
                    "client_id": client_id,
                    "client_name": "METTEL/NEW YORK",
                },
            },
            "device_info": {
                "probeId": "1",
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
                "nodetonode": {"status": 1, "lastUpdate": "2020-11-11T13:00:11Z"},
                "realservice": {"status": 1, "lastUpdate": "2020-10-15T02:18:28Z"},
            },
        }

        ticket_id = 99999
        ticket = {
            "clientID": client_id,
            "clientName": "Aperture Science",
            "ticketID": ticket_id,
            "category": "Network Scout",
            "topic": "Service Outage Trouble",
            "ticketStatus": "New",
            "createDate": "9/25/2020 6:31:54 AM",
            "createdBy": "Intelygenz Ai",
        }
        outage_ticket_response = {
            "body": [ticket],
            "status": 200,
        }

        ticket_details_response = {
            "body": "Got internal error from Bruin",
            "status": 500,
        }

        outage_monitor_instance._bruin_repository.get_open_outage_tickets = AsyncMock(
            return_value=outage_ticket_response
        )
        outage_monitor_instance._bruin_repository.get_ticket_details = AsyncMock(return_value=ticket_details_response)

        outage_monitor_instance._was_ticket_created_by_automation_engine = Mock(return_value=True)
        outage_monitor_instance._was_last_outage_detected_recently = Mock()

        await outage_monitor_instance._run_ticket_autoresolve(device)

        outage_monitor_instance._bruin_repository.get_open_outage_tickets.assert_awaited_once_with(
            client_id, service_number=serial_number
        )
        outage_monitor_instance._bruin_repository.get_ticket_details.assert_awaited_once_with(ticket_id)
        outage_monitor_instance._was_last_outage_detected_recently.assert_not_called()

    @pytest.mark.asyncio
    async def run_ticket_autoresolve_with_last_outage_detected_long_ago_test(self, outage_monitor_instance):
        serial_number = "B827EB92EB72"
        client_id = 9994

        device = {
            "cached_info": {
                "serial_number": serial_number,
                "last_contact": "2020-01-16T14:59:56.245Z",
                "bruin_client_info": {
                    "client_id": client_id,
                    "client_name": "METTEL/NEW YORK",
                },
            },
            "device_info": {
                "probeId": "1",
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
                "nodetonode": {"status": 1, "lastUpdate": "2020-11-11T13:00:11Z"},
                "realservice": {"status": 1, "lastUpdate": "2020-10-15T02:18:28Z"},
            },
        }

        ticket_id = 99999
        ticket_creation_date = "9/25/2020 6:31:54 AM"
        ticket = {
            "clientID": client_id,
            "clientName": "Aperture Science",
            "ticketID": ticket_id,
            "category": "Network Scout",
            "topic": "Service Outage Trouble",
            "ticketStatus": "New",
            "createDate": ticket_creation_date,
            "createdBy": "Intelygenz Ai",
        }
        outage_ticket_response = {
            "body": [
                ticket,
            ],
            "status": 200,
        }

        ticket_detail_1_id = 2746937
        ticket_detail_1 = {
            "detailID": ticket_detail_1_id,
            "detailValue": serial_number,
            "detailStatus": "I",
        }

        ticket_detail_2_id = 999999
        ticket_detail_2 = {
            "detailID": ticket_detail_2_id,
            "detailValue": "VC9999999",
            "detailStatus": "I",
        }

        ticket_note_1 = {
            "noteId": 68246614,
            "noteValue": "#*MetTel's IPA*#\nTriage (Ixia).\nTimeStamp: 2021-01-02 10:18:16-05:00",
            "serviceNumber": [
                serial_number,
            ],
        }
        ticket_note_2 = {
            "noteId": 68246615,
            "noteValue": "Some irrelevant note",
            "serviceNumber": [
                "VC1234567",
            ],
        }
        ticket_note_3 = {
            "noteId": 68246616,
            "noteValue": "#*MetTel's IPA*#\nAuto-resolving detail.\nTimeStamp: 2021-01-03 10:18:16-05:00",
            "serviceNumber": [
                serial_number,
            ],
        }
        ticket_notes = [
            ticket_note_1,
            ticket_note_2,
            ticket_note_3,
        ]

        ticket_details_response = {
            "body": {
                "ticketDetails": [
                    ticket_detail_1,
                    ticket_detail_2,
                ],
                "ticketNotes": ticket_notes,
            },
            "status": 200,
        }

        relevant_notes = [
            ticket_note_1,
            ticket_note_3,
        ]

        outage_monitor_instance._bruin_repository.get_open_outage_tickets = AsyncMock(
            return_value=outage_ticket_response
        )
        outage_monitor_instance._bruin_repository.get_ticket_details = AsyncMock(return_value=ticket_details_response)

        outage_monitor_instance._was_ticket_created_by_automation_engine = Mock(return_value=True)
        outage_monitor_instance._was_last_outage_detected_recently = Mock(return_value=False)
        outage_monitor_instance.is_outage_ticket_auto_resolvable = Mock()

        await outage_monitor_instance._run_ticket_autoresolve(device)

        outage_monitor_instance._bruin_repository.get_open_outage_tickets.assert_awaited_once_with(
            client_id, service_number=serial_number
        )
        outage_monitor_instance._bruin_repository.get_ticket_details.assert_awaited_once_with(ticket_id)
        outage_monitor_instance._was_last_outage_detected_recently.assert_called_once_with(
            relevant_notes, ticket_creation_date
        )
        outage_monitor_instance.is_outage_ticket_auto_resolvable.assert_not_called()

    @pytest.mark.asyncio
    async def run_ticket_autoresolve_with_resolve_limit_exceeded_test(self, outage_monitor_instance):
        serial_number = "B827EB92EB72"
        client_id = 9994

        device = {
            "cached_info": {
                "serial_number": serial_number,
                "last_contact": "2020-01-16T14:59:56.245Z",
                "bruin_client_info": {
                    "client_id": client_id,
                    "client_name": "METTEL/NEW YORK",
                },
            },
            "device_info": {
                "probeId": "1",
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
                "nodetonode": {"status": 1, "lastUpdate": "2020-11-11T13:00:11Z"},
                "realservice": {"status": 1, "lastUpdate": "2020-10-15T02:18:28Z"},
            },
        }

        ticket_id = 99999
        ticket_creation_date = "9/25/2020 6:31:54 AM"
        ticket = {
            "clientID": client_id,
            "clientName": "Aperture Science",
            "ticketID": ticket_id,
            "category": "Network Scout",
            "topic": "Service Outage Trouble",
            "ticketStatus": "New",
            "createDate": ticket_creation_date,
            "createdBy": "Intelygenz Ai",
        }
        outage_ticket_response = {
            "body": [
                ticket,
            ],
            "status": 200,
        }

        ticket_detail_1_id = 2746937
        ticket_detail_1 = {
            "detailID": ticket_detail_1_id,
            "detailValue": serial_number,
            "detailStatus": "I",
        }

        ticket_detail_2_id = 999999
        ticket_detail_2 = {
            "detailID": ticket_detail_2_id,
            "detailValue": "VC9999999",
            "detailStatus": "I",
        }

        ticket_note_1 = {
            "noteId": 68246614,
            "noteValue": "#*MetTel's IPA*#\nTriage (Ixia).\nTimeStamp: 2021-01-02 10:18:16-05:00",
            "serviceNumber": [
                serial_number,
            ],
        }
        ticket_note_2 = {
            "noteId": 68246615,
            "noteValue": "Some irrelevant note",
            "serviceNumber": [
                "VC1234567",
            ],
        }
        ticket_note_3 = {
            "noteId": 68246616,
            "noteValue": "#*MetTel's IPA*#\nAuto-resolving detail.\nTimeStamp: 2021-01-03 10:18:16-05:00",
            "serviceNumber": [
                serial_number,
            ],
        }
        ticket_note_4 = {
            "noteId": 68246616,
            "noteValue": "#*MetTel's IPA*#\nAuto-resolving detail.\nTimeStamp: 2021-01-03 10:18:16-05:00",
            "serviceNumber": [
                serial_number,
            ],
        }
        ticket_notes = [
            ticket_note_1,
            ticket_note_2,
            ticket_note_3,
            ticket_note_4,
        ]

        ticket_details_response = {
            "body": {
                "ticketDetails": [
                    ticket_detail_1,
                    ticket_detail_2,
                ],
                "ticketNotes": ticket_notes,
            },
            "status": 200,
        }

        relevant_notes = [
            ticket_note_1,
            ticket_note_3,
            ticket_note_4,
        ]

        outage_monitor_instance._bruin_repository.get_open_outage_tickets = AsyncMock(
            return_value=outage_ticket_response
        )
        outage_monitor_instance._bruin_repository.get_ticket_details = AsyncMock(return_value=ticket_details_response)

        outage_monitor_instance._was_ticket_created_by_automation_engine = Mock(return_value=True)
        outage_monitor_instance._was_last_outage_detected_recently = Mock(return_value=True)
        outage_monitor_instance.is_outage_ticket_auto_resolvable = Mock(return_value=False)
        outage_monitor_instance._is_detail_resolved = Mock()

        await outage_monitor_instance._run_ticket_autoresolve(device)

        outage_monitor_instance._bruin_repository.get_open_outage_tickets.assert_awaited_once_with(
            client_id, service_number=serial_number
        )
        outage_monitor_instance._bruin_repository.get_ticket_details.assert_awaited_once_with(ticket_id)
        outage_monitor_instance._was_last_outage_detected_recently.assert_called_once_with(
            relevant_notes, ticket_creation_date
        )
        outage_monitor_instance.is_outage_ticket_auto_resolvable.assert_called_once_with(
            relevant_notes, max_autoresolves=3
        )
        outage_monitor_instance._is_detail_resolved.assert_not_called()

    @pytest.mark.asyncio
    async def run_ticket_autoresolve_with_ticket_detail_already_resolved_test(self, outage_monitor_instance):
        serial_number = "B827EB92EB72"
        client_id = 9994

        device = {
            "cached_info": {
                "serial_number": serial_number,
                "last_contact": "2020-01-16T14:59:56.245Z",
                "bruin_client_info": {
                    "client_id": client_id,
                    "client_name": "METTEL/NEW YORK",
                },
            },
            "device_info": {
                "probeId": "1",
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
                "nodetonode": {"status": 1, "lastUpdate": "2020-11-11T13:00:11Z"},
                "realservice": {"status": 1, "lastUpdate": "2020-10-15T02:18:28Z"},
            },
        }

        ticket_id = 99999
        ticket_creation_date = "9/25/2020 6:31:54 AM"
        ticket = {
            "clientID": client_id,
            "clientName": "Aperture Science",
            "ticketID": ticket_id,
            "category": "Network Scout",
            "topic": "Service Outage Trouble",
            "ticketStatus": "New",
            "createDate": ticket_creation_date,
            "createdBy": "Intelygenz Ai",
        }
        outage_ticket_response = {
            "body": [
                ticket,
            ],
            "status": 200,
        }

        ticket_detail_1_id = 2746937
        ticket_detail_1 = {
            "detailID": ticket_detail_1_id,
            "detailValue": serial_number,
            "detailStatus": "R",
        }

        ticket_detail_2_id = 999999
        ticket_detail_2 = {
            "detailID": ticket_detail_2_id,
            "detailValue": "VC9999999",
            "detailStatus": "I",
        }

        ticket_note_1 = {
            "noteId": 68246614,
            "noteValue": "#*MetTel's IPA*#\nTriage (Ixia).\nTimeStamp: 2021-01-02 10:18:16-05:00",
            "serviceNumber": [
                serial_number,
            ],
        }
        ticket_note_2 = {
            "noteId": 68246615,
            "noteValue": "Some irrelevant note",
            "serviceNumber": [
                "VC1234567",
            ],
        }
        ticket_note_3 = {
            "noteId": 68246616,
            "noteValue": "#*MetTel's IPA*#\nAuto-resolving detail.\nTimeStamp: 2021-01-03 10:18:16-05:00",
            "serviceNumber": [
                serial_number,
            ],
        }
        ticket_note_4 = {
            "noteId": 68246616,
            "noteValue": "#*MetTel's IPA*#\nAuto-resolving detail.\nTimeStamp: 2021-01-03 10:18:16-05:00",
            "serviceNumber": [
                serial_number,
            ],
        }
        ticket_notes = [
            ticket_note_1,
            ticket_note_2,
            ticket_note_3,
            ticket_note_4,
        ]

        ticket_details_response = {
            "body": {
                "ticketDetails": [
                    ticket_detail_1,
                    ticket_detail_2,
                ],
                "ticketNotes": ticket_notes,
            },
            "status": 200,
        }

        relevant_notes = [
            ticket_note_1,
            ticket_note_3,
            ticket_note_4,
        ]

        outage_monitor_instance._bruin_repository.get_open_outage_tickets = AsyncMock(
            return_value=outage_ticket_response
        )
        outage_monitor_instance._bruin_repository.get_ticket_details = AsyncMock(return_value=ticket_details_response)
        outage_monitor_instance._bruin_repository.resolve_ticket = AsyncMock()

        outage_monitor_instance._was_ticket_created_by_automation_engine = Mock(return_value=True)
        outage_monitor_instance._was_last_outage_detected_recently = Mock(return_value=True)
        outage_monitor_instance.is_outage_ticket_auto_resolvable = Mock(return_value=True)
        outage_monitor_instance._is_detail_resolved = Mock(return_value=True)

        await outage_monitor_instance._run_ticket_autoresolve(device)

        outage_monitor_instance._bruin_repository.get_open_outage_tickets.assert_awaited_once_with(
            client_id, service_number=serial_number
        )
        outage_monitor_instance._bruin_repository.get_ticket_details.assert_awaited_once_with(ticket_id)
        outage_monitor_instance._was_last_outage_detected_recently.assert_called_once_with(
            relevant_notes, ticket_creation_date
        )
        outage_monitor_instance.is_outage_ticket_auto_resolvable.assert_called_once_with(
            relevant_notes, max_autoresolves=3
        )
        outage_monitor_instance._is_detail_resolved.assert_called_once_with(ticket_detail_1)
        outage_monitor_instance._bruin_repository.resolve_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def run_ticket_autoresolve_with_environment_different_from_production_test(self, outage_monitor_instance):
        serial_number = "B827EB92EB72"
        client_id = 9994

        device = {
            "cached_info": {
                "serial_number": serial_number,
                "last_contact": "2020-01-16T14:59:56.245Z",
                "bruin_client_info": {
                    "client_id": client_id,
                    "client_name": "METTEL/NEW YORK",
                },
            },
            "device_info": {
                "probeId": "1",
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
                "nodetonode": {"status": 1, "lastUpdate": "2020-11-11T13:00:11Z"},
                "realservice": {"status": 1, "lastUpdate": "2020-10-15T02:18:28Z"},
            },
        }

        ticket_id = 99999
        ticket_creation_date = "9/25/2020 6:31:54 AM"
        ticket = {
            "clientID": client_id,
            "clientName": "Aperture Science",
            "ticketID": ticket_id,
            "category": "Network Scout",
            "topic": "Service Outage Trouble",
            "ticketStatus": "New",
            "createDate": ticket_creation_date,
            "createdBy": "Intelygenz Ai",
        }
        outage_ticket_response = {
            "body": [
                ticket,
            ],
            "status": 200,
        }

        ticket_detail_1_id = 2746937
        ticket_detail_1 = {
            "detailID": ticket_detail_1_id,
            "detailValue": serial_number,
            "detailStatus": "I",
        }

        ticket_detail_2_id = 999999
        ticket_detail_2 = {
            "detailID": ticket_detail_2_id,
            "detailValue": "VC9999999",
            "detailStatus": "I",
        }

        ticket_note_1 = {
            "noteId": 68246614,
            "noteValue": "#*MetTel's IPA*#\nTriage (Ixia).\nTimeStamp: 2021-01-02 10:18:16-05:00",
            "serviceNumber": [
                serial_number,
            ],
        }
        ticket_note_2 = {
            "noteId": 68246615,
            "noteValue": "Some irrelevant note",
            "serviceNumber": [
                "VC1234567",
            ],
        }
        ticket_note_3 = {
            "noteId": 68246616,
            "noteValue": "#*MetTel's IPA*#\nAuto-resolving detail.\nTimeStamp: 2021-01-03 10:18:16-05:00",
            "serviceNumber": [
                serial_number,
            ],
        }
        ticket_note_4 = {
            "noteId": 68246616,
            "noteValue": "#*MetTel's IPA*#\nAuto-resolving detail.\nTimeStamp: 2021-01-03 10:18:16-05:00",
            "serviceNumber": [
                serial_number,
            ],
        }
        ticket_notes = [
            ticket_note_1,
            ticket_note_2,
            ticket_note_3,
            ticket_note_4,
        ]

        ticket_details_response = {
            "body": {
                "ticketDetails": [
                    ticket_detail_1,
                    ticket_detail_2,
                ],
                "ticketNotes": ticket_notes,
            },
            "status": 200,
        }

        relevant_notes = [
            ticket_note_1,
            ticket_note_3,
            ticket_note_4,
        ]

        outage_monitor_instance._bruin_repository.get_open_outage_tickets = AsyncMock(
            return_value=outage_ticket_response
        )
        outage_monitor_instance._bruin_repository.get_ticket_details = AsyncMock(return_value=ticket_details_response)
        outage_monitor_instance._bruin_repository.resolve_ticket = AsyncMock()

        outage_monitor_instance._was_ticket_created_by_automation_engine = Mock(return_value=True)
        outage_monitor_instance._was_last_outage_detected_recently = Mock(return_value=True)
        outage_monitor_instance.is_outage_ticket_auto_resolvable = Mock(return_value=True)
        outage_monitor_instance._is_detail_resolved = Mock(return_value=False)

        with patch.object(outage_monitor_instance._config, "CURRENT_ENVIRONMENT", "dev"):
            await outage_monitor_instance._run_ticket_autoresolve(device)

        outage_monitor_instance._bruin_repository.get_open_outage_tickets.assert_awaited_once_with(
            client_id, service_number=serial_number
        )
        outage_monitor_instance._bruin_repository.get_ticket_details.assert_awaited_once_with(ticket_id)
        outage_monitor_instance._was_last_outage_detected_recently.assert_called_once_with(
            relevant_notes, ticket_creation_date
        )
        outage_monitor_instance.is_outage_ticket_auto_resolvable.assert_called_once_with(
            relevant_notes, max_autoresolves=3
        )
        outage_monitor_instance._is_detail_resolved.assert_called_once_with(ticket_detail_1)
        outage_monitor_instance._bruin_repository.resolve_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def run_ticket_autoresolve_with_resolve_outage_return_non_2xx_status_test(self, outage_monitor_instance):
        serial_number = "B827EB92EB72"
        client_id = 9994

        device = {
            "cached_info": {
                "serial_number": serial_number,
                "last_contact": "2020-01-16T14:59:56.245Z",
                "bruin_client_info": {
                    "client_id": client_id,
                    "client_name": "METTEL/NEW YORK",
                },
            },
            "device_info": {
                "probeId": "1",
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
                "nodetonode": {"status": 1, "lastUpdate": "2020-11-11T13:00:11Z"},
                "realservice": {"status": 1, "lastUpdate": "2020-10-15T02:18:28Z"},
            },
        }

        ticket_id = 99999
        ticket_creation_date = "9/25/2020 6:31:54 AM"
        ticket = {
            "clientID": client_id,
            "clientName": "Aperture Science",
            "ticketID": ticket_id,
            "category": "Network Scout",
            "topic": "Service Outage Trouble",
            "ticketStatus": "New",
            "createDate": ticket_creation_date,
            "createdBy": "Intelygenz Ai",
        }
        outage_ticket_response = {
            "body": [
                ticket,
            ],
            "status": 200,
        }

        ticket_detail_1_id = 2746937
        ticket_detail_1 = {
            "detailID": ticket_detail_1_id,
            "detailValue": serial_number,
            "detailStatus": "I",
        }

        ticket_detail_2_id = 999999
        ticket_detail_2 = {
            "detailID": ticket_detail_2_id,
            "detailValue": "VC9999999",
            "detailStatus": "I",
        }

        ticket_note_1 = {
            "noteId": 68246614,
            "noteValue": "#*MetTel's IPA*#\nTriage (Ixia).\nTimeStamp: 2021-01-02 10:18:16-05:00",
            "serviceNumber": [
                serial_number,
            ],
        }
        ticket_note_2 = {
            "noteId": 68246615,
            "noteValue": "Some irrelevant note",
            "serviceNumber": [
                "VC1234567",
            ],
        }
        ticket_note_3 = {
            "noteId": 68246616,
            "noteValue": "#*MetTel's IPA*#\nAuto-resolving detail.\nTimeStamp: 2021-01-03 10:18:16-05:00",
            "serviceNumber": [
                serial_number,
            ],
        }
        ticket_note_4 = {
            "noteId": 68246616,
            "noteValue": "#*MetTel's IPA*#\nAuto-resolving detail.\nTimeStamp: 2021-01-03 10:18:16-05:00",
            "serviceNumber": [
                serial_number,
            ],
        }
        ticket_notes = [
            ticket_note_1,
            ticket_note_2,
            ticket_note_3,
            ticket_note_4,
        ]

        ticket_details_response = {
            "body": {
                "ticketDetails": [
                    ticket_detail_1,
                    ticket_detail_2,
                ],
                "ticketNotes": ticket_notes,
            },
            "status": 200,
        }

        relevant_notes = [
            ticket_note_1,
            ticket_note_3,
            ticket_note_4,
        ]

        resolve_ticket_response = {
            "body": "Got internal error from Bruin",
            "status": 500,
        }

        outage_monitor_instance._bruin_repository.get_open_outage_tickets = AsyncMock(
            return_value=outage_ticket_response
        )
        outage_monitor_instance._bruin_repository.get_ticket_details = AsyncMock(return_value=ticket_details_response)
        outage_monitor_instance._bruin_repository.unpause_ticket_detail = AsyncMock()
        outage_monitor_instance._bruin_repository.resolve_ticket = AsyncMock(return_value=resolve_ticket_response)
        outage_monitor_instance._bruin_repository.append_autoresolve_note_to_ticket = AsyncMock()

        outage_monitor_instance._was_ticket_created_by_automation_engine = Mock(return_value=True)
        outage_monitor_instance._was_last_outage_detected_recently = Mock(return_value=True)
        outage_monitor_instance.is_outage_ticket_auto_resolvable = Mock(return_value=True)
        outage_monitor_instance._is_detail_resolved = Mock(return_value=False)
        outage_monitor_instance._get_notes_appended_since_latest_reopen_or_ticket_creation = Mock(return_value=[])

        with patch.object(outage_monitor_instance._config, "CURRENT_ENVIRONMENT", "production"):
            await outage_monitor_instance._run_ticket_autoresolve(device)

        outage_monitor_instance._bruin_repository.get_open_outage_tickets.assert_awaited_once_with(
            client_id, service_number=serial_number
        )
        outage_monitor_instance._bruin_repository.get_ticket_details.assert_awaited_once_with(ticket_id)
        outage_monitor_instance._was_last_outage_detected_recently.assert_called_once_with(
            relevant_notes, ticket_creation_date
        )
        outage_monitor_instance.is_outage_ticket_auto_resolvable.assert_called_once_with(
            relevant_notes, max_autoresolves=3
        )
        outage_monitor_instance._is_detail_resolved.assert_called_once_with(ticket_detail_1)
        outage_monitor_instance._bruin_repository.unpause_ticket_detail.assert_awaited_once_with(
            ticket_id, service_number=serial_number, detail_id=ticket_detail_1_id
        )
        outage_monitor_instance._bruin_repository.resolve_ticket.assert_awaited_once_with(ticket_id, ticket_detail_1_id)
        outage_monitor_instance._bruin_repository.append_autoresolve_note_to_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def run_ticket_autoresolve_with_all_conditions_met_test(self, outage_monitor_instance):
        serial_number = "B827EB92EB72"
        client_id = 9994

        device = {
            "cached_info": {
                "serial_number": serial_number,
                "last_contact": "2020-01-16T14:59:56.245Z",
                "bruin_client_info": {
                    "client_id": client_id,
                    "client_name": "METTEL/NEW YORK",
                },
            },
            "device_info": {
                "probeId": "1",
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
                "nodetonode": {"status": 1, "lastUpdate": "2020-11-11T13:00:11Z"},
                "realservice": {"status": 1, "lastUpdate": "2020-10-15T02:18:28Z"},
            },
        }

        ticket_id = 99999
        ticket_creation_date = "9/25/2020 6:31:54 AM"
        ticket = {
            "clientID": client_id,
            "clientName": "Aperture Science",
            "ticketID": ticket_id,
            "category": "Network Scout",
            "topic": "Service Outage Trouble",
            "ticketStatus": "New",
            "createDate": ticket_creation_date,
            "createdBy": "Intelygenz Ai",
        }
        outage_ticket_response = {
            "body": [
                ticket,
            ],
            "status": 200,
        }

        ticket_detail_1_id = 2746937
        ticket_detail_1 = {
            "detailID": ticket_detail_1_id,
            "detailValue": serial_number,
            "detailStatus": "I",
        }

        ticket_detail_2_id = 999999
        ticket_detail_2 = {
            "detailID": ticket_detail_2_id,
            "detailValue": "VC9999999",
            "detailStatus": "I",
        }

        ticket_note_1 = {
            "noteId": 68246614,
            "noteValue": "#*MetTel's IPA*#\nTriage (Ixia).\nTimeStamp: 2021-01-02 10:18:16-05:00",
            "serviceNumber": [
                serial_number,
            ],
        }
        ticket_note_2 = {
            "noteId": 68246615,
            "noteValue": "Some irrelevant note",
            "serviceNumber": [
                "VC1234567",
            ],
        }
        ticket_note_3 = {
            "noteId": 68246616,
            "noteValue": "#*MetTel's IPA*#\nAuto-resolving detail.\nTimeStamp: 2021-01-03 10:18:16-05:00",
            "serviceNumber": [
                serial_number,
            ],
        }
        ticket_note_4 = {
            "noteId": 68246616,
            "noteValue": "#*MetTel's IPA*#\nAuto-resolving detail.\nTimeStamp: 2021-01-03 10:18:16-05:00",
            "serviceNumber": [
                serial_number,
            ],
        }
        ticket_notes = [
            ticket_note_1,
            ticket_note_2,
            ticket_note_3,
            ticket_note_4,
        ]

        ticket_details_response = {
            "body": {
                "ticketDetails": [
                    ticket_detail_1,
                    ticket_detail_2,
                ],
                "ticketNotes": ticket_notes,
            },
            "status": 200,
        }

        relevant_notes = [
            ticket_note_1,
            ticket_note_3,
            ticket_note_4,
        ]

        resolve_ticket_response = {
            "body": "ok",
            "status": 200,
        }

        outage_monitor_instance._bruin_repository.get_open_outage_tickets = AsyncMock(
            return_value=outage_ticket_response
        )
        outage_monitor_instance._bruin_repository.get_ticket_details = AsyncMock(return_value=ticket_details_response)
        outage_monitor_instance._bruin_repository.unpause_ticket_detail = AsyncMock()
        outage_monitor_instance._bruin_repository.resolve_ticket = AsyncMock(return_value=resolve_ticket_response)
        outage_monitor_instance._bruin_repository.append_autoresolve_note_to_ticket = AsyncMock()

        outage_monitor_instance._was_ticket_created_by_automation_engine = Mock(return_value=True)
        outage_monitor_instance._was_last_outage_detected_recently = Mock(return_value=True)
        outage_monitor_instance.is_outage_ticket_auto_resolvable = Mock(return_value=True)
        outage_monitor_instance._is_detail_resolved = Mock(return_value=False)
        outage_monitor_instance._get_notes_appended_since_latest_reopen_or_ticket_creation = Mock(return_value=[])
        outage_monitor_instance._notify_successful_autoresolve = AsyncMock()

        with patch.object(outage_monitor_instance._config, "CURRENT_ENVIRONMENT", "production"):
            await outage_monitor_instance._run_ticket_autoresolve(device)

        outage_monitor_instance._bruin_repository.get_open_outage_tickets.assert_awaited_once_with(
            client_id, service_number=serial_number
        )
        outage_monitor_instance._bruin_repository.get_ticket_details.assert_awaited_once_with(ticket_id)
        outage_monitor_instance._was_last_outage_detected_recently.assert_called_once_with(
            relevant_notes, ticket_creation_date
        )
        outage_monitor_instance.is_outage_ticket_auto_resolvable.assert_called_once_with(
            relevant_notes, max_autoresolves=3
        )
        outage_monitor_instance._is_detail_resolved.assert_called_once_with(ticket_detail_1)
        outage_monitor_instance._bruin_repository.unpause_ticket_detail.assert_awaited_once_with(
            ticket_id, service_number=serial_number, detail_id=ticket_detail_1_id
        )
        outage_monitor_instance._bruin_repository.resolve_ticket.assert_awaited_once_with(ticket_id, ticket_detail_1_id)
        outage_monitor_instance._bruin_repository.append_autoresolve_note_to_ticket.assert_awaited_once_with(
            ticket_id, serial_number
        )
        outage_monitor_instance._notify_successful_autoresolve.assert_awaited_once_with(ticket_id, ticket_detail_1_id)

    def was_ticket_created_by_automation_engine_test(self, outage_monitor_instance):

        ticket = {
            "clientID": 12345,
            "clientName": "Aperture Science",
            "ticketID": 12345,
            "category": "Network Scout",
            "topic": "Service Outage Trouble",
            "ticketStatus": "New",
            "createDate": "9/25/2020 6:31:54 AM",
            "createdBy": "Intelygenz Ai",
        }
        result = outage_monitor_instance._was_ticket_created_by_automation_engine(ticket)
        assert result is True

        ticket = {
            "clientID": 12345,
            "clientName": "Aperture Science",
            "ticketID": 12345,
            "category": "Network Scout",
            "topic": "Service Outage Trouble",
            "ticketStatus": "New",
            "createDate": "9/25/2020 6:31:54 AM",
            "createdBy": "InterMapper Service",
        }
        result = outage_monitor_instance._was_ticket_created_by_automation_engine(ticket)
        assert result is False

    def is_outage_ticket_detail_auto_resolvable_test(self, outage_monitor_instance):

        autoresolve_limit = 3

        ticket_notes = [
            {
                "noteId": 41894040,
                "noteValue": (
                    "#*Automation Engine*#\nAuto-resolving detail for serial\nTimeStamp: 2021-01-02 10:18:16-05:00"
                ),
                "serviceNumber": [
                    "B827EB92EB72",
                ],
            },
            {
                "noteId": 41894041,
                "noteValue": (
                    "#*MetTel's IPA*#\nAuto-resolving detail for serial\nTimeStamp: 2021-01-03 10:18:16-05:00"
                ),
                "serviceNumber": [
                    "B827EB92EB72",
                ],
            },
        ]
        result = outage_monitor_instance.is_outage_ticket_auto_resolvable(ticket_notes, autoresolve_limit)
        assert result is True

        ticket_notes = [
            {
                "noteId": 41894040,
                "noteValue": (
                    "#*Automation Engine*#\nAuto-resolving detail for serial\nTimeStamp: 2021-01-02 10:18:16-05:00"
                ),
                "serviceNumber": [
                    "B827EB92EB72",
                ],
            },
            {
                "noteId": 41894041,
                "noteValue": (
                    "#*Automation Engine*#\nAuto-resolving detail for serial\nTimeStamp: 2021-01-03 10:18:16-05:00"
                ),
                "serviceNumber": [
                    "B827EB92EB72",
                ],
            },
            {
                "noteId": 41894042,
                "noteValue": (
                    "#*MetTel's IPA*#\nAuto-resolving detail for serial\nTimeStamp: 2021-01-04 10:18:16-05:00"
                ),
                "serviceNumber": [
                    "B827EB92EB72",
                ],
            },
        ]
        result = outage_monitor_instance.is_outage_ticket_auto_resolvable(ticket_notes, autoresolve_limit)
        assert result is False

    @pytest.mark.asyncio
    async def notify_successful_autoresolve_test(self, outage_monitor_instance):
        ticket_id = 12345
        detail_id = 67890

        outage_monitor_instance._notifications_repository.send_slack_message = AsyncMock()

        await outage_monitor_instance._notify_successful_autoresolve(ticket_id, detail_id)

        autoresolve_slack_message = (
            f"Detail {detail_id} of outage ticket {ticket_id} was autoresolved: https://app.bruin.com/t/{ticket_id}"
        )
        outage_monitor_instance._notifications_repository.send_slack_message.assert_awaited_once_with(
            autoresolve_slack_message
        )

    def was_last_outage_detected_recently_with_reopen_note_not_found_and_triage_not_found_test(
        self, outage_monitor_instance
    ):
        ticket_creation_date = "9/25/2020 6:31:54 AM"
        ticket_notes = []

        new_now = parse(ticket_creation_date).replace(tzinfo=utc) + timedelta(minutes=59, seconds=59)
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(outage_monitoring_module, "datetime", new=datetime_mock):
            result = outage_monitor_instance._was_last_outage_detected_recently(ticket_notes, ticket_creation_date)
            assert result is True

        new_now = parse(ticket_creation_date).replace(tzinfo=utc) + timedelta(hours=1)
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(outage_monitoring_module, "datetime", new=datetime_mock):
            result = outage_monitor_instance._was_last_outage_detected_recently(ticket_notes, ticket_creation_date)
            assert result is True

        new_now = parse(ticket_creation_date).replace(tzinfo=utc) + timedelta(hours=1, seconds=1)
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(outage_monitoring_module, "datetime", new=datetime_mock):
            result = outage_monitor_instance._was_last_outage_detected_recently(ticket_notes, ticket_creation_date)
            assert result is False

    def was_last_outage_detected_recently_with_reopen_note_found_test(self, outage_monitor_instance):
        ticket_creation_date = "9/25/2020 6:31:54 AM"
        triage_timestamp = "2021-01-02T10:18:16.71-05:00"
        reopen_timestamp = "2021-01-02T11:00:16.71-05:00"

        ticket_note_1 = {
            "noteId": 68246614,
            "noteValue": "#*MetTel's IPA*#\nTriage\nTimeStamp: 2021-01-02 10:18:16-05:00",
            "serviceNumber": [
                "B827EB92EB72",
            ],
            "createdDate": triage_timestamp,
        }
        ticket_note_2 = {
            "noteId": 68246615,
            "noteValue": "#*MetTel's IPA*#\nRe-opening\nTimeStamp: 2021-01-03 10:18:16-05:00",
            "serviceNumber": [
                "B827EB92EB72",
            ],
            "createdDate": reopen_timestamp,
        }

        ticket_notes = [
            ticket_note_1,
            ticket_note_2,
        ]

        datetime_mock = Mock()

        new_now = parse(reopen_timestamp) + timedelta(minutes=59, seconds=59)
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(outage_monitoring_module, "datetime", new=datetime_mock):
            result = outage_monitor_instance._was_last_outage_detected_recently(ticket_notes, ticket_creation_date)
            assert result is True

        new_now = parse(reopen_timestamp) + timedelta(hours=1)
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(outage_monitoring_module, "datetime", new=datetime_mock):
            result = outage_monitor_instance._was_last_outage_detected_recently(ticket_notes, ticket_creation_date)
            assert result is True

        new_now = parse(reopen_timestamp) + timedelta(hours=1, seconds=1)
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(outage_monitoring_module, "datetime", new=datetime_mock):
            result = outage_monitor_instance._was_last_outage_detected_recently(ticket_notes, ticket_creation_date)
            assert result is False

    def was_last_outage_detected_recently_with_reopen_note_having_old_watermark_found_test(
        self, outage_monitor_instance
    ):
        ticket_creation_date = "9/25/2020 6:31:54 AM"
        triage_timestamp = "2021-01-02T10:18:16.71-05:00"
        reopen_timestamp = "2021-01-02T11:00:16.71-05:00"

        ticket_note_1 = {
            "noteId": 68246614,
            "noteValue": "#*MetTel's IPA*#\nTriage\nTimeStamp: 2021-01-02 10:18:16-05:00",
            "serviceNumber": [
                "B827EB92EB72",
            ],
            "createdDate": triage_timestamp,
        }
        ticket_note_2 = {
            "noteId": 68246615,
            "noteValue": "#*Automation Engine*#\nRe-opening\nTimeStamp: 2021-01-03 10:18:16-05:00",
            "serviceNumber": [
                "B827EB92EB72",
            ],
            "createdDate": reopen_timestamp,
        }

        ticket_notes = [
            ticket_note_1,
            ticket_note_2,
        ]

        datetime_mock = Mock()

        new_now = parse(reopen_timestamp) + timedelta(minutes=59, seconds=59)
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(outage_monitoring_module, "datetime", new=datetime_mock):
            result = outage_monitor_instance._was_last_outage_detected_recently(ticket_notes, ticket_creation_date)
            assert result is True

        new_now = parse(reopen_timestamp) + timedelta(hours=1)
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(outage_monitoring_module, "datetime", new=datetime_mock):
            result = outage_monitor_instance._was_last_outage_detected_recently(ticket_notes, ticket_creation_date)
            assert result is True

        new_now = parse(reopen_timestamp) + timedelta(hours=1, seconds=1)
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(outage_monitoring_module, "datetime", new=datetime_mock):
            result = outage_monitor_instance._was_last_outage_detected_recently(ticket_notes, ticket_creation_date)
            assert result is False

    def was_last_outage_detected_recently_with_reopen_note_not_found_and_triage_note_found_test(
        self, outage_monitor_instance
    ):
        ticket_creation_date = "9/25/2020 6:31:54 AM"
        triage_timestamp = "2021-01-02T10:18:16.71-05:00"

        ticket_note_1 = {
            "noteId": 68246614,
            "noteValue": "#*MetTel's IPA*#\nTriage (Ixia)\nTimeStamp: 2021-01-02 10:18:16-05:00",
            "serviceNumber": [
                "B827EB92EB72",
            ],
            "createdDate": triage_timestamp,
        }

        ticket_notes = [
            ticket_note_1,
        ]

        datetime_mock = Mock()

        new_now = parse(triage_timestamp) + timedelta(minutes=59, seconds=59)
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(outage_monitoring_module, "datetime", new=datetime_mock):
            result = outage_monitor_instance._was_last_outage_detected_recently(ticket_notes, ticket_creation_date)
            assert result is True

        new_now = parse(triage_timestamp) + timedelta(hours=1)
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(outage_monitoring_module, "datetime", new=datetime_mock):
            result = outage_monitor_instance._was_last_outage_detected_recently(ticket_notes, ticket_creation_date)
            assert result is True

        new_now = parse(triage_timestamp) + timedelta(hours=1, seconds=1)
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(outage_monitoring_module, "datetime", new=datetime_mock):
            result = outage_monitor_instance._was_last_outage_detected_recently(ticket_notes, ticket_creation_date)
            assert result is False

    def was_last_outage_detected_recently_with_reopen_note_not_found_and_triage_note_having_old_watermark_found_test(
        self, outage_monitor_instance
    ):
        ticket_creation_date = "9/25/2020 6:31:54 AM"
        triage_timestamp = "2021-01-02T10:18:16.71-05:00"

        ticket_note_1 = {
            "noteId": 68246614,
            "noteValue": "#*Automation Engine*#\nTriage (Ixia)\nTimeStamp: 2021-01-02 10:18:16-05:00",
            "serviceNumber": [
                "B827EB92EB72",
            ],
            "createdDate": triage_timestamp,
        }

        ticket_notes = [
            ticket_note_1,
        ]

        datetime_mock = Mock()

        new_now = parse(triage_timestamp) + timedelta(minutes=59, seconds=59)
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(outage_monitoring_module, "datetime", new=datetime_mock):
            result = outage_monitor_instance._was_last_outage_detected_recently(ticket_notes, ticket_creation_date)
            assert result is True

        new_now = parse(triage_timestamp) + timedelta(hours=1)
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(outage_monitoring_module, "datetime", new=datetime_mock):
            result = outage_monitor_instance._was_last_outage_detected_recently(ticket_notes, ticket_creation_date)
            assert result is True

        new_now = parse(triage_timestamp) + timedelta(hours=1, seconds=1)
        datetime_mock.now = Mock(return_value=new_now)
        with patch.object(outage_monitoring_module, "datetime", new=datetime_mock):
            result = outage_monitor_instance._was_last_outage_detected_recently(ticket_notes, ticket_creation_date)
            assert result is False
