from prometheus_client import start_http_server, Gauge, Counter
import asyncio


class PrometheusRepository:

    _config = None
    _edge_gauge = None
    _edge_status_gauge = None
    _link_status_gauge = None
    _edge_status_counter = None
    _link_status_counter = None

    def __init__(self, config):
        self._config = config
        self._edge_gauge = Gauge('edges_processed', 'Edges processed')
        self._edge_status_gauge = Gauge('edge_state_gauge', 'Edge States',
                                        ['enterprise_name', 'state'])
        self._link_status_gauge = Gauge('link_state_gauge', 'Link States',
                                        ['enterprise_name', 'state'])
        self._edge_status_counter = Counter('edge_state', 'Edge States', ['enterprise_name', 'state'])
        self._link_status_counter = Counter('link_state', 'Link States', ['enterprise_name', 'state'])

    def inc(self, edge_info):
        self._edge_status_counter.labels(state=edge_info["edges"]["edgeState"],
                                         enterprise_name=edge_info["enterprise_name"]).inc()
        self._edge_status_gauge.labels(state=edge_info["edges"]["edgeState"],
                                       enterprise_name=edge_info["enterprise_name"]).inc()
        for links in edge_info["links"]:
            self._link_status_counter.labels(state=links["link"]["state"],
                                             enterprise_name=edge_info["enterprise_name"]).inc()
            self._link_status_gauge.labels(state=links["link"]["state"],
                                           enterprise_name=edge_info["enterprise_name"]).inc()

    def set_cycle_total_edges(self, total):
        self._edge_gauge.set(total)

    def reset_edges_counter(self):
        self._edge_gauge.set(0)

    def reset_counter(self):
        self._edge_status_gauge._metrics.clear()
        self._link_status_gauge._metrics.clear()

    def start_prometheus_metrics_server(self):
        start_http_server(self._config.GRAFANA_CONFIG['port'])
