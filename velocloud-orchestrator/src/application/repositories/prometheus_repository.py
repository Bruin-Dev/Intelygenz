from prometheus_client import start_http_server, Gauge, Counter


class PrometheusRepository:

    def __init__(self, config):
        self._config = config
        self._edge_gauge = Gauge('edges_processed', 'Edges processed')
        self._edge_status_gauge = Gauge('edge_state_gauge', 'Edge States',
                                        ['enterprise_name', 'state'])
        self._link_status_gauge = Gauge('link_state_gauge', 'Link States',
                                        ['enterprise_name', 'state'])

    def inc(self, edge_info):
        self._edge_status_gauge.labels(state=edge_info["edges"]["edgeState"],
                                       enterprise_name=edge_info["enterprise_name"]).inc()
        for links in edge_info["links"]:
            self._link_status_gauge.labels(state=links["link"]["state"],
                                           enterprise_name=edge_info["enterprise_name"]).inc()

    def dec(self, edge_info):
        self._edge_status_gauge.labels(state=edge_info["edges"]["edgeState"],
                                       enterprise_name=edge_info["enterprise_name"]).dec()
        for links in edge_info["links"]:
            self._link_status_gauge.labels(state=links["link"]["state"],
                                           enterprise_name=edge_info["enterprise_name"]).dec()

    def update_edge(self, edge_info, redis_data):
        self._edge_status_gauge.labels(state=edge_info["edges"]["edgeState"],
                                       enterprise_name=edge_info["enterprise_name"]).inc()
        self._edge_status_gauge.labels(state=redis_data["edges"]["edgeState"],
                                       enterprise_name=edge_info["enterprise_name"]).dec()

    def update_link(self, edge_info, link_info, redis_edge, redis_link):
        self._link_status_gauge.labels(state=link_info["link"]["state"],
                                       enterprise_name=edge_info["enterprise_name"]).inc()
        self._link_status_gauge.labels(state=redis_link["link"]["state"],
                                       enterprise_name=redis_edge["enterprise_name"]).dec()

    def set_cycle_total_edges(self, total):
        self._edge_gauge.set(total)

    def reset_edges_counter(self):
        self._edge_gauge.set(0)

    def reset_counter(self):
        self._edge_status_gauge._metrics.clear()
        self._link_status_gauge._metrics.clear()

    def start_prometheus_metrics_server(self):
        start_http_server(self._config.GRAFANA_CONFIG['port'])
