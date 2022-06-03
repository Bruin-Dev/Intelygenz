from prometheus_client import Counter

COMMON_LABELS = ['feature', 'system', 'topic', 'client', 'host', 'severity']
AUTORESOLVE_LABELS = []


class MetricsRepository:
    _tasks_autoresolved = Counter('tasks_autoresolved', 'Tasks autoresolved', COMMON_LABELS + AUTORESOLVE_LABELS)

    def __init__(self, config):
        self._config = config

        self._STATIC_LABELS = {
            'feature': 'TNBA Monitor',
            'system': 'VeloCloud',
            'host': self._config.VELOCLOUD_HOST,
        }

    def _get_client_label(self, client: str) -> str:
        relevant_clients = self._config.METRICS_RELEVANT_CLIENTS

        if client.startswith('FIS-'):
            return 'FIS'
        elif client in relevant_clients:
            return client
        else:
            return 'Other'

    def increment_tasks_autoresolved(self, client, **labels):
        client = self._get_client_label(client)
        labels = {'client': client, **labels, **self._STATIC_LABELS}
        self._tasks_autoresolved.labels(**labels).inc()
