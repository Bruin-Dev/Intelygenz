from prometheus_client import Counter
from typing import List, Optional

from application import Outages

COMMON_LABELS = ['feature', 'system', 'topic', 'client', 'outage_type', 'severity']
CREATE_LABELS = []
REOPEN_LABELS = []
AUTORESOLVE_LABELS = []


class MetricsRepository:
    _tasks_created = Counter('tasks_created', 'Tasks created', COMMON_LABELS + CREATE_LABELS)
    _tasks_reopened = Counter('tasks_reopened', 'Tasks reopened', COMMON_LABELS + REOPEN_LABELS)
    _tasks_autoresolved = Counter('tasks_autoresolved', 'Tasks autoresolved', COMMON_LABELS + AUTORESOLVE_LABELS)

    def __init__(self, config):
        self._config = config

        self._STATIC_LABELS = {
            'feature': 'Hawkeye Outage Monitor',
            'system': 'Ixia',
            'topic': 'VOO',
            'severity': 2,
        }

    def _get_client_label(self, client: str) -> str:
        relevant_clients = self._config.METRICS_RELEVANT_CLIENTS

        if client.startswith('FIS-'):
            return 'FIS'
        elif client in relevant_clients:
            return client
        else:
            return 'Other'

    @staticmethod
    def _get_outage_type_label(outage_types: List[Outages]) -> Optional[str]:
        if not outage_types:
            return None
        elif len(outage_types) == 1:
            return outage_types[0].value
        else:
            return 'Both'

    def increment_tasks_created(self, client, outage_types, **labels):
        client = self._get_client_label(client)
        outage_type = self._get_outage_type_label(outage_types)
        labels = {'client': client, 'outage_type': outage_type, **labels, **self._STATIC_LABELS}
        self._tasks_created.labels(**labels).inc()

    def increment_tasks_reopened(self, client, outage_types, **labels):
        client = self._get_client_label(client)
        outage_type = self._get_outage_type_label(outage_types)
        labels = {'client': client, 'outage_type': outage_type, **labels, **self._STATIC_LABELS}
        self._tasks_reopened.labels(**labels).inc()

    def increment_tasks_autoresolved(self, client, outage_types, **labels):
        client = self._get_client_label(client)
        outage_type = self._get_outage_type_label(outage_types)
        labels = {'client': client, 'outage_type': outage_type, **labels, **self._STATIC_LABELS}
        self._tasks_autoresolved.labels(**labels).inc()
