import pytest


# Model-as-dict generators
def __generate_cached_edge(*, edge_full_id: dict, serial_number: str, **kwargs):
    last_contact = kwargs.get('last_contact', '2020-01-16T14:59:56.245Z')
    logical_ids = kwargs.get(
        'logical_ids',
        [
            {
                'interface_name': 'GE1',
                'logical_id': '68:ef:bd:71:7b:10:0000',
            },
        ]
    )
    bruin_client_name = kwargs.get('bruin_client_name', 'METTEL/NEW YORK')
    bruin_client_id = kwargs.get('bruin_client_id', 9994)

    return {
        "edge": edge_full_id,
        "last_contact": last_contact,
        "logical_ids": logical_ids,
        "serial_number": serial_number,
        "bruin_client_info": {
            "client_id": bruin_client_id,
            "client_name": bruin_client_name,
        },
    }


# Cached edges
@pytest.fixture(scope='session')
def edge_cached_info_1(edge_full_id_1, serial_number_1):
    return __generate_cached_edge(
        edge_full_id=edge_full_id_1,
        serial_number=serial_number_1,
    )


@pytest.fixture(scope='session')
def edge_cached_info_2(edge_full_id_2, serial_number_2):
    return __generate_cached_edge(
        edge_full_id=edge_full_id_2,
        serial_number=serial_number_2,
    )


@pytest.fixture(scope='session')
def edge_cached_info_3(edge_full_id_3, serial_number_3):
    return __generate_cached_edge(
        edge_full_id=edge_full_id_3,
        serial_number=serial_number_3,
    )


# RPC responses
@pytest.fixture(scope='session')
def get_customer_cache_202_response():
    return {
        'body': 'Cache is still being built for host(s): mettel.velocloud.net',
        'status': 202,
    }


@pytest.fixture(scope='session')
def get_customer_cache_404_response():
    return {
        'body': 'No edges were found for the specified filters',
        'status': 202,
    }
