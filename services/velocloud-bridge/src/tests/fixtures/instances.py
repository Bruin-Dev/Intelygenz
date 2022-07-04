from unittest.mock import Mock

import pytest
from application.actions.gateway_status_metrics import GatewayStatusMetrics
from application.actions.network_enterprise_edge_list import NetworkEnterpriseEdgeList
from application.actions.network_gateway_list import NetworkGatewayList
from application.clients.velocloud_client import VelocloudClient
from application.repositories.velocloud_repository import VelocloudRepository
from asynctest import CoroutineMock
from config import testconfig
from tests.fixtures._helpers import wrap_all_methods


@pytest.fixture(scope="function")
def logger() -> Mock:
    return Mock()


@pytest.fixture(scope="function")
def event_bus() -> Mock:
    event_bus = Mock()
    event_bus.publish_message = CoroutineMock()
    return event_bus


@pytest.fixture(scope="function")
def scheduler() -> Mock:
    return Mock()


@pytest.fixture(scope="function")
async def velocloud_client(logger, scheduler) -> VelocloudClient:
    instance = VelocloudClient(testconfig, logger, scheduler)
    wrap_all_methods(instance)
    return instance


@pytest.fixture(scope="function")
def velocloud_repository(logger, velocloud_client) -> VelocloudRepository:
    instance = VelocloudRepository(testconfig, logger, velocloud_client)
    wrap_all_methods(instance)
    return instance


@pytest.fixture(scope="function")
def network_enterprise_edge_list_action(event_bus, velocloud_repository, logger) -> NetworkEnterpriseEdgeList:
    instance = NetworkEnterpriseEdgeList(event_bus, velocloud_repository, logger)
    wrap_all_methods(instance)
    return instance


@pytest.fixture(scope="function")
def network_gateway_list_action(event_bus, velocloud_repository, logger) -> NetworkGatewayList:
    instance = NetworkGatewayList(event_bus, velocloud_repository, logger)
    wrap_all_methods(instance)
    return instance


@pytest.fixture(scope="function")
def gateway_status_metrics_action(event_bus, velocloud_repository, logger) -> GatewayStatusMetrics:
    instance = GatewayStatusMetrics(event_bus, velocloud_repository, logger)
    wrap_all_methods(instance)
    return instance
