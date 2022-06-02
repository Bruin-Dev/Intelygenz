from prometheus_client import Counter

COMMON_LABELS = ['feature', 'system', 'topic', 'client', 'host', 'outage_type', 'severity']
CREATE_LABELS = ['has_digi', 'has_byob', 'link_types']
REOPEN_LABELS = ['has_digi', 'has_byob', 'link_types']
FORWARD_LABELS = ['has_digi', 'has_byob', 'link_types', 'target_queue']
AUTORESOLVE_LABELS = []


class MetricsRepository:
    _tasks_created = Counter('tasks_created', 'Tasks created', COMMON_LABELS + CREATE_LABELS)
    _tasks_reopened = Counter('tasks_reopened', 'Tasks reopened', COMMON_LABELS + REOPEN_LABELS)
    _tasks_forwarded = Counter('tasks_forwarded', 'Tasks forwarded', COMMON_LABELS + FORWARD_LABELS)
    _tasks_autoresolved = Counter('tasks_autoresolved', 'Tasks autoresolved', COMMON_LABELS + AUTORESOLVE_LABELS)

    def __init__(self, config):
        self._config = config

        self._STATIC_LABELS = {
            'feature': 'Service Outage Monitor',
            'system': 'VeloCloud',
            'topic': 'VOO',
            'host': self._config.VELOCLOUD_HOST,
        }

    def _get_client_label(self, client):
        relevant_clients = self._config.METRICS_RELEVANT_CLIENTS

        if client.startswith('FIS-'):
            return 'FIS'
        elif client in relevant_clients:
            return client
        else:
            return 'Other'

    @staticmethod
    def _get_link_types_label(link_types):
        if not link_types:
            return None
        elif len(link_types) == 1:
            return link_types[0].title()
        else:
            return 'Both'

    def increment_tasks_created(self, client, link_types, **labels):
        client = self._get_client_label(client)
        link_types = self._get_link_types_label(link_types)
        labels = {'client': client, 'link_types': link_types, **labels, **self._STATIC_LABELS}
        self._tasks_created.labels(**labels).inc()

    def increment_tasks_reopened(self, client, link_types, **labels):
        client = self._get_client_label(client)
        link_types = self._get_link_types_label(link_types)
        labels = {'client': client, 'link_types': link_types, **labels, **self._STATIC_LABELS}
        self._tasks_reopened.labels(**labels).inc()

    def increment_tasks_forwarded(self, client, link_types, **labels):
        client = self._get_client_label(client)
        link_types = self._get_link_types_label(link_types)
        labels = {'client': client, 'link_types': link_types, **labels, **self._STATIC_LABELS}
        self._tasks_forwarded.labels(**labels).inc()

    def increment_tasks_autoresolved(self, client, **labels):
        client = self._get_client_label(client)
        labels = {'client': client, **labels, **self._STATIC_LABELS}
        self._tasks_autoresolved.labels(**labels).inc()
