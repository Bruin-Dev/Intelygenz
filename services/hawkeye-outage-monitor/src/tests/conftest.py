from unittest.mock import Mock
import copy

import pytest
from shortuuid import uuid

from application.actions.outage_monitoring import OutageMonitor

from application.repositories.bruin_repository import BruinRepository
from application.repositories.customer_cache_repository import CustomerCacheRepository
from application.repositories.hawkeye_repository import HawkeyeRepository
from application.repositories.metrics_repository import MetricsRepository
from application.repositories.notifications_repository import NotificationsRepository
from application.repositories.utils_repository import UtilsRepository

from config import testconfig as config


# Scopes
# - function
# - module
# - session
@pytest.fixture(scope='function')
def event_bus():
    return Mock()


@pytest.fixture(scope='function')
def logger():
    return Mock()


@pytest.fixture(scope='function')
def scheduler():
    return Mock()


@pytest.fixture(scope='function')
def metrics_repository():
    return Mock()


@pytest.fixture(scope='function')
def notifications_repository(event_bus):
    return NotificationsRepository(event_bus)


@pytest.fixture(scope='function')
def bruin_repository(logger, event_bus, notifications_repository):
    return BruinRepository(config, logger, event_bus, notifications_repository)


@pytest.fixture(scope='function')
def customer_cache_repository():
    return CustomerCacheRepository(event_bus, logger)


@pytest.fixture(scope='function')
def hawkeye_repository(event_bus, logger, notifications_repository):
    return HawkeyeRepository(event_bus, logger, config, notifications_repository)


@pytest.fixture(scope='function')
def utils_repository():
    return UtilsRepository()


@pytest.fixture(scope='function')
def outage_monitor(event_bus, logger, scheduler, metrics_repository, bruin_repository, hawkeye_repository,
                   notifications_repository, utils_repository):
    return OutageMonitor(event_bus, logger, scheduler, config, metrics_repository, bruin_repository, hawkeye_repository,
                         notifications_repository, customer_cache_repository, utils_repository)


@pytest.fixture(scope='function')
def serial_number_1():
    return 'B827EB76A8DE'


@pytest.fixture(scope='function')
def serial_number_2():
    return 'D827GD76C8FG'


@pytest.fixture(scope='function')
def bruin_client_id():
    return 9994


@pytest.fixture(scope='function')
def probe_1(serial_number_1):
    return {
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
            "status": 0,
            "lastUpdate": "2020-10-15T02:18:28Z"
        }
    }


@pytest.fixture(scope='function')
def probe_2(serial_number_2):
    return {
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


@pytest.fixture(scope='function')
def probe_up(serial_number_2):
    return {
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
            "status": 1,
            "lastUpdate": "2020-11-11T13:00:11Z"
        },
        "realservice": {
            "status": 1,
            "lastUpdate": "2020-10-15T02:18:28Z"
        }
    }


@pytest.fixture(scope='function')
def device_1_cached_info(serial_number_1, bruin_client_id):
    return {
        "serial_number": serial_number_1,
        "last_contact": "2020-01-16T14:59:56.245Z",
        "bruin_client_info": {
            "client_id": bruin_client_id,
            "client_name": "METTEL/NEW YORK",
        },
    }


@pytest.fixture(scope='function')
def device_2_cached_info(serial_number_2, bruin_client_id):
    return {
        "serial_number": serial_number_2,
        "last_contact": "2020-01-16T14:59:56.245Z",
        "bruin_client_info": {
            "client_id": bruin_client_id,
            "client_name": "METTEL/NEW YORK",
        },
    }


@pytest.fixture(scope='function')
def device_1_info(probe_1, device_1_cached_info):
    return {
        'device_info': probe_1,
        'cached_info': device_1_cached_info,
    }


@pytest.fixture(scope='function')
def device_2_info(probe_2, device_2_cached_info):
    return {
        'device_info': probe_2,
        'cached_info': device_2_cached_info,
    }


@pytest.fixture(scope='function')
def device_up_info(probe_up, device_2_cached_info):
    return {
        'device_info': probe_up,
        'cached_info': device_2_cached_info,
    }


@pytest.fixture(scope='function')
def devices_info(device_1_info, device_2_info):
    return [
        device_1_info,
        device_2_info,
    ]


@pytest.fixture(scope='function')
def devices_up_info(device_up_info):
    return [
        device_up_info,
    ]


@pytest.fixture(scope='function')
def probes(probe_1, probe_2):
    return [
        probe_1,
        probe_2,
    ]


@pytest.fixture(scope='function')
def probes_response(probes):
    return {
        'body': probes,
        'status': 200,
    }


@pytest.fixture(scope='function')
def probes_up(probe_up):
    return [
        probe_up,
    ]


@pytest.fixture(scope='function')
def probes_up_response(probes_up):
    return {
        'body': probes_up,
        'status': 200,
    }


@pytest.fixture(scope='function')
def ticket_response_reopen():
    return {'body': {}, 'status': 471}


@pytest.fixture(scope='function')
def bruin_exception_response():
    return {
        'request_id': uuid,
        'body': 'Got internal error from Bruin',
        'status': 500,
    }


@pytest.fixture(scope='function')
def ticket_id():
    return 1234


@pytest.fixture(scope='function')
def bruin_example_request(ticket_id):
    return {
        'request_id': uuid,
        'body': {
            'ticket_id': ticket_id,
        },
    }


@pytest.fixture(scope='function')
def ticket_detail_for_serial_1(serial_number_1):
    return {
        "detailID": 2746938,
        "detailValue": serial_number_1,
    }


@pytest.fixture(scope='function')
def ticket_detail_for_serial_2(serial_number_2):
    return {
        "detailID": 2746939,
        "detailValue": serial_number_2,
    }


@pytest.fixture(scope='function')
def bruin_response_ok(ticket_detail_for_serial_1, ticket_detail_for_serial_2):
    return {
        'request_id': uuid,
        'body': {
            'ticketDetails': [
                ticket_detail_for_serial_1,
                ticket_detail_for_serial_2,
            ],
            'ticketNotes': [
                {
                    "noteId": 41894043,
                    "noteValue": f'Some note value to create a note',
                    "createdDate": "2020-02-24T10:07:13.503-05:00",
                },
                {
                    "noteId": 41894044,
                    "noteValue": f'Second value to create a note',
                    "createdDate": "2020-02-24T10:07:13.503-05:00",
                }
            ]
        },
        'status': 200,
    }


@pytest.fixture(scope='function')
def bruin_reopen_response_ok():
    return {
        'body': 'success',
        'status': 200,
    }
