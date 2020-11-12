import os

from datetime import datetime
from datetime import timedelta
from unittest.mock import Mock
from unittest.mock import patch

import pytest

from apscheduler.jobstores.base import ConflictingIdError
from apscheduler.util import undefined
from asynctest import CoroutineMock
from shortuuid import uuid
from pytz import timezone
from pytz import utc

from application.actions import outage_monitoring as outage_monitoring_module
from application.actions.outage_monitoring import OutageMonitor
from config import testconfig


uuid_ = uuid()
uuid_mock = patch.object(outage_monitoring_module, 'uuid', return_value=uuid_)


class TestServiceOutageMonitor:
    def instance_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        bruin_repository = Mock()
        hawkeye_repository = Mock()
        notifications_repository = Mock()
        customer_cache_repository = Mock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, bruin_repository, hawkeye_repository,
                                       notifications_repository, customer_cache_repository)

        assert outage_monitor._event_bus is event_bus
        assert outage_monitor._logger is logger
        assert outage_monitor._scheduler is scheduler
        assert outage_monitor._config is config
        assert outage_monitor._bruin_repository is bruin_repository
        assert outage_monitor._hawkeye_repository is hawkeye_repository
        assert outage_monitor._notifications_repository is notifications_repository
        assert outage_monitor._customer_cache_repository is customer_cache_repository

    @pytest.mark.asyncio
    async def start_hawkeye_outage_monitoring_with_exec_on_start_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        bruin_repository = Mock()
        hawkeye_repository = Mock()
        notifications_repository = Mock()
        customer_cache_repository = Mock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, bruin_repository, hawkeye_repository,
                                       notifications_repository, customer_cache_repository)

        next_run_time = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            with patch.object(outage_monitoring_module, 'timezone', new=Mock()):
                await outage_monitor.start_hawkeye_outage_monitoring(exec_on_start=True)

        scheduler.add_job.assert_called_once_with(
            outage_monitor._outage_monitoring_process, 'interval',
            seconds=config.MONITOR_CONFIG['jobs_intervals']['outage_monitor'],
            next_run_time=next_run_time,
            replace_existing=False,
            id='_hawkeye_outage_monitor_process',
        )

    @pytest.mark.asyncio
    async def start_hawkeye_outage_monitoring_with_no_exec_on_start_test(self):
        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        bruin_repository = Mock()
        hawkeye_repository = Mock()
        notifications_repository = Mock()
        customer_cache_repository = Mock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, bruin_repository, hawkeye_repository,
                                       notifications_repository, customer_cache_repository)

        await outage_monitor.start_hawkeye_outage_monitoring(exec_on_start=False)

        scheduler.add_job.assert_called_once_with(
            outage_monitor._outage_monitoring_process, 'interval',
            seconds=config.MONITOR_CONFIG['jobs_intervals']['outage_monitor'],
            next_run_time=undefined,
            replace_existing=False,
            id='_hawkeye_outage_monitor_process',
        )

    @pytest.mark.asyncio
    async def start_hawkeye_outage_monitoring_with_job_id_already_executing_test(self):
        job_id = 'some-duplicated-id'
        exception_instance = ConflictingIdError(job_id)

        event_bus = Mock()
        logger = Mock()
        config = testconfig
        bruin_repository = Mock()
        hawkeye_repository = Mock()
        notifications_repository = Mock()
        customer_cache_repository = Mock()

        scheduler = Mock()
        scheduler.add_job = Mock(side_effect=exception_instance)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, bruin_repository, hawkeye_repository,
                                       notifications_repository, customer_cache_repository)

        try:
            await outage_monitor.start_hawkeye_outage_monitoring(exec_on_start=False)
            # TODO: The test should fail at this point if no exception was raised
        except ConflictingIdError:
            scheduler.add_job.assert_called_once_with(
                outage_monitor._outage_monitoring_process, 'interval',
                seconds=config.MONITOR_CONFIG['jobs_intervals']['outage_monitor'],
                next_run_time=undefined,
                replace_existing=False,
                id='_hawkeye_outage_monitor_process',
            )

    @pytest.mark.asyncio
    async def outage_monitoring_process_ok_test(self):
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
            'body': customer_cache,
            'status': 200,
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
            "availability": {
                "from": 1,
                "to": 1,
                "mesh": "1"
            },
            "ips": [
                "192.168.90.102",
                "192.226.111.211"
            ],
            "userGroups": [
                "1",
                "10"
            ],
            "wifi": {
                "available": 0,
                "associated": 0,
                "bssid": "",
                "ssid": "",
                "frequency": "",
                "level": "0",
                "bitrate": ""
            },
            "nodetonode": {
                "status": 1,
                "lastUpdate": "2020-11-11T13:00:11Z"
            },
            "realservice": {
                "status": 1,
                "lastUpdate": "2020-10-15T02:18:28Z"
            }
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
            "availability": {
                "from": 1,
                "to": 1,
                "mesh": "1"
            },
            "ips": [
                "192.168.90.102",
                "192.226.111.211"
            ],
            "userGroups": [
                "1",
                "10"
            ],
            "wifi": {
                "available": 0,
                "associated": 0,
                "bssid": "",
                "ssid": "",
                "frequency": "",
                "level": "0",
                "bitrate": ""
            },
            "nodetonode": {
                "status": 1,
                "lastUpdate": "2020-11-11T13:00:11Z"
            },
            "realservice": {
                "status": 1,
                "lastUpdate": "2020-10-15T02:18:28Z"
            }
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
            "availability": {
                "from": 1,
                "to": 1,
                "mesh": "1"
            },
            "ips": [
                "192.168.90.102",
                "192.226.111.211"
            ],
            "userGroups": [
                "1",
                "10"
            ],
            "wifi": {
                "available": 0,
                "associated": 0,
                "bssid": "",
                "ssid": "",
                "frequency": "",
                "level": "0",
                "bitrate": ""
            },
            "nodetonode": {
                "status": 0,
                "lastUpdate": "2020-11-11T13:00:11Z"
            },
            "realservice": {
                "status": 0,
                "lastUpdate": "2020-10-15T02:18:28Z"
            }
        }
        probes = [
            probe_1_info,
            probe_2_info,
            probe_3_info,
        ]
        probes_response = {
            'body': probes,
            'status': 200,
        }

        active_probes = [
            probe_1_info,
            probe_3_info,
        ]

        active_probe_with_cached_info_1 = {
            'device_info': probe_1_info,
            'cached_info': device_1_cached_info,
        }
        active_probe_with_cached_info_3 = {
            'device_info': probe_3_info,
            'cached_info': device_3_cached_info,
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

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        bruin_repository = Mock()
        notifications_repository = Mock()

        customer_cache_repository = Mock()
        customer_cache_repository.get_cache_for_outage_monitoring = CoroutineMock(return_value=customer_cache_response)

        hawkeye_repository = Mock()
        hawkeye_repository.get_probes = CoroutineMock(return_value=probes_response)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, bruin_repository, hawkeye_repository,
                                       notifications_repository, customer_cache_repository)
        outage_monitor._map_probes_info_with_customer_cache = Mock(return_value=active_probes_with_customer_cache_info)
        outage_monitor._schedule_recheck_job_for_devices = Mock()

        await outage_monitor._outage_monitoring_process()

        customer_cache_repository.get_cache_for_outage_monitoring.assert_awaited_once()
        hawkeye_repository.get_probes.assert_awaited_once()
        outage_monitor._map_probes_info_with_customer_cache.assert_called_once_with(active_probes, customer_cache)
        outage_monitor._schedule_recheck_job_for_devices.assert_called_once_with(outage_devices_info)

    @pytest.mark.asyncio
    async def outage_monitoring_process_with_customer_cache_response_having_202_status_test(self):
        customer_cache_response = {
            'body': 'Cache is still being built',
            'status': 202,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        bruin_repository = Mock()
        notifications_repository = Mock()

        customer_cache_repository = Mock()
        customer_cache_repository.get_cache_for_outage_monitoring = CoroutineMock(return_value=customer_cache_response)

        hawkeye_repository = Mock()
        hawkeye_repository.get_probes = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, bruin_repository, hawkeye_repository,
                                       notifications_repository, customer_cache_repository)
        outage_monitor._map_probes_info_with_customer_cache = Mock()
        outage_monitor._schedule_recheck_job_for_devices = Mock()

        await outage_monitor._outage_monitoring_process()

        customer_cache_repository.get_cache_for_outage_monitoring.assert_awaited_once()
        hawkeye_repository.get_probes.assert_not_awaited()
        outage_monitor._map_probes_info_with_customer_cache.assert_not_called()
        outage_monitor._schedule_recheck_job_for_devices.assert_not_called()

    @pytest.mark.asyncio
    async def outage_monitoring_process_with_customer_cache_response_having_non_2xx_status_test(self):
        customer_cache_response = {
            'body': 'No devices were found for the specified filters',
            'status': 404,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        bruin_repository = Mock()
        notifications_repository = Mock()

        customer_cache_repository = Mock()
        customer_cache_repository.get_cache_for_outage_monitoring = CoroutineMock(return_value=customer_cache_response)

        hawkeye_repository = Mock()
        hawkeye_repository.get_probes = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, bruin_repository, hawkeye_repository,
                                       notifications_repository, customer_cache_repository)
        outage_monitor._map_probes_info_with_customer_cache = Mock()
        outage_monitor._schedule_recheck_job_for_devices = Mock()

        await outage_monitor._outage_monitoring_process()

        customer_cache_repository.get_cache_for_outage_monitoring.assert_awaited_once()
        hawkeye_repository.get_probes.assert_not_awaited()
        outage_monitor._map_probes_info_with_customer_cache.assert_not_called()
        outage_monitor._schedule_recheck_job_for_devices.assert_not_called()

    @pytest.mark.asyncio
    async def outage_monitoring_process_with_get_probes_response_having_non_2xx_status_test(self):
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
            'body': customer_cache,
            'status': 200,
        }

        probes_response = {
            'body': 'Got internal error from Hawkeye',
            'status': 500,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        bruin_repository = Mock()
        notifications_repository = Mock()

        customer_cache_repository = Mock()
        customer_cache_repository.get_cache_for_outage_monitoring = CoroutineMock(return_value=customer_cache_response)

        hawkeye_repository = Mock()
        hawkeye_repository.get_probes = CoroutineMock(return_value=probes_response)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, bruin_repository, hawkeye_repository,
                                       notifications_repository, customer_cache_repository)
        outage_monitor._map_probes_info_with_customer_cache = Mock()
        outage_monitor._schedule_recheck_job_for_devices = Mock()

        await outage_monitor._outage_monitoring_process()

        customer_cache_repository.get_cache_for_outage_monitoring.assert_awaited_once()
        hawkeye_repository.get_probes.assert_awaited_once()
        outage_monitor._map_probes_info_with_customer_cache.assert_not_called()
        outage_monitor._schedule_recheck_job_for_devices.assert_not_called()

    @pytest.mark.asyncio
    async def outage_monitoring_process_with_empty_list_of_probes_test(self):
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
            'body': customer_cache,
            'status': 200,
        }

        probes_response = {
            'body': [],
            'status': 200,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        bruin_repository = Mock()
        notifications_repository = Mock()

        customer_cache_repository = Mock()
        customer_cache_repository.get_cache_for_outage_monitoring = CoroutineMock(return_value=customer_cache_response)

        hawkeye_repository = Mock()
        hawkeye_repository.get_probes = CoroutineMock(return_value=probes_response)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, bruin_repository, hawkeye_repository,
                                       notifications_repository, customer_cache_repository)
        outage_monitor._map_probes_info_with_customer_cache = Mock()
        outage_monitor._schedule_recheck_job_for_devices = Mock()

        await outage_monitor._outage_monitoring_process()

        customer_cache_repository.get_cache_for_outage_monitoring.assert_awaited_once()
        hawkeye_repository.get_probes.assert_awaited_once()
        outage_monitor._map_probes_info_with_customer_cache.assert_not_called()
        outage_monitor._schedule_recheck_job_for_devices.assert_not_called()

    @pytest.mark.asyncio
    async def outage_monitoring_process_with_no_active_probes_test(self):
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
            'body': customer_cache,
            'status': 200,
        }

        probes_response = {
            'body': [
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
                    "availability": {
                        "from": 1,
                        "to": 1,
                        "mesh": "1"
                    },
                    "ips": [
                        "192.168.90.102",
                        "192.226.111.211"
                    ],
                    "userGroups": [
                        "1",
                        "10"
                    ],
                    "wifi": {
                        "available": 0,
                        "associated": 0,
                        "bssid": "",
                        "ssid": "",
                        "frequency": "",
                        "level": "0",
                        "bitrate": ""
                    },
                    "nodetonode": {
                        "status": 1,
                        "lastUpdate": "2020-11-11T13:00:11Z"
                    },
                    "realservice": {
                        "status": 1,
                        "lastUpdate": "2020-10-15T02:18:28Z"
                    }
                }
            ],
            'status': 200,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        bruin_repository = Mock()
        notifications_repository = Mock()

        customer_cache_repository = Mock()
        customer_cache_repository.get_cache_for_outage_monitoring = CoroutineMock(return_value=customer_cache_response)

        hawkeye_repository = Mock()
        hawkeye_repository.get_probes = CoroutineMock(return_value=probes_response)

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, bruin_repository, hawkeye_repository,
                                       notifications_repository, customer_cache_repository)
        outage_monitor._map_probes_info_with_customer_cache = Mock()
        outage_monitor._schedule_recheck_job_for_devices = Mock()

        await outage_monitor._outage_monitoring_process()

        customer_cache_repository.get_cache_for_outage_monitoring.assert_awaited_once()
        hawkeye_repository.get_probes.assert_awaited_once()
        outage_monitor._map_probes_info_with_customer_cache.assert_not_called()
        outage_monitor._schedule_recheck_job_for_devices.assert_not_called()

    def is_active_probe_test(self):
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

    def is_there_an_outage_test(self):
        probe = {
            "probeId": "1",
            "uid": "b8:27:eb:76:a8:de",
            "os": "Linux ARM",
            "name": "FIS_Demo_XrPi",
            "testIp": "none",
            "managementIp": "none",
            "active": "1",
            # Omitting a few keys for simplicity
            "nodetonode": {
                "status": 1,
                "lastUpdate": "2020-11-11T13:00:11Z"
            },
            "realservice": {
                "status": 1,
                "lastUpdate": "2020-10-15T02:18:28Z"
            }
        }
        result = OutageMonitor._is_there_an_outage(probe)
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
            "nodetonode": {
                "status": 0,
                "lastUpdate": "2020-11-11T13:00:11Z"
            },
            "realservice": {
                "status": 1,
                "lastUpdate": "2020-10-15T02:18:28Z"
            }
        }
        result = OutageMonitor._is_there_an_outage(probe)
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
            "nodetonode": {
                "status": 1,
                "lastUpdate": "2020-11-11T13:00:11Z"
            },
            "realservice": {
                "status": 0,
                "lastUpdate": "2020-10-15T02:18:28Z"
            }
        }
        result = OutageMonitor._is_there_an_outage(probe)
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
            "nodetonode": {
                "status": 0,
                "lastUpdate": "2020-11-11T13:00:11Z"
            },
            "realservice": {
                "status": 0,
                "lastUpdate": "2020-10-15T02:18:28Z"
            }
        }
        result = OutageMonitor._is_there_an_outage(probe)
        assert result is True

    def map_probes_info_with_customer_cache_test(self):
        serial_number_1 = 'B827EB76A8DE'
        serial_number_2 = 'C827FC76B8EF'
        serial_number_3 = 'D827GD76C8FG'
        serial_number_4 = 'E827HE76D8GH'
        serial_number_5 = 'F827IF76E8HI'

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

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        bruin_repository = Mock()
        notifications_repository = Mock()
        customer_cache_repository = Mock()
        hawkeye_repository = Mock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, bruin_repository, hawkeye_repository,
                                       notifications_repository, customer_cache_repository)

        result = outage_monitor._map_probes_info_with_customer_cache(probes, customer_cache)

        expected = [
            {
                'device_info': probe_1,
                'cached_info': device_1_cached_info,
            },
            {
                'device_info': probe_2,
                'cached_info': device_3_cached_info,
            },
        ]
        assert result == expected

    def schedule_recheck_job_for_devices_test(self):
        devices = [
            {
                'cached_info': {
                    'serial_number': 'B827EB76A8DE',
                    'last_contact': '2020-08-17T02:23:59',
                    'bruin_client_info': {
                        'client_id': 9994,
                        'client_name': 'METTEL/NEW YORK',
                    },
                },
                'device_info': [
                    {
                        "probeId": "3",
                        "uid": "b8:27:eb:76:a8:de",
                        "os": "Linux ARM",
                        "name": "FIS_Demo_XrPi",
                        "testIp": "none",
                        "managementIp": "none",
                        "active": "1",
                        "serialNumber": 'B827EB76A8DE',
                        # Omitting a few keys for simplicity
                    }
                ]
            }
        ]

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        bruin_repository = Mock()
        notifications_repository = Mock()
        customer_cache_repository = Mock()
        hawkeye_repository = Mock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, bruin_repository, hawkeye_repository,
                                       notifications_repository, customer_cache_repository)

        next_run_time = datetime.now()
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=next_run_time)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            with patch.object(outage_monitoring_module, 'timezone', new=Mock()):
                outage_monitor._schedule_recheck_job_for_devices(devices)

        expected_run_date = next_run_time + timedelta(seconds=config.MONITOR_CONFIG['jobs_intervals']['quarantine'])
        scheduler.add_job.assert_called_once_with(
            outage_monitor._recheck_devices_for_ticket_creation, 'date',
            args=[devices],
            run_date=expected_run_date,
            replace_existing=False,
            misfire_grace_time=9999,
            id=f'_ticket_creation_recheck',
        )

    @pytest.mark.asyncio
    async def recheck_devices_for_ticket_creation_with_creation_response_having_2xx_status_test(self):
        serial_number_1 = 'B827EB76A8DE'
        serial_number_2 = 'D827GD76C8FG'

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
            "availability": {
                "from": 1,
                "to": 1,
                "mesh": "1"
            },
            "ips": [
                "192.168.90.102",
                "192.226.111.211"
            ],
            "userGroups": [
                "1",
                "10"
            ],
            "wifi": {
                "available": 0,
                "associated": 0,
                "bssid": "",
                "ssid": "",
                "frequency": "",
                "level": "0",
                "bitrate": ""
            },
            "nodetonode": {
                "status": 1,
                "lastUpdate": "2020-11-11T13:00:11Z"
            },
            "realservice": {
                "status": 1,
                "lastUpdate": "2020-10-15T02:18:28Z"
            }
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
            "availability": {
                "from": 1,
                "to": 1,
                "mesh": "1"
            },
            "ips": [
                "192.168.90.102",
                "192.226.111.211"
            ],
            "userGroups": [
                "1",
                "10"
            ],
            "wifi": {
                "available": 0,
                "associated": 0,
                "bssid": "",
                "ssid": "",
                "frequency": "",
                "level": "0",
                "bitrate": ""
            },
            "nodetonode": {
                "status": 0,
                "lastUpdate": "2020-11-11T13:00:11Z"
            },
            "realservice": {
                "status": 1,
                "lastUpdate": "2020-10-15T02:18:28Z"
            }
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
            'device_info': probe_1_info,
            'cached_info': device_1_cached_info,
        }
        device_2_info = {
            'device_info': probe_2_info,
            'cached_info': device_2_cached_info,
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
            'body': probes,
            'status': 200,
        }

        ticket_id = 12345
        create_ticket_response = {
            'body': ticket_id,
            'status': 200,
        }

        triage_note = "This is Hawkeye's triage note"

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        customer_cache_repository = Mock()

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'production'

        bruin_repository = Mock()
        bruin_repository.create_outage_ticket = CoroutineMock(return_value=create_ticket_response)
        bruin_repository.append_triage_note_to_ticket = CoroutineMock()

        hawkeye_repository = Mock()
        hawkeye_repository.get_probes = CoroutineMock(return_value=probes_response)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, bruin_repository, hawkeye_repository,
                                       notifications_repository, customer_cache_repository)
        outage_monitor._map_probes_info_with_customer_cache = Mock(return_value=devices_info)
        outage_monitor._build_triage_note = Mock(return_value=triage_note)

        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            await outage_monitor._recheck_devices_for_ticket_creation(devices_info)

        hawkeye_repository.get_probes.assert_awaited_once()
        outage_monitor._map_probes_info_with_customer_cache.assert_called_once_with(probes, devices_cached_info)
        bruin_repository.create_outage_ticket.assert_awaited_once_with(bruin_client_id, serial_number_2)
        outage_monitor._build_triage_note.assert_called_once_with(probe_2_info)
        bruin_repository.append_triage_note_to_ticket.assert_awaited_once_with(ticket_id, serial_number_2, triage_note)

    @pytest.mark.asyncio
    async def recheck_devices_for_ticket_creation_with_creation_response_having_409_status_test(self):
        serial_number_1 = 'B827EB76A8DE'
        serial_number_2 = 'D827GD76C8FG'

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
            "availability": {
                "from": 1,
                "to": 1,
                "mesh": "1"
            },
            "ips": [
                "192.168.90.102",
                "192.226.111.211"
            ],
            "userGroups": [
                "1",
                "10"
            ],
            "wifi": {
                "available": 0,
                "associated": 0,
                "bssid": "",
                "ssid": "",
                "frequency": "",
                "level": "0",
                "bitrate": ""
            },
            "nodetonode": {
                "status": 1,
                "lastUpdate": "2020-11-11T13:00:11Z"
            },
            "realservice": {
                "status": 1,
                "lastUpdate": "2020-10-15T02:18:28Z"
            }
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
            "availability": {
                "from": 1,
                "to": 1,
                "mesh": "1"
            },
            "ips": [
                "192.168.90.102",
                "192.226.111.211"
            ],
            "userGroups": [
                "1",
                "10"
            ],
            "wifi": {
                "available": 0,
                "associated": 0,
                "bssid": "",
                "ssid": "",
                "frequency": "",
                "level": "0",
                "bitrate": ""
            },
            "nodetonode": {
                "status": 0,
                "lastUpdate": "2020-11-11T13:00:11Z"
            },
            "realservice": {
                "status": 1,
                "lastUpdate": "2020-10-15T02:18:28Z"
            }
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
            'device_info': probe_1_info,
            'cached_info': device_1_cached_info,
        }
        device_2_info = {
            'device_info': probe_2_info,
            'cached_info': device_2_cached_info,
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
            'body': probes,
            'status': 200,
        }

        ticket_id = 12345
        create_ticket_response = {
            'body': ticket_id,
            'status': 409,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        customer_cache_repository = Mock()

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'production'

        bruin_repository = Mock()
        bruin_repository.create_outage_ticket = CoroutineMock(return_value=create_ticket_response)
        bruin_repository.append_triage_note_to_ticket = CoroutineMock()

        hawkeye_repository = Mock()
        hawkeye_repository.get_probes = CoroutineMock(return_value=probes_response)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, bruin_repository, hawkeye_repository,
                                       notifications_repository, customer_cache_repository)
        outage_monitor._map_probes_info_with_customer_cache = Mock(return_value=devices_info)
        outage_monitor._build_triage_note = Mock()

        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            await outage_monitor._recheck_devices_for_ticket_creation(devices_info)

        hawkeye_repository.get_probes.assert_awaited_once()
        outage_monitor._map_probes_info_with_customer_cache.assert_called_once_with(probes, devices_cached_info)
        bruin_repository.create_outage_ticket.assert_awaited_once_with(bruin_client_id, serial_number_2)
        outage_monitor._build_triage_note.assert_not_called()
        bruin_repository.append_triage_note_to_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def recheck_devices_for_ticket_creation_with_creation_response_having_471_status_test(self):
        serial_number_1 = 'B827EB76A8DE'
        serial_number_2 = 'D827GD76C8FG'

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
            "availability": {
                "from": 1,
                "to": 1,
                "mesh": "1"
            },
            "ips": [
                "192.168.90.102",
                "192.226.111.211"
            ],
            "userGroups": [
                "1",
                "10"
            ],
            "wifi": {
                "available": 0,
                "associated": 0,
                "bssid": "",
                "ssid": "",
                "frequency": "",
                "level": "0",
                "bitrate": ""
            },
            "nodetonode": {
                "status": 1,
                "lastUpdate": "2020-11-11T13:00:11Z"
            },
            "realservice": {
                "status": 1,
                "lastUpdate": "2020-10-15T02:18:28Z"
            }
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
            "availability": {
                "from": 1,
                "to": 1,
                "mesh": "1"
            },
            "ips": [
                "192.168.90.102",
                "192.226.111.211"
            ],
            "userGroups": [
                "1",
                "10"
            ],
            "wifi": {
                "available": 0,
                "associated": 0,
                "bssid": "",
                "ssid": "",
                "frequency": "",
                "level": "0",
                "bitrate": ""
            },
            "nodetonode": {
                "status": 0,
                "lastUpdate": "2020-11-11T13:00:11Z"
            },
            "realservice": {
                "status": 1,
                "lastUpdate": "2020-10-15T02:18:28Z"
            }
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
            'device_info': probe_1_info,
            'cached_info': device_1_cached_info,
        }
        device_2_info = {
            'device_info': probe_2_info,
            'cached_info': device_2_cached_info,
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
            'body': probes,
            'status': 200,
        }

        ticket_id = 12345
        create_ticket_response = {
            'body': ticket_id,
            'status': 471,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        customer_cache_repository = Mock()

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'production'

        bruin_repository = Mock()
        bruin_repository.create_outage_ticket = CoroutineMock(return_value=create_ticket_response)
        bruin_repository.append_triage_note_to_ticket = CoroutineMock()

        hawkeye_repository = Mock()
        hawkeye_repository.get_probes = CoroutineMock(return_value=probes_response)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, bruin_repository, hawkeye_repository,
                                       notifications_repository, customer_cache_repository)
        outage_monitor._map_probes_info_with_customer_cache = Mock(return_value=devices_info)
        outage_monitor._build_triage_note = Mock()

        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            await outage_monitor._recheck_devices_for_ticket_creation(devices_info)

        hawkeye_repository.get_probes.assert_awaited_once()
        outage_monitor._map_probes_info_with_customer_cache.assert_called_once_with(probes, devices_cached_info)
        bruin_repository.create_outage_ticket.assert_awaited_once_with(bruin_client_id, serial_number_2)
        outage_monitor._build_triage_note.assert_not_called()
        bruin_repository.append_triage_note_to_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def recheck_devices_for_ticket_creation_with_get_probes_response_having_non_2xx_status_test(self):
        serial_number_1 = 'B827EB76A8DE'
        serial_number_2 = 'D827GD76C8FG'

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
            "availability": {
                "from": 1,
                "to": 1,
                "mesh": "1"
            },
            "ips": [
                "192.168.90.102",
                "192.226.111.211"
            ],
            "userGroups": [
                "1",
                "10"
            ],
            "wifi": {
                "available": 0,
                "associated": 0,
                "bssid": "",
                "ssid": "",
                "frequency": "",
                "level": "0",
                "bitrate": ""
            },
            "nodetonode": {
                "status": 1,
                "lastUpdate": "2020-11-11T13:00:11Z"
            },
            "realservice": {
                "status": 1,
                "lastUpdate": "2020-10-15T02:18:28Z"
            }
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
            "availability": {
                "from": 1,
                "to": 1,
                "mesh": "1"
            },
            "ips": [
                "192.168.90.102",
                "192.226.111.211"
            ],
            "userGroups": [
                "1",
                "10"
            ],
            "wifi": {
                "available": 0,
                "associated": 0,
                "bssid": "",
                "ssid": "",
                "frequency": "",
                "level": "0",
                "bitrate": ""
            },
            "nodetonode": {
                "status": 0,
                "lastUpdate": "2020-11-11T13:00:11Z"
            },
            "realservice": {
                "status": 1,
                "lastUpdate": "2020-10-15T02:18:28Z"
            }
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
            'device_info': probe_1_info,
            'cached_info': device_1_cached_info,
        }
        device_2_info = {
            'device_info': probe_2_info,
            'cached_info': device_2_cached_info,
        }
        devices_info = [
            device_1_info,
            device_2_info,
        ]

        probes_response = {
            'body': 'Got internal error from Hawkeye',
            'status': 500,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        customer_cache_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.create_outage_ticket = CoroutineMock()
        bruin_repository.append_triage_note_to_ticket = CoroutineMock()

        hawkeye_repository = Mock()
        hawkeye_repository.get_probes = CoroutineMock(return_value=probes_response)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, bruin_repository, hawkeye_repository,
                                       notifications_repository, customer_cache_repository)
        outage_monitor._map_probes_info_with_customer_cache = Mock()
        outage_monitor._build_triage_note = Mock()

        await outage_monitor._recheck_devices_for_ticket_creation(devices_info)

        hawkeye_repository.get_probes.assert_awaited_once()
        outage_monitor._map_probes_info_with_customer_cache.assert_not_called()
        bruin_repository.create_outage_ticket.assert_not_awaited()
        outage_monitor._build_triage_note.assert_not_called()
        bruin_repository.append_triage_note_to_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def recheck_devices_for_ticket_creation_with_empty_list_of_probes_test(self):
        serial_number_1 = 'B827EB76A8DE'
        serial_number_2 = 'D827GD76C8FG'

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
            "availability": {
                "from": 1,
                "to": 1,
                "mesh": "1"
            },
            "ips": [
                "192.168.90.102",
                "192.226.111.211"
            ],
            "userGroups": [
                "1",
                "10"
            ],
            "wifi": {
                "available": 0,
                "associated": 0,
                "bssid": "",
                "ssid": "",
                "frequency": "",
                "level": "0",
                "bitrate": ""
            },
            "nodetonode": {
                "status": 1,
                "lastUpdate": "2020-11-11T13:00:11Z"
            },
            "realservice": {
                "status": 1,
                "lastUpdate": "2020-10-15T02:18:28Z"
            }
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
            "availability": {
                "from": 1,
                "to": 1,
                "mesh": "1"
            },
            "ips": [
                "192.168.90.102",
                "192.226.111.211"
            ],
            "userGroups": [
                "1",
                "10"
            ],
            "wifi": {
                "available": 0,
                "associated": 0,
                "bssid": "",
                "ssid": "",
                "frequency": "",
                "level": "0",
                "bitrate": ""
            },
            "nodetonode": {
                "status": 0,
                "lastUpdate": "2020-11-11T13:00:11Z"
            },
            "realservice": {
                "status": 1,
                "lastUpdate": "2020-10-15T02:18:28Z"
            }
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
            'device_info': probe_1_info,
            'cached_info': device_1_cached_info,
        }
        device_2_info = {
            'device_info': probe_2_info,
            'cached_info': device_2_cached_info,
        }
        devices_info = [
            device_1_info,
            device_2_info,
        ]

        probes_response = {
            'body': [],
            'status': 200,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        customer_cache_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.create_outage_ticket = CoroutineMock()
        bruin_repository.append_triage_note_to_ticket = CoroutineMock()

        hawkeye_repository = Mock()
        hawkeye_repository.get_probes = CoroutineMock(return_value=probes_response)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, bruin_repository, hawkeye_repository,
                                       notifications_repository, customer_cache_repository)
        outage_monitor._map_probes_info_with_customer_cache = Mock()
        outage_monitor._build_triage_note = Mock()

        await outage_monitor._recheck_devices_for_ticket_creation(devices_info)

        hawkeye_repository.get_probes.assert_awaited_once()
        outage_monitor._map_probes_info_with_customer_cache.assert_not_called()
        bruin_repository.create_outage_ticket.assert_not_awaited()
        outage_monitor._build_triage_note.assert_not_called()
        bruin_repository.append_triage_note_to_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def recheck_devices_for_ticket_creation_with_no_active_probes_test(self):
        serial_number_1 = 'B827EB76A8DE'
        serial_number_2 = 'D827GD76C8FG'

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
            "availability": {
                "from": 1,
                "to": 1,
                "mesh": "1"
            },
            "ips": [
                "192.168.90.102",
                "192.226.111.211"
            ],
            "userGroups": [
                "1",
                "10"
            ],
            "wifi": {
                "available": 0,
                "associated": 0,
                "bssid": "",
                "ssid": "",
                "frequency": "",
                "level": "0",
                "bitrate": ""
            },
            "nodetonode": {
                "status": 1,
                "lastUpdate": "2020-11-11T13:00:11Z"
            },
            "realservice": {
                "status": 1,
                "lastUpdate": "2020-10-15T02:18:28Z"
            }
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
            "availability": {
                "from": 1,
                "to": 1,
                "mesh": "1"
            },
            "ips": [
                "192.168.90.102",
                "192.226.111.211"
            ],
            "userGroups": [
                "1",
                "10"
            ],
            "wifi": {
                "available": 0,
                "associated": 0,
                "bssid": "",
                "ssid": "",
                "frequency": "",
                "level": "0",
                "bitrate": ""
            },
            "nodetonode": {
                "status": 0,
                "lastUpdate": "2020-11-11T13:00:11Z"
            },
            "realservice": {
                "status": 1,
                "lastUpdate": "2020-10-15T02:18:28Z"
            }
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
            'device_info': probe_1_info,
            'cached_info': device_1_cached_info,
        }
        device_2_info = {
            'device_info': probe_2_info,
            'cached_info': device_2_cached_info,
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
                "availability": {
                    "from": 1,
                    "to": 1,
                    "mesh": "1"
                },
                "ips": [
                    "192.168.90.102",
                    "192.226.111.211"
                ],
                "userGroups": [
                    "1",
                    "10"
                ],
                "wifi": {
                    "available": 0,
                    "associated": 0,
                    "bssid": "",
                    "ssid": "",
                    "frequency": "",
                    "level": "0",
                    "bitrate": ""
                },
                "nodetonode": {
                    "status": 1,
                    "lastUpdate": "2020-11-11T13:00:11Z"
                },
                "realservice": {
                    "status": 1,
                    "lastUpdate": "2020-10-15T02:18:28Z"
                }
            }
        ]
        probes_response = {
            'body': probes,
            'status': 200,
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        customer_cache_repository = Mock()

        bruin_repository = Mock()
        bruin_repository.create_outage_ticket = CoroutineMock()
        bruin_repository.append_triage_note_to_ticket = CoroutineMock()

        hawkeye_repository = Mock()
        hawkeye_repository.get_probes = CoroutineMock(return_value=probes_response)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, bruin_repository, hawkeye_repository,
                                       notifications_repository, customer_cache_repository)
        outage_monitor._map_probes_info_with_customer_cache = Mock()
        outage_monitor._build_triage_note = Mock()

        await outage_monitor._recheck_devices_for_ticket_creation(devices_info)

        hawkeye_repository.get_probes.assert_awaited_once()
        outage_monitor._map_probes_info_with_customer_cache.assert_not_called()
        bruin_repository.create_outage_ticket.assert_not_awaited()
        outage_monitor._build_triage_note.assert_not_called()
        bruin_repository.append_triage_note_to_ticket.assert_not_awaited()

    @pytest.mark.asyncio
    async def recheck_devices_for_ticket_creation_with_environment_other_than_production_test(self):
        serial_number_1 = 'B827EB76A8DE'
        serial_number_2 = 'D827GD76C8FG'

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
            "availability": {
                "from": 1,
                "to": 1,
                "mesh": "1"
            },
            "ips": [
                "192.168.90.102",
                "192.226.111.211"
            ],
            "userGroups": [
                "1",
                "10"
            ],
            "wifi": {
                "available": 0,
                "associated": 0,
                "bssid": "",
                "ssid": "",
                "frequency": "",
                "level": "0",
                "bitrate": ""
            },
            "nodetonode": {
                "status": 1,
                "lastUpdate": "2020-11-11T13:00:11Z"
            },
            "realservice": {
                "status": 1,
                "lastUpdate": "2020-10-15T02:18:28Z"
            }
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
            "availability": {
                "from": 1,
                "to": 1,
                "mesh": "1"
            },
            "ips": [
                "192.168.90.102",
                "192.226.111.211"
            ],
            "userGroups": [
                "1",
                "10"
            ],
            "wifi": {
                "available": 0,
                "associated": 0,
                "bssid": "",
                "ssid": "",
                "frequency": "",
                "level": "0",
                "bitrate": ""
            },
            "nodetonode": {
                "status": 0,
                "lastUpdate": "2020-11-11T13:00:11Z"
            },
            "realservice": {
                "status": 1,
                "lastUpdate": "2020-10-15T02:18:28Z"
            }
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
            'device_info': probe_1_info,
            'cached_info': device_1_cached_info,
        }
        device_2_info = {
            'device_info': probe_2_info,
            'cached_info': device_2_cached_info,
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
            'body': probes,
            'status': 200,
        }

        ticket_id = 12345
        create_ticket_response = {
            'body': ticket_id,
            'status': 200,
        }

        triage_note = "This is Hawkeye's triage note"

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        customer_cache_repository = Mock()

        config = testconfig
        custom_monitor_config = config.MONITOR_CONFIG.copy()
        custom_monitor_config['environment'] = 'dev'

        bruin_repository = Mock()
        bruin_repository.create_outage_ticket = CoroutineMock(return_value=create_ticket_response)
        bruin_repository.append_triage_note_to_ticket = CoroutineMock()

        hawkeye_repository = Mock()
        hawkeye_repository.get_probes = CoroutineMock(return_value=probes_response)

        notifications_repository = Mock()
        notifications_repository.send_slack_message = CoroutineMock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, bruin_repository, hawkeye_repository,
                                       notifications_repository, customer_cache_repository)
        outage_monitor._map_probes_info_with_customer_cache = Mock(return_value=devices_info)
        outage_monitor._build_triage_note = Mock(return_value=triage_note)

        with patch.dict(config.MONITOR_CONFIG, custom_monitor_config):
            await outage_monitor._recheck_devices_for_ticket_creation(devices_info)

        hawkeye_repository.get_probes.assert_awaited_once()
        outage_monitor._map_probes_info_with_customer_cache.assert_called_once_with(probes, devices_cached_info)
        bruin_repository.create_outage_ticket.assert_not_awaited()
        outage_monitor._build_triage_note.assert_not_called()
        bruin_repository.append_triage_note_to_ticket.assert_not_awaited()

    def build_triage_note_test(self):
        probe_info = {
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
            "serialNumber": 'B827EB76A8DE',
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
            "availability": {
                "from": 1,
                "to": 1,
                "mesh": "1"
            },
            "ips": [
                "192.168.90.102",
                "192.226.111.211"
            ],
            "userGroups": [
                "1",
                "10"
            ],
            "wifi": {
                "available": 0,
                "associated": 0,
                "bssid": "",
                "ssid": "",
                "frequency": "",
                "level": "0",
                "bitrate": ""
            },
            "nodetonode": {
                "status": 0,
                "lastUpdate": "2020-11-11T13:00:11Z"
            },
            "realservice": {
                "status": 1,
                "lastUpdate": "2020-11-15T10:18:28Z"
            }
        }

        event_bus = Mock()
        logger = Mock()
        scheduler = Mock()
        config = testconfig
        bruin_repository = Mock()
        hawkeye_repository = Mock()
        notifications_repository = Mock()
        customer_cache_repository = Mock()

        outage_monitor = OutageMonitor(event_bus, logger, scheduler, config, bruin_repository, hawkeye_repository,
                                       notifications_repository, customer_cache_repository)

        current_datetime = datetime.now(utc)
        datetime_mock = Mock()
        datetime_mock.now = Mock(return_value=current_datetime)
        with patch.object(outage_monitoring_module, 'datetime', new=datetime_mock):
            triage_note = outage_monitor._build_triage_note(probe_info)

        expected_note = os.linesep.join([
            '#*Automation Engine*#',
            'Triage (Ixia)',
            '',
            'Hawkeye Instance: https://ixia.metconnect.net/',
            'Links: [Dashboard|https://ixia.metconnect.net/ixrr_main.php?type=ProbesManagement] - '
            '[Probe|https://ixia.metconnect.net/probeinformation.php?probeid=1]',
            'Device Name: FIS_Demo_XrPi',
            'Device Type: xr_pi',
            'Serial: B827EB76A8DE',
            'Device Node to Node Status: DOWN',
            'Node to Node Last Update: 2020-11-11 08:00:11-05:00',
            'Device Real Service Status: UP',
            'Real Service Last Update: 2020-11-15 05:18:28-05:00',
            '',
            f'TimeStamp: {str(current_datetime.astimezone(timezone(config.MONITOR_CONFIG["timezone"])))}',
        ])
        assert triage_note == expected_note
