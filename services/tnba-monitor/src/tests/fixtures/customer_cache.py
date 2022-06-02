from typing import List

import pytest


# Model-as-dict generators
def __generate_cached_edge(
    *,
    edge_full_id: dict,
    serial_number: str,
    name: str = "",
    site_details: dict = None,
    links_configuration: List[dict] = None,
    **kwargs,
):
    last_contact = kwargs.get("last_contact", "2020-01-16T14:59:56.245Z")
    logical_ids = kwargs.get(
        "logical_ids",
        [
            {
                "interface_name": "GE1",
                "logical_id": "68:ef:bd:71:7b:10:0000",
            },
        ],
    )
    bruin_client_name = kwargs.get("bruin_client_name", "METTEL/NEW YORK")
    bruin_client_id = kwargs.get("bruin_client_id", 9994)

    return {
        "edge": edge_full_id,
        "edge_name": name,
        "last_contact": last_contact,
        "logical_ids": logical_ids,
        "serial_number": serial_number,
        "bruin_client_info": {
            "client_id": bruin_client_id,
            "client_name": bruin_client_name,
        },
        "site_details": site_details,
        "links_configuration": links_configuration,
    }


# Cached edges
@pytest.fixture(scope="session")
def edge_cached_info_1(edge_full_id_1, serial_number_1):
    return __generate_cached_edge(
        edge_full_id=edge_full_id_1,
        serial_number=serial_number_1,
    )


@pytest.fixture(scope="session")
def edge_cached_info_2(edge_full_id_2, serial_number_2):
    return __generate_cached_edge(
        edge_full_id=edge_full_id_2,
        serial_number=serial_number_2,
    )


@pytest.fixture(scope="session")
def edge_cached_info_3(edge_full_id_3, serial_number_3):
    return __generate_cached_edge(
        edge_full_id=edge_full_id_3,
        serial_number=serial_number_3,
    )


@pytest.fixture(scope="session")
def make_cached_edge(make_site_details):
    def _inner(
        edge_full_id,
        serial_number: str = "",
        name: str = "",
        site_details: dict = None,
        links_configuration: List[dict] = None,
    ):

        site_details = site_details or make_site_details()
        links_configuration = links_configuration or []
        return __generate_cached_edge(
            edge_full_id=edge_full_id,
            serial_number=serial_number,
            name=name,
            site_details=site_details,
            links_configuration=links_configuration,
        )

    return _inner


@pytest.fixture(scope="session")
def make_customer_cache():
    def _inner(*edges: List[dict]):
        return list(edges)

    return _inner


# RPC responses
@pytest.fixture(scope="session")
def get_customer_cache_202_response():
    return {
        "body": "Cache is still being built for host(s): mettel.velocloud.net",
        "status": 202,
    }


@pytest.fixture(scope="session")
def get_customer_cache_404_response():
    return {
        "body": "No edges were found for the specified filters",
        "status": 202,
    }
