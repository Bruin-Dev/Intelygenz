from typing import Optional

import pytest
from application import Troubles


# Factories
@pytest.fixture(scope="session")
def make_gateway():
    def _inner(*, id: int, status: str = "CONNECTED", trouble: Troubles = None):
        return {
            "host": "mettel.velocloud.net",
            "id": id,
            "name": f"vcg-test-{id}",
            "status": status,
            "trouble": trouble,
        }

    return _inner


@pytest.fixture(scope="session")
def make_gateway_metrics():
    def _inner(*, tunnel_count: Optional[dict] = None):
        metrics = {}

        if tunnel_count is not None:
            metrics["tunnelCount"] = tunnel_count

        return metrics

    return _inner


@pytest.fixture(scope="session")
def make_gateway_with_metrics(make_gateway, make_gateway_metrics):
    def _inner(*, id: int, status: str = None, trouble: Troubles = None, **metrics):
        return {
            **make_gateway(id=id, status=status, trouble=trouble),
            "metrics": make_gateway_metrics(**metrics),
        }

    return _inner
