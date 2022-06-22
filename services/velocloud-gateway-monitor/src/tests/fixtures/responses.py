from typing import List

import pytest


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
        body = []

        for gateway_id in gateway_ids:
            gateway_status = gateway_status_template.copy()
            gateway_status["id"] = gateway_id
            body.append(gateway_status)
        return body

    return _inner
