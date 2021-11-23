import pytest


# Factories
def __generate_cached_device(*, probe_uid: str, serial_number: str, **kwargs):
    last_contact = kwargs.get('last_contact', '2020-01-16T14:59:56.245Z')
    bruin_client_name = kwargs.get('bruin_client_name', 'METTEL/NEW YORK')
    bruin_client_id = kwargs.get('bruin_client_id', 9994)
    probe_id = kwargs.get('probe_id', 1)
    probe_group = kwargs.get('probe_group', 'FIS')
    device_type_name = kwargs.get('device_type_name', 'xr_pi')

    return {
        "probe_id": probe_id,
        "probe_uid": probe_uid,
        "probe_group": probe_group,
        "device_type_name": device_type_name,
        "serial_number": serial_number,
        "last_contact": last_contact,
        "bruin_client_info": {
            "client_id": bruin_client_id,
            "client_name": bruin_client_name,
        },
    }


# Cached devices
@pytest.fixture(scope='session')
def device_cached_info_1(probe_1_uid, serial_number_1):
    return __generate_cached_device(
        probe_uid=probe_1_uid,
        serial_number=serial_number_1,
    )


@pytest.fixture(scope='session')
def device_cached_info_2(probe_2_uid, serial_number_2):
    return __generate_cached_device(
        probe_uid=probe_2_uid,
        serial_number=serial_number_2,
    )


@pytest.fixture(scope='session')
def device_cached_info_3(probe_3_uid, serial_number_3):
    return __generate_cached_device(
        probe_uid=probe_3_uid,
        serial_number=serial_number_3,
    )


@pytest.fixture(scope='session')
def customer_cache(device_cached_info_1, device_cached_info_2, device_cached_info_3):
    return [
        device_cached_info_1,
        device_cached_info_2,
        device_cached_info_3,
    ]


# RPC responses
@pytest.fixture(scope='session')
def get_customer_cache_200_response(customer_cache):
    return {
        'body': customer_cache,
        'status': 200,
    }


@pytest.fixture(scope='session')
def get_customer_cache_202_response():
    return {
        'body': 'Cache is still being built',
        'status': 202,
    }


@pytest.fixture(scope='session')
def get_customer_cache_404_response():
    return {
        'body': 'No devices were found for the specified filters',
        'status': 202,
    }
