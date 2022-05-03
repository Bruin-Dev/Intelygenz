from prometheus_client import Counter

COMMON_LABELS = ['feature', 'system', 'ticket_type', 'severity', 'client', 'host']
CREATE_LABELS = ['trouble']
REOPEN_LABELS = ['trouble']
FORWARD_LABELS = ['trouble', 'target_queue']
AUTORESOLVE_LABELS = []

STATIC_LABELS = {
    'feature': 'Service Affecting Monitor',
    'system': 'VeloCloud',
    'ticket_type': 'VAS',
    'severity': 3,
}


class MetricsRepository:  # pragma: no cover
    _tasks_created = Counter('tasks_created', 'Tasks created', COMMON_LABELS + CREATE_LABELS)
    _tasks_reopened = Counter('tasks_reopened', 'Tasks reopened', COMMON_LABELS + REOPEN_LABELS)
    _tasks_forwarded = Counter('tasks_forwarded', 'Tasks forwarded', COMMON_LABELS + FORWARD_LABELS)
    _tasks_autoresolved = Counter('tasks_autoresolved', 'Tasks autoresolved', COMMON_LABELS + AUTORESOLVE_LABELS)

    def __init__(self, config):
        self._config = config

    def _get_client_label(self, client):
        relevant_clients = self._config.METRICS_RELEVANT_CLIENTS

        if client.startswith('FIS-'):
            return 'FIS'
        elif client in relevant_clients:
            return client
        else:
            return 'Other'

    def increment_tasks_created(self, client, **labels):
        client = self._get_client_label(client)
        labels = {'client': client, **labels, **STATIC_LABELS}
        self._tasks_created.labels(**labels).inc()

    def increment_tasks_reopened(self, client, **labels):
        client = self._get_client_label(client)
        labels = {'client': client, **labels, **STATIC_LABELS}
        self._tasks_reopened.labels(**labels).inc()

    def increment_tasks_forwarded(self, client, **labels):
        client = self._get_client_label(client)
        labels = {'client': client, **labels, **STATIC_LABELS}
        self._tasks_forwarded.labels(**labels).inc()

    def increment_tasks_autoresolved(self, client, **labels):
        client = self._get_client_label(client)
        labels = {'client': client, **labels, **STATIC_LABELS}
        self._tasks_autoresolved.labels(**labels).inc()
