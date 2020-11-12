from unittest.mock import Mock
from datetime import datetime
import pytest

from application.repositories.hawkeye_repository import HawkeyeRepository
from application.repositories.storage_repository import StorageRepository
from application.repositories.bruin_repository import BruinRepository
from application.actions.get_customers import GetCustomers
from application.actions.refresh_cache import RefreshCache

from asynctest import CoroutineMock

from config import testconfig as config


# Scopes
# - function
# - module
# - session


@pytest.fixture(scope='function')
def logger():
    return Mock()


@pytest.fixture(scope='function')
def event_bus():
    return Mock()


@pytest.fixture(scope='function')
def redis():
    return Mock()


@pytest.fixture(scope='function')
def notifications_repository():
    return Mock()


@pytest.fixture(scope='function')
def scheduler():
    return Mock()


@pytest.fixture(scope='function')
def bruin_repository(logger, event_bus):
    return BruinRepository(config, logger, event_bus)


@pytest.fixture(scope='function')
def hawkeye_repository(logger, event_bus, notifications_repository):
    return HawkeyeRepository(logger, event_bus, config, notifications_repository)


@pytest.fixture(scope='function')
def storage_repository(logger, redis):
    return StorageRepository(config, logger, redis)


@pytest.fixture(scope='function')
def get_customer(storage_repository, logger, event_bus):
    event_bus.publish_message = CoroutineMock()
    return GetCustomers(config, logger, storage_repository, event_bus)


@pytest.fixture(scope='function')
def instance_get_customer(storage_repository, logger, event_bus):
    return GetCustomers(config, logger, storage_repository, event_bus)


@pytest.fixture(scope='function')
def refresh_cache(logger, event_bus, scheduler, storage_repository, bruin_repository, hawkeye_repository):
    return RefreshCache(config, event_bus, logger, scheduler, storage_repository,
                        bruin_repository, hawkeye_repository)


@pytest.fixture(scope='function')
def default_call_with_params():
    return {'request_id': '1234', 'response_topic': "hawkeye.probe.request",
            'body': {'serial_number': 'VCO11', 'status': 'down'}}


@pytest.fixture(scope='function')
def probes_example():
    return [{
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
            "lastUpdate": "2020-11-05T13:57:07Z"
        },
        "realservice": {
            "status": 0,
            "lastUpdate": "2020-10-15T02:18:28Z"
        }
    },
        {
            "probeId": "58",
            "uid": "b8:27:eb:1c:60:d5",
            "os": "Linux ARM",
            "name": "Valley-Land",
            "testIp": "Valley-Land",
            "managementIp": "Valley-Land",
            "active": "0",
            "type": "8",
            "mode": "Automatic",
            "n2nMode": "1",
            "rsMode": "1",
            "typeName": "xr_pi",
            "serialNumber": "B827EB1C60D5",
            "probeGroup": "Valley_medical",
            "location": "",
            "latitude": "0",
            "longitude": "0",
            "endpointVersion": "9.6 SP1 build 121",
            "xrVersion": "3.1.10159616",
            "defaultInterface": "eth0",
            "defaultGateway": "10.207.100.10",
            "availableForMesh": "1",
            "lastRestart": "2020-08-05T22:06:05Z",
            "availability": {
                "from": 1,
                "to": 1,
                "mesh": "1"
            },
            "ips": [
                "10.207.100.43",
                "192.226.126.2"
            ],
            "userGroups": [
                "1",
                "3"
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
                "lastUpdate": "2020-08-05T23:31:56Z"
            },
            "realservice": {
                "status": 0,
                "lastUpdate": "2020-11-05T13:57:07Z"
            }
        }]


@pytest.fixture(scope='function')
def get_probes_down(probes_example):
    return probes_example


@pytest.fixture(scope='function')
def response_get_probes_down_ok(get_probes_down):
    return {
        'body': get_probes_down,
        'status': 200
    }


@pytest.fixture(scope='function')
def response_internal_error():
    return {
        'request_id': '1234',
        'body': 'Got internal error from Hawkeye',
        'status': 500,
    }


@pytest.fixture(scope='function')
def cache_probes():
    return [{'last_contact': '2020-11-05T13:57:07Z', 'serial_number': 'B827EB76A8DE',
             'bruin_client_info': {'client_id': 'some client info'}},
            {'last_contact': '2020-11-05T13:57:07Z', 'serial_number': 'B827EB1C60D5',
             'bruin_client_info': {'client_id': 'some client info'}}]


@pytest.fixture(scope='function')
def cache_probes_now():
    return [
        {
            'last_contact': str(datetime.now()),
            'serial_number': 'B827EB76A8DE',
            'bruin_client_info': {'client_id': 'some client info'}
        },
        {
            'last_contact': str(datetime.now()),
            'serial_number': 'B827EB1C60D5',
            'bruin_client_info': {'client_id': 'some client info'}
        }
    ]


@pytest.fixture(scope='function')
def request_message_without_topic():
    return {
        "request_id": '1234',
        "body": {"last_contact_filter": None}
    }


@pytest.fixture(scope='function')
def response_building_cache_message():
    return {
        'request_id': '1234',
        'body': "Cache is still being built",
        'status': 202
    }


@pytest.fixture(scope='function')
def response_not_body_message():
    return {
        'request_id': '1234',
        'body': 'You must specify {.."body":{...}} in the request',
        'status': 400
    }


@pytest.fixture(scope='function')
def response_not_found_message():
    return {
        'request_id': '1234',
        'body': 'No devices were found for the specified filters',
        'status': 404
    }


@pytest.fixture(scope='function')
def response_bruin_get_client_ok():
    return {
        'request_id': '1234',
        'body': {'client_id': 'some client info'},
        'status': 200
    }


@pytest.fixture(scope='function')
def response_bruin_management_status_ok():
    return {
        'request_id': '1234',
        'body': "Active – Gold Monitoring",
        'status': 200
    }


@pytest.fixture(scope='function')
def err_msg_refresh_cache():
    return {
        'request_id': '1234',
        'message': (
            "Maximum retries happened while while refreshing the cache cause of error was Couldn't find any probe"
            " to refresh the cache"
        ),
    }


@pytest.fixture(scope='function')
def response_none_probes():
    return {
        'body': None,
        'status': 200
    }


@pytest.fixture(scope='function')
def response_500_probes():
    return {
        'body': None,
        'status': 500
    }
