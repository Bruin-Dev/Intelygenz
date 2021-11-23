from unittest.mock import Mock

import pytest
from application.actions.get_probes import GetProbes
from application.actions.get_test_results import GetTestResults
from application.clients.hawkeye_client import HawkeyeClient
from application.repositories.hawkeye_repository import HawkeyeRepository
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
def get_probes_init(logger, event_bus, hawkeye_repository):
    return GetProbes(logger, config, event_bus, hawkeye_repository)


@pytest.fixture(scope='function')
def get_test_result_init(logger, event_bus, hawkeye_repository):
    return GetTestResults(logger, config, event_bus, hawkeye_repository)


@pytest.fixture(scope='function')
def hawkeye_client(logger):
    return HawkeyeClient(logger, config)


@pytest.fixture(scope='function')
def hawkeye_repository(logger, hawkeye_client):
    return HawkeyeRepository(logger, hawkeye_client, config)


@pytest.fixture(scope='function')
def request_id():
    return '1234'


@pytest.fixture(scope='function')
def init_msg():
    return {'request_id': '1234', 'body': {}}


@pytest.fixture(scope='function')
def default_call_with_params():
    return {'request_id': '1234', 'response_topic': "hawkeye.probe.request",
            'body': {'serial_number': 'VCO11', 'status': 'down'}}


@pytest.fixture(scope='function')
def default_call_with_params_test_result():
    return {'request_id': '1234', 'response_topic': "hawkeye.test.request",
            'body': {'probe_uids': ["b8:27:eb:76:a8:de"],
                     'interval': {'start': 'fake_start_date', 'end': 'fake_end_date'}}}


@pytest.fixture(scope='function')
def default_call_without_params():
    return {'request_id': '1234', 'response_topic': "hawkeye.probe.request", 'body': {}}


@pytest.fixture(scope='function')
def default_call_without_params_test_result():
    return {'request_id': '1234', 'response_topic': "hawkeye.test.request", 'body': {}}


@pytest.fixture(scope='function')
def default_call_without_body():
    return {'request_id': '1234', 'response_topic': "hawkeye.probe.request"}


@pytest.fixture(scope='function')
def default_call_without_body_test_result():
    return {'request_id': '1234', 'response_topic': "hawkeye.test.request"}


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
                "lastUpdate": "2020-11-05T13:57:07Z"
            },
            "realservice": {
                "status": 0,
                "lastUpdate": "2020-08-05T23:31:56Z"
            }
        }]


@pytest.fixture(scope='function')
def get_probes_down(probes_example):
    return {
        "total_count": "12",
        "count": 12,
        "limit": 100,
        "offset": 0,
        "has_more": 0,
        "records": probes_example
    }


@pytest.fixture(scope='function')
def get_probes_down_not_end(probes_example):
    return {
        "total_count": "12",
        "count": 12,
        "limit": 100,
        "offset": 0,
        "has_more": 1,
        "records": probes_example
    }


@pytest.fixture(scope='function')
def first_call_big_probes(probes_example):
    return {
        "total_count": "1024",
        "count": 500,
        "limit": 500,
        "offset": 0,
        "has_more": 1,
        "records": 250 * probes_example
    }


@pytest.fixture(scope='function')
def second_call_big_probes(probes_example):
    return {
        "total_count": "1024",
        "count": 500,
        "limit": 500,
        "offset": 500,
        "has_more": 1,
        "records": 250 * probes_example
    }


@pytest.fixture(scope='function')
def third_call_big_probes(probes_example):
    return {
        "total_count": "1024",
        "count": 24,
        "limit": 500,
        "offset": 1000,
        "has_more": 0,
        "records": 12 * probes_example
    }


@pytest.fixture(scope='function')
def response_get_probes_down_ok(get_probes_down):
    return {
        'body': get_probes_down,
        'status': 200
    }


@pytest.fixture(scope='function')
def response_get_probes_down_not_end_ok(get_probes_down_not_end):
    return {
        'body': get_probes_down_not_end,
        'status': 200
    }


@pytest.fixture(scope='function')
def first_response_get_probes_down_big_ok(first_call_big_probes):
    return {
        'body': first_call_big_probes,
        'status': 200
    }


@pytest.fixture(scope='function')
def second_response_get_probes_down_big_ok(second_call_big_probes):
    return {
        'body': second_call_big_probes,
        'status': 200
    }


@pytest.fixture(scope='function')
def third_response_get_probes_down_big_ok(third_call_big_probes):
    return {
        'body': third_call_big_probes,
        'status': 200
    }


@pytest.fixture(scope='function')
def response_not_body():
    return {
        'request_id': '1234',
        'body': 'Must include "body" in request',
        'status': 400
    }


@pytest.fixture(scope='function')
def response_bad_status(get_probes_down):
    return {
        'request_id': '1234',
        'body': get_probes_down,
        'status': 400
    }


