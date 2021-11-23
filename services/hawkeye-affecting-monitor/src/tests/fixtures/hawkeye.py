import pytest
import shortuuid


# Factories
def __generate_test_result(*, date: str, status: str, test_type: str):
    id_ = shortuuid.ShortUUID().random(length=20)

    return {
        "summary": {
            "id": id_,
            "date": date,
            "duration": "30",
            "status": status,
            "reasonCause": "",
            "module": "MESH",
            "testId": "335",
            "testType": test_type,
            "probeFrom": "Vi_Pi_DRI test",
            "probeTo": "V_Basement",
            "mesh": 1,
            "testOptions": "DSCP Setting: Best Effort ",
            "meshId": "CORE",
            "testTag": "",
            "userId": 6,
        },
        "metrics": [
            {
                "metric": "Jitter (ms)",
                "pairName": "KPI from->to",
                "value": "6",
                "threshold": "5",
                "thresholdType": "0",
                "status": "Failed"
            },
            {
                "metric": "Loss",
                "pairName": "KPI from->to",
                "value": "0.5",
                "threshold": "0.2",
                "thresholdType": "0",
                "status": "Passed"
            },
        ]
    }


def __generate_passed_test_result(*, date: str, test_type: str):
    id_ = shortuuid.ShortUUID().random(length=20)

    return {
        "summary": {
            "id": id_,
            "date": date,
            "duration": "30",
            "status": 'Passed',
            "reasonCause": "",
            "module": "MESH",
            "testId": "335",
            "testType": test_type,
            "probeFrom": "Vi_Pi_DRI test",
            "probeTo": "V_Basement",
            "mesh": 1,
            "testOptions": "DSCP Setting: Best Effort ",
            "meshId": "CORE",
            "testTag": "",
            "userId": 6,
        },
        "metrics": [
            {
                "metric": "Jitter (ms)",
                "pairName": "KPI from->to",
                "value": "5",
                "threshold": "6",
                "thresholdType": "0",
                "status": "Passed"
            },
            {
                "metric": "Loss",
                "pairName": "KPI from->to",
                "value": "2",
                "threshold": "5",
                "thresholdType": "0",
                "status": "Passed"
            },
        ],
    }


def __generate_failed_test_result(*, date: str, test_type: str):
    id_ = shortuuid.ShortUUID().random(length=20)

    return {
        "summary": {
            "id": id_,
            "date": date,
            "duration": "30",
            "status": 'Failed',
            "reasonCause": "",
            "module": "MESH",
            "testId": "335",
            "testType": test_type,
            "probeFrom": "Vi_Pi_DRI test",
            "probeTo": "V_Basement",
            "mesh": 1,
            "testOptions": "DSCP Setting: Best Effort ",
            "meshId": "CORE",
            "testTag": "",
            "userId": 6,
        },
        "metrics": [
            {
                "metric": "Jitter (ms)",
                "pairName": "KPI from->to",
                "value": "7",
                "threshold": "6",
                "thresholdType": "0",
                "status": "Failed"
            },
            {
                "metric": "Loss",
                "pairName": "KPI from->to",
                "value": "2",
                "threshold": "5",
                "thresholdType": "0",
                "status": "Passed"
            },
            {
                "metric": "Latency (ms)",
                "pairName": "KPI from->to",
                "value": "10",
                "threshold": "7",
                "thresholdType": "0",
                "status": "Failed"
            },
        ],
    }


def __generate_error_test_result(*, date: str, test_type: str):
    id_ = shortuuid.ShortUUID().random(length=20)

    return {
        "summary": {
            "id": id_,
            "date": date,
            "duration": "30",
            "status": 'Error',
            "reasonCause": "Endpoint ATL_XR2000_1 Not Available for Test",
            "module": "MESH",
            "testId": "335",
            "testType": test_type,
            "probeFrom": "Vi_Pi_DRI test",
            "probeTo": "V_Basement",
            "mesh": 1,
            "testOptions": "DSCP Setting: Best Effort ",
            "meshId": "CORE",
            "testTag": "",
            "userId": 6,
        },
        "metrics": [],
    }


