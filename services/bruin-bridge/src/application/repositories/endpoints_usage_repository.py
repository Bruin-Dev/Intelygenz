import re

from prometheus_client import Counter


class EndpointsUsageRepository:  # pragma: no cover
    __counter = Counter(
        name="bruin_api_usage",
        documentation="Track HTTP requests made to Bruin API",
        labelnames=["method", "endpoint_", "response_status"],
    )

    def increment_usage(self, method: str, endpoint: str, response_status: int):
        endpoint = endpoint.rstrip("/")
        endpoint = re.sub(r"\d+", "{id}", endpoint)
        self.__counter.labels(method, endpoint, response_status).inc()