@pytest.fixture(scope='function')
def get_test_result():
    return {
        "total_count": "2",
        "count": 2,
        "limit": "100",
        "offset": 0,
        "has_more": 0,
        "records": [
            {
                "id": "2951533",
                "date": "2021-01-21T15:21:55Z",
                "duration": 0,
                "meshId": 0,
                "mesh": 0,
                "module": "RealService",
                "probeFrom": "ATL_XR2000_1",
                "probeTo": "8.8.8.8",
                "reasonCause": "",
                "status": "Passed",
                "testId": "316",
                "testOptions": "Destination Servers: 8.8.8.8 Interval: 20 ms Count: 100 packets Packet Size:"
                               " 32 bytes (74) IP Protocol: ipv4 Class of Service: Best Effort Jitter "
                               "Calculation: Enabled",
                "testTag": "Core",
                "testType": "ICMP Test",
                "userId": "1"
            },
            {
                "id": "2951532",
                "date": "2021-01-21T15:21:49Z",
                "duration": 30,
                "meshId": 0,
                "mesh": 0,
                "module": "N2N",
                "probeFrom": "Test_Titan",
                "probeTo": "ATL_XR2000_1",
                "reasonCause": "",
                "status": "Passed",
                "testId": 630,
                "testOptions": "DSCP Setting: Best Effort",
                "testTag": "",
                "testType": "Network KPI",
                "userId": 6
            },

        ]
    }


@pytest.fixture(scope='function')
def get_response_test_result(get_test_result):
    return {
        'status': 200,
        'body': get_test_result['records']
    }


@pytest.fixture(scope='function')
def get_response_test_not_found_result():
    return {
        'status': 404,
        'body': []
    }


@pytest.fixture(scope='function')
def get_test_result_details():
    return {
        "id": "2951533",
        "date": "2020-12-11T09:17:36Z",
        "duration": "60",
        "status": "Passed",
        "reasonCause": "",
        "module": "N2N",
        "testId": "583",
        "testType": "Voice bidirectional",
        "parameters": " Voice Codec: G711 DSCP Setting: Best Effort",
        "probeFrom": "88184-Pi1",
        "probeTo": "88184-Pi2",
        "probeFromId": "77",
        "probeToId": "78",
        "mesh": 0,
        "meshId": "0",
        "metrics": [
            {
                "metric": "Datagrams Out of Order",
                "pairName": "Voice from->to",
                "value": "0",
                "threshold": "1",
                "thresholdType": "0",
                "status": "Passed"
            },
            {
                "metric": "Delay (ms)",
                "pairName": "Voice from->to",
                "value": "1",
                "threshold": "100",
                "thresholdType": "0",
                "status": "Passed"
            },
            {
                "metric": "Jitter (ms)",
                "pairName": "Voice from->to",
                "value": "0.03",
                "threshold": "5",
                "thresholdType": "0",
                "status": "Passed"
            },
            {
                "metric": "Jitter Max (ms)",
                "pairName": "Voice from->to",
                "value": "1",
                "threshold": "5",
                "thresholdType": "0",
                "status": "Passed"
            },
            {
                "metric": "Loss",
                "pairName": "Voice from->to",
                "value": "0",
                "threshold": "0.2",
                "thresholdType": "0",
                "status": "Passed"
            },
            {
                "metric": "Max loss burst",
                "pairName": "Voice from->to",
                "value": "0",
                "threshold": "2",
                "thresholdType": "0",
                "status": "Passed"
            },
            {
                "metric": "MOS",
                "pairName": "Voice from->to",
                "value": "4.37",
                "threshold": "3.9",
                "thresholdType": "1",
                "status": "Passed"
            },
            {
                "metric": "Source and destination ports",
                "pairName": "Voice from->to",
                "value": "source AUTO - dest AUTO",
                "threshold": "",
                "thresholdType": "-1",
                "status": ""
            },
            {
                "metric": "Datagrams Out of Order",
                "pairName": "Voice to->from",
                "value": "0",
                "threshold": "1",
                "thresholdType": "0",
                "status": "Passed"
            },
            {
                "metric": "Delay (ms)",
                "pairName": "Voice to->from",
                "value": "1",
                "threshold": "100",
                "thresholdType": "0",
                "status": "Passed"
            },
            {
                "metric": "Jitter (ms)",
                "pairName": "Voice to->from",
                "value": "0",
                "threshold": "5",
                "thresholdType": "0",
                "status": "Passed"
            },
            {
                "metric": "Jitter Max (ms)",
                "pairName": "Voice to->from",
                "value": "0",
                "threshold": "5",
                "thresholdType": "0",
                "status": "Passed"
            },
            {
                "metric": "Loss",
                "pairName": "Voice to->from",
                "value": "0",
                "threshold": "0.2",
                "thresholdType": "0",
                "status": "Passed"
            },
            {
                "metric": "Max loss burst",
                "pairName": "Voice to->from",
                "value": "0",
                "threshold": "2",
                "thresholdType": "0",
                "status": "Passed"
            },
            {
                "metric": "MOS",
                "pairName": "Voice to->from",
                "value": "4.37",
                "threshold": "3.9",
                "thresholdType": "1",
                "status": "Passed"
            },
            {
                "metric": "Source and destination ports",
                "pairName": "Voice to->from",
                "value": "source AUTO - dest AUTO",
                "threshold": "",
                "thresholdType": "-1",
                "status": ""
            }
        ]
    }


@pytest.fixture(scope='function')
def get_response_test_result_details(get_test_result_details):
    return {
        'status': 200,
        'body': get_test_result_details
    }


@pytest.fixture(scope='function')
def get_response_test_result_details_empty(get_test_result_details):
    return {
        'status': 404,
        'body': []
    }


@pytest.fixture(scope='function')
def response_return_all_test(get_test_result_details):
    return {'body': {"b8:27:eb:76:a8:de": get_test_result_details}, 'status': 200}