# Probe UIDs
@pytest.fixture(scope='session')
def probe_1_uid():
    return 'b8:27:eb:76:a8:de'


@pytest.fixture(scope='session')
def probe_2_uid():
    return 'c8:27:fc:76:b8:ef'


@pytest.fixture(scope='session')
def probe_3_uid():
    return 'd8:27:ad:76:c8:fa'


# Tests results
@pytest.fixture(scope='session')
def passed_icmp_test_result_1_on_2020_01_16(test_type_icmp_test):
    return __generate_passed_test_result(date='2020-01-16T00:00:00Z', test_type=test_type_icmp_test)


@pytest.fixture(scope='session')
def passed_icmp_test_result_2_on_2020_01_17(test_type_icmp_test):
    return __generate_passed_test_result(date='2020-01-17T00:00:00Z', test_type=test_type_icmp_test)


@pytest.fixture(scope='session')
def failed_icmp_test_result_1_on_2020_01_18(test_type_icmp_test):
    return __generate_failed_test_result(date='2020-01-18T00:00:00Z', test_type=test_type_icmp_test)


@pytest.fixture(scope='session')
def failed_icmp_test_result_2_on_2020_01_19(test_type_icmp_test):
    return __generate_failed_test_result(date='2020-01-19T00:00:00Z', test_type=test_type_icmp_test)


@pytest.fixture(scope='session')
def error_icmp_test_result_1_on_2020_01_20(test_type_icmp_test):
    return __generate_error_test_result(date='2020-01-20T00:00:00Z', test_type=test_type_icmp_test)


@pytest.fixture(scope='session')
def error_icmp_test_result_2_on_2020_01_21(test_type_icmp_test):
    return __generate_error_test_result(date='2020-01-21T00:00:00Z', test_type=test_type_icmp_test)


@pytest.fixture(scope='session')
def passed_network_kpi_test_result_1_on_2020_01_22(test_type_network_kpi):
    return __generate_passed_test_result(date='2020-01-22T00:00:00Z', test_type=test_type_network_kpi)


@pytest.fixture(scope='session')
def failed_network_kpi_test_result_2_on_2020_01_23(test_type_network_kpi):
    return __generate_failed_test_result(date='2020-01-23T00:00:00Z', test_type=test_type_network_kpi)


@pytest.fixture(scope='session')
def tests_results(passed_icmp_test_result_1_on_2020_01_16, passed_icmp_test_result_2_on_2020_01_17,
                  failed_icmp_test_result_1_on_2020_01_18, failed_icmp_test_result_2_on_2020_01_19,
                  error_icmp_test_result_1_on_2020_01_20, error_icmp_test_result_2_on_2020_01_21,
                  passed_network_kpi_test_result_1_on_2020_01_22, failed_network_kpi_test_result_2_on_2020_01_23):
    return [
        passed_icmp_test_result_1_on_2020_01_16,
        passed_icmp_test_result_2_on_2020_01_17,
        failed_icmp_test_result_1_on_2020_01_18,
        failed_icmp_test_result_2_on_2020_01_19,
        error_icmp_test_result_1_on_2020_01_20,
        error_icmp_test_result_2_on_2020_01_21,
        passed_network_kpi_test_result_1_on_2020_01_22,
        failed_network_kpi_test_result_2_on_2020_01_23,
    ]


# Test types
@pytest.fixture(scope='session')
def test_type_network_kpi():
    return 'Network KPI'


@pytest.fixture(scope='session')
def test_type_icmp_test():
    return 'ICMP Test'


# RPC responses
@pytest.fixture(scope='session')
def get_tests_results_under_probe_uid_1_200_response(probe_1_uid, tests_results):
    return {
        'body': {
            probe_1_uid: tests_results,
        },
        'status': 200,
    }


@pytest.fixture(scope='session')
def hawkeye_500_response():
    return {
        'body': 'Got internal error from Hawkeye',
        'status': 500,
    }
