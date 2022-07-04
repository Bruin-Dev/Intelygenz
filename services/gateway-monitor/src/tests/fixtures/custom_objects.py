from typing import Optional

import pytest


# Factories
@pytest.fixture(scope="session")
def make_gateway():
    def _inner(*, id: int):
        return {
            "host": "mettel.velocloud.net",
            "id": id,
            "name": f"vcg-test-{id}",
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
    def _inner(*, id: int, **metrics):
        return {
            **make_gateway(id=id),
            "metrics": make_gateway_metrics(**metrics),
        }

    return _inner
