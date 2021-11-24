from datetime import datetime
from typing import List

import pytest

from tests.fixtures._helpers import velocloudize_date


# Factories
@pytest.fixture(scope='session')
def make_bruin_client_info():
    def _inner(*, client_id: int = 0, client_name: str = '', site_id: int = 0):
        return {
            'client_id': client_id,
            'client_name': client_name,
            'site_id': site_id,
        }

    return _inner


@pytest.fixture(scope='session')
def make_links_configuration():
    def _inner(*, interfaces: List[str] = None, mode: str = '', type_: str = ''):
        interfaces = interfaces or []

        return {
            'interfaces': interfaces,
            'mode': mode,
            'type': type_,
        }

    return _inner


@pytest.fixture(scope='session')
def make_list_of_links_configurations():
    def _inner(*links_configurations: List[dict]):
        return list(links_configurations)

    return _inner


@pytest.fixture(scope='session')
def make_cached_edge(make_edge_full_id, make_bruin_client_info, make_site_details):
    def _inner(*, full_id: dict = None, name: str = '', last_contact: str = '',
               logical_ids: List[dict] = None, serial_number: str = '', bruin_client_info: dict = None,
               site_details: dict = None, links_configuration: List[dict] = None):
        full_id = full_id or make_edge_full_id()
        last_contact = last_contact or velocloudize_date(datetime.now())
        logical_ids = logical_ids or []
        bruin_client_info = bruin_client_info or make_bruin_client_info()
        site_details = site_details or make_site_details()
        links_configuration = links_configuration or []

        return {
            'edge': full_id,
            'edge_name': name,
            'last_contact': last_contact,
            'logical_ids': logical_ids,
            'serial_number': serial_number,
            'bruin_client_info': bruin_client_info,
            'site_details': site_details,
            'links_configuration': links_configuration,
        }

    return _inner


@pytest.fixture(scope='session')
def make_customer_cache():
    def _inner(*edges: List[dict]):
        return list(edges)

    return _inner


# RPC requests
@pytest.fixture(scope='session')
def make_get_cache_request(make_rpc_request):
    def _inner(*, request_id: str = '', filter_: dict = None):
        filter_ = filter_ or {}

        payload = {
            'filter': filter_,
        }

        return make_rpc_request(
            request_id=request_id,
            **payload,
        )

    return _inner


# RPC responses
@pytest.fixture(scope='session')
def get_customer_cache_202_response(make_rpc_response):
    return make_rpc_response(
        body='Cache is still being built for host(s): mettel.velocloud.net',
        status=202,
    )


@pytest.fixture(scope='session')
def get_customer_cache_404_response(make_rpc_response):
    return make_rpc_response(
        body='No edges were found for the specified filters',
        status=404,
    )


@pytest.fixture(scope='session')
def get_customer_cache_empty_response(make_rpc_response, make_customer_cache):
    return make_rpc_response(
        body=make_customer_cache(),
        status=200,
    )
