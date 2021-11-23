from unittest.mock import Mock

import pytest
from asynctest import CoroutineMock

from application.clients.velocloud_client import VelocloudClient
from application.repositories.velocloud_repository import VelocloudRepository
from application.actions.network_enterprise_edge_list import NetworkEnterpriseEdgeList
from tests.fixtures._helpers import wrap_all_methods

from config import testconfig


@pytest.fixture(scope='function')
def logger() -> Mock:
    return Mock()


@pytest.fixture(scope='function')
def event_bus() -> Mock:
    event_bus = Mock()
    event_bus.publish_message = CoroutineMock()
    return event_bus


@pytest.fixture(scope='function')
def scheduler() -> Mock:
    return Mock()


@pytest.fixture(scope='function')
def velocloud_client(logger, scheduler) -> VelocloudClient:
    client = VelocloudClient(testconfig, logger, scheduler)
    wrap_all_methods(client)
    return client


@pytest.fixture(scope='function')
def velocloud_repository(logger) -> VelocloudRepository:
    velocloud_client = Mock()
    return VelocloudRepository(testconfig, logger, velocloud_client)


@pytest.fixture(scope='function')
def network_enterprise_edge_list_action(event_bus, logger) -> NetworkEnterpriseEdgeList:
    velocloud_repository = Mock()
    return NetworkEnterpriseEdgeList(event_bus, logger, velocloud_repository)
