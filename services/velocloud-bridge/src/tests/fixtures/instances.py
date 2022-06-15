from unittest.mock import AsyncMock, Mock

import pytest

from ...application.actions.gateway_status_metrics import GatewayStatusMetrics
from ...application.actions.network_enterprise_edge_list import NetworkEnterpriseEdgeList
from ...application.actions.network_gateway_list import NetworkGatewayList
from ...application.clients.velocloud_client import VelocloudClient
from ...application.repositories.velocloud_repository import VelocloudRepository
from ...config import testconfig
from ._helpers import wrap_all_methods


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
