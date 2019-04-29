from prometheus_client import start_http_server, Gauge, Counter
import asyncio


class PrometheusRepository:

    _config = None
    _edge_status_gauge = None
    _link_status_gauge = None
    _edge_status_counter = None
    _link_status_counter = None

    def __init__(self, config):
        self._config = config
        self._edge_status_gauge = Gauge('edge_state_gauge', 'Edge States',
                                        ['enterprise_id', 'enterprise_name', 'state'])
        self._link_status_gauge = Gauge('link_state_gauge', 'Link States',
                                        ['enterprise_id', 'enterprise_name', 'state'])
        self._edge_status_counter = Counter('edge_state', 'Edge States', ['enterprise_id', 'enterprise_name', 'state'])
        self._link_status_counter = Counter('link_state', 'Link States', ['enterprise_id', 'enterprise_name', 'state'])

    def inc(self, enterprise_id, enterprise_name, edge_state, link_status):
        self._edge_status_counter.labels(state=edge_state, enterprise_id=enterprise_id,
                                         enterprise_name=enterprise_name).inc()
        self._edge_status_gauge.labels(state=edge_state, enterprise_id=enterprise_id,
                                       enterprise_name=enterprise_name).inc()
        for links in link_status:
            self._link_status_counter.labels(state=links._link._state, enterprise_id=enterprise_id,
                                             enterprise_name=enterprise_name).inc()
            self._link_status_gauge.labels(state=links._link._state, enterprise_id=enterprise_id,
                                           enterprise_name=enterprise_name).inc()

    async def reset_counter(self):
        while True:
            await asyncio.sleep(self._config.GRAFANA_CONFIG['time'])
            print('here')
            self._edge_status_gauge._metrics.clear()
            self._link_status_gauge._metrics.clear()

    def start_server(self):
        start_http_server(self._config.GRAFANA_CONFIG['port'])
