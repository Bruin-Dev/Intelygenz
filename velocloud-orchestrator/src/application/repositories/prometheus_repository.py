from prometheus_client import start_http_server, Gauge


class PrometheusRepository:

    _config = None
    _edge_gauge = None

    def __init__(self, config):
        self._config = config
        self._edge_gauge = Gauge('edges_processed', 'Edges processed')

    def set_cycle_total_edges(self, sum):
        self._edge_gauge.set(sum)

    def reset_edges_counter(self):
        self._edge_gauge.set(0)

    def start_prometheus_metrics_server(self):
        start_http_server(self._config.GRAFANA_CONFIG['port'])
