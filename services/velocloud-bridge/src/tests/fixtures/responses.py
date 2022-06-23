from typing import Any, List
from unittest.mock import Mock

import pytest
from asynctest import CoroutineMock


@pytest.fixture(scope="session")
def make_http_response():
    response = Mock()

    def _inner(*, status: int, body: Any) -> Mock:
        response.status = status
        response.json = CoroutineMock(return_value=body)
        return response

    return _inner


@pytest.fixture(scope="session")
def make_error_body():
    def _inner(*, error_code: int, message: str):
        body = {
            "error": {
                "code": error_code,
                "message": message,
            }
        }
        return body

    return _inner


@pytest.fixture(scope="session")
def make_error_response(make_error_body, make_http_response):
    def _inner(*, status: int, error_code: int, message: str):
        body = make_error_body(error_code=error_code, message=message)
        return make_http_response(status=status, body=body)

    return _inner


@pytest.fixture(scope="session")
def make_network_enterprises_edges():
    def _inner(*, enterprise_id: int, n_edges: int):
        edge_list = []
        edge_template = {
            "activationKey": "string",
            "activationKeyExpires": "string",
            "activationState": "UNASSIGNED",
            "activationTime": "string",
            "alertsEnabled": 0,
            "buildNumber": "string",
            "created": "string",
            "customInfo": "string",
            "description": "string",
            "deviceFamily": "string",
            "deviceId": "string",
            "dnsName": "string",
            "edgeState": "NEVER_ACTIVATED",
            "edgeStateTime": "string",
            "endpointPkiMode": "CERTIFICATE_DISABLED",
            "enterpriseId": enterprise_id,
            "factorySoftwareVersion": "string",
            "factoryBuildNumber": "string",
            "haLastContact": "string",
            "haPreviousState": "UNCONFIGURED",
            "haSerialNumber": "string",
            "haState": "UNCONFIGURED",
            "id": 0,
            "isLive": 0,
            "lastContact": "string",
            "logicalId": "string",
            "modelNumber": "string",
            "modified": "string",
            "name": "string",
            "operatorAlertsEnabled": 0,
            "selfMacAddress": "string",
            "serialNumber": "string",
            "serviceState": "IN_SERVICE",
            "serviceUpSince": "string",
            "siteId": 0,
            "softwareUpdated": "string",
            "softwareVersion": "string",
            "systemUpSince": "string",
        }
        edge_list.extend([edge_template for _ in range(n_edges)])
        return edge_list

    return _inner


@pytest.fixture(scope="session")
def make_network_enterprises_body(make_network_enterprises_edges):
    def _inner(*, enterprise_ids: List[int] = None, n_edges: int = 1):
        enterprise_ids = [1] if enterprise_ids is None else enterprise_ids
        enterprise_template = {
            "id": 0,
            "created": "2021-09-23T13:30:23.944Z",
            "networkId": 0,
            "gatewayPoolId": 0,
            "alertsEnabled": 0,
            "operatorAlertsEnabled": 0,
            "endpointPkiMode": "CERTIFICATE_DISABLED",
            "name": "string",
            "domain": "string",
            "prefix": "string",
            "logicalId": "string",
            "accountNumber": "string",
            "description": "string",
            "contactName": "string",
            "contactPhone": "string",
            "contactMobile": "string",
            "contactEmail": "string",
            "streetAddress": "string",
            "streetAddress2": "string",
            "city": "string",
            "state": "string",
            "postalCode": "string",
            "country": "string",
            "lat": 0,
            "lon": 0,
            "timezone": "string",
            "locale": "string",
            "modified": "2021-09-23T13:30:23.944Z",
            "enterpriseProxyId": 0,
            "enterpriseProxyName": "string",
            "edgeCount": 0,
            "edges": [],
        }
        body = []
        for enterprise_id in enterprise_ids:
            edges = make_network_enterprises_edges(enterprise_id=enterprise_id, n_edges=n_edges)
            enterprise = enterprise_template.copy()
            enterprise["id"] = enterprise_id
            enterprise["edges"] = edges
            body.append(enterprise)

        return body

    return _inner


@pytest.fixture(scope="session")
def make_network_gateway_status_body():
    def _inner(
        *,
        gateway_ids: List[int] = None,
    ):
        gateway_ids = [1] if gateway_ids is None else gateway_ids
        gateway_status_template = {
            "gatewayId": 0,
            "tunnelCount": 0,
            "tunnelCountV6": 0,
            "memoryPct": 0,
            "flowCount": 0,
            "cpuPct": 0,
            "handoffQueueDrops": 0,
            "connectedEdges": 0,
        }
        body = {"metaData": {"limit": 0, "more": True}, "data": []}

        for gateway_id in gateway_ids:
            gateway_status = gateway_status_template.copy()
            gateway_status["id"] = gateway_id
            body["data"].append(gateway_status)
        return body

    return _inner
