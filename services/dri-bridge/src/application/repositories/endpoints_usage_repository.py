from prometheus_client import Counter


class EndpointsUsageRepository:  # pragma: no cover
    __counter = Counter(
        name="dri_api_usage",
        documentation="Track HTTP requests made to DRI API",
        labelnames=["method", "endpoint_"],
    )

    def increment_usage(self, method: str, endpoint: str):
        endpoint = endpoint.rstrip("/")
        self.__counter.labels(method, endpoint).inc()
