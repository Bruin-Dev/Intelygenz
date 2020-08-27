from unittest.mock import Mock

from datetime import datetime, timedelta
import pytest
from asynctest import CoroutineMock

from application.actions.get_customers import GetCustomers
from application.actions.refresh_cache import RefreshCache
from application.repositories.storage_repository import StorageRepository
from application.repositories.bruin_repository import BruinRepository
from application.repositories.velocloud_repository import VelocloudRepository
from config import testconfig as config


# Scopes
# - function
# - module
# - session


@pytest.fixture(scope='function')
def mock_logger():
    logger = Mock()
    return logger


@pytest.fixture(scope='function')
def mock_event_bus():
    event_bus = Mock()
    return event_bus


@pytest.fixture(scope='function')
def mock_redis():
    redis = Mock()
    return redis


@pytest.fixture(scope='function')
def mock_scheduler():
    scheduler = Mock()
    return scheduler


@pytest.fixture(scope='function')
def mock_storage_repository():
    storage_repository = Mock()
    return storage_repository


@pytest.fixture(scope='function')
def mock_velocloud_repository():
    velocloud_repository = Mock()
    return velocloud_repository


@pytest.fixture(scope='function')
def instance_velocloud_repository(mock_logger, mock_event_bus, ):
    return VelocloudRepository(config, mock_logger, mock_event_bus)


@pytest.fixture(scope='function')
def instance_bruin_repository(mock_logger, mock_event_bus):
    return BruinRepository(config, mock_logger, mock_event_bus)


@pytest.fixture(scope='function')
def instance_storage_repository(mock_logger, mock_redis):
    return StorageRepository(config, mock_logger, mock_redis)


@pytest.fixture(scope='function')
def instance_refresh_cache(mock_logger, mock_event_bus, mock_scheduler, mock_storage_repository,
                           instance_bruin_repository, mock_velocloud_repository):
    return RefreshCache(config, mock_event_bus, mock_logger, mock_scheduler, mock_storage_repository,
                        instance_bruin_repository, mock_velocloud_repository)


@pytest.fixture(scope='function')
def instance_request_message():
    return {
        "request_id": '1111',
        "response_topic": "some.topic",
        "body": {"filter": {"mettel.velocloud.com": []},
                 "last_contact_filter": None}
    }


@pytest.fixture(scope='function')
def instance_request_message_without_topic():
    return {
        "request_id": '1111',
        "body": {"filter": {"mettel.velocloud.com": []},
                 "last_contact_filter": None}
    }


@pytest.fixture(scope='function')
def instance_response_message():
    return {
        'request_id': '1111',
        'body': "Cache is still being built for host(s): mettel.velocloud.com",
        'status': 202
    }


@pytest.fixture(scope='function')
def instance_cache_edges():
    return [{
        'edge': {'host': 'some host', 'enterprise_id': 123, 'edge_id': 321},
        'last_contact': str(datetime.now()),
        'serial_number': "VC01",
        'bruin_client_info': 'some client info'
    },
        {
            'edge': {'host': 'some host', 'enterprise_id': 1, 'edge_id': 321},
            'last_contact': str(datetime.now()),
            'serial_number': "VC02",
            'bruin_client_info': 'some client info'
        }]


@pytest.fixture(scope='function')
def instance_edges_refresh_cache():
    return [{
        'edge': {'host': 'metvco02.mettel.net', 'enterprise_id': 123, 'edge_id': 321},
        'serial_number': "VC01"
    },
        {
            'edge': {'host': 'metvco04.mettel.net', 'enterprise_id': 123, 'edge_id': 321},
            'serial_number': "VC02"
        }]


@pytest.fixture(scope='function')
def instance_err_msg_refresh_cache():
    return {
        'request_id': '1111',
        'message': (
            "[customer-cache] Too many consecutive failures happened while trying to claim the list "
            "of edges from Velocloud"
        ),
    }


@pytest.fixture(scope='function')
def instance_velocloud_request():
    return {
        'request_id': '2222',
        'body': {
            'filter': {'mettel.velocloud.net': []},
        }
    }


@pytest.fixture(scope='function')
def instance_velocloud_response():
    return {
        'request_id': '2222',
        'body': [
            {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 1},
            {'host': 'some-host', 'enterprise_id': 1, 'edge_id': 2},
        ],
        'status': 200,
    }


@pytest.fixture(scope='function')
def instance_get_customer(instance_storage_repository, mock_logger, mock_event_bus, instance_cache_edges):
    mock_event_bus.publish_message = CoroutineMock()
    instance_storage_repository.get_cache = Mock(return_value=instance_cache_edges)
    return GetCustomers(config, mock_logger, instance_storage_repository, mock_event_bus)


@pytest.fixture(scope='function')
def instance_cache_edges_with_last_contact(instance_cache_edges):
    instance_cache_edges[0]["last_contact"] = str(datetime.now() - timedelta(days=6))
    instance_cache_edges[1]["last_contact"] = str(datetime.now() - timedelta(days=8))
    return instance_cache_edges


@pytest.fixture(scope='function')
def instance_get_customer_with_last_contact(instance_storage_repository, mock_logger, mock_event_bus,
                                            instance_cache_edges_with_last_contact):
    mock_event_bus.publish_message = CoroutineMock()
    instance_storage_repository.get_cache = Mock(return_value=instance_cache_edges_with_last_contact)
    return GetCustomers(config, mock_logger, instance_storage_repository, mock_event_bus)


@pytest.fixture(scope='function')
def instance_get_customer_with_empty_cache(instance_storage_repository, mock_logger, mock_event_bus):
    mock_event_bus.publish_message = CoroutineMock()
    instance_storage_repository.get_cache = Mock(return_value=[])
    return GetCustomers(config, mock_logger, instance_storage_repository, mock_event_bus)
