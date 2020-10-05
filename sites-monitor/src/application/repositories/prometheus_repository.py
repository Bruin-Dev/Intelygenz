from prometheus_client import start_http_server, Gauge, Counter


class PrometheusRepository:

    def __init__(self, config):
        self._config = config
        self._edge_gauge = Gauge('edges_processed', 'Edges processed')
        self._edge_status_gauge = Gauge('edge_state_gauge', 'Edge States',
                                        ['enterprise_name', 'name', 'state'])
        self._link_status_gauge = Gauge('link_state_gauge', 'Link States',
                                        ['enterprise_name', 'state'])

    def inc(self, edge_info):
        self._edge_status_gauge.labels(
            state=edge_info["edgeState"],
            enterprise_name=edge_info["enterpriseName"],
            name=edge_info["edgeName"]
        ).inc()
        for link in edge_info["links"]:
            self._link_status_gauge.labels(
                state=link["linkState"],
                enterprise_name=edge_info["enterpriseName"]
            ).inc()

    def dec(self, edge_info):
        self._edge_status_gauge.labels(
            state=edge_info["edgeState"],
            enterprise_name=edge_info["enterpriseName"],
            name=edge_info["edgeName"]
        ).dec()
        for link in edge_info["links"]:
            self._link_status_gauge.labels(
                state=link["linkState"],
                enterprise_name=edge_info["enterpriseName"]
            ).dec()

    def update_edge(self, edge_info, cache_data):
        self._edge_status_gauge.labels(
            state=edge_info["edgeState"],
            enterprise_name=edge_info["enterpriseName"],
            name=edge_info["edgeName"]
        ).inc()
        self._edge_status_gauge.labels(
            state=cache_data["edgeState"],
            enterprise_name=cache_data["enterpriseName"],
            name=cache_data["edgeName"]
        ).dec()

    def update_link(self, edge_info, link_info, cache_edge, cache_link):
        self._link_status_gauge.labels(
            state=link_info["linkState"],
            enterprise_name=edge_info["enterpriseName"]
        ).inc()
        self._link_status_gauge.labels(
            state=cache_link["linkState"],
            enterprise_name=cache_edge["enterpriseName"]
        ).dec()

    def set_cycle_total_edges(self, total):
        self._edge_gauge.set(total)

    def reset_edges_counter(self):
        self._edge_gauge.set(0)

    def reset_counter(self):
        self._edge_status_gauge._metrics.clear()
        self._link_status_gauge._metrics.clear()

    def start_prometheus_metrics_server(self):
        start_http_server(self._config.METRICS_SERVER_CONFIG['port'])
