from prometheus_client import start_http_server, Gauge


class PrometheusRepository:

    _config = None
    _edge_gauge = None
    _velocloud_repository = None

    def __init__(self, config, velocloud_repository):
        self._config = config
        self._edge_gauge = Gauge('edges_processed', 'Edges processed')
        self._velocloud_repository = velocloud_repository

    def inc(self):
        sum = self._velocloud_repository.get_edge_count()
        self._edge_gauge.set(sum)

    def reset_counter(self):
        self._edge_gauge.set(0)

    def start_prometheus_metrics_server(self):
        start_http_server(self._config.GRAFANA_CONFIG['port'])
