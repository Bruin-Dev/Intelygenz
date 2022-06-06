from prometheus_client import Counter
from typing import List, Optional

from application import AffectingTroubles

COMMON_LABELS = ['feature', 'system', 'topic', 'severity', 'client', 'host', 'trouble', 'has_byob', 'link_types']
CREATE_LABELS = []
REOPEN_LABELS = []
FORWARD_LABELS = ['target_queue']
AUTORESOLVE_LABELS = []


class MetricsRepository:
    _tasks_created = Counter('tasks_created', 'Tasks created', COMMON_LABELS + CREATE_LABELS)
    _tasks_reopened = Counter('tasks_reopened', 'Tasks reopened', COMMON_LABELS + REOPEN_LABELS)
    _tasks_forwarded = Counter('tasks_forwarded', 'Tasks forwarded', COMMON_LABELS + FORWARD_LABELS)
    _tasks_autoresolved = Counter('tasks_autoresolved', 'Tasks autoresolved', COMMON_LABELS + AUTORESOLVE_LABELS)

    def __init__(self, config):
        self._config = config

        self._STATIC_LABELS = {
            'feature': 'Service Affecting Monitor',
            'system': 'VeloCloud',
            'topic': 'VAS',
            'severity': 3,
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

    @staticmethod
    def _get_link_type_label(link_type: Optional[str]) -> Optional[str]:
        if not link_type:
            return None
        else:
            return link_type.capitalize()

    @staticmethod
    def _get_trouble_label(troubles: List[AffectingTroubles]) -> Optional[str]:
        if not troubles:
            return None
        elif len(troubles) == 1:
            return troubles[0].value
        else:
            return 'Multiple'

    def increment_tasks_created(self, client, link_type, **labels):
        client = self._get_client_label(client)
        link_type = self._get_link_type_label(link_type)
        labels = {'client': client, 'link_types': link_type, **labels, **self._STATIC_LABELS}
        self._tasks_created.labels(**labels).inc()

    def increment_tasks_reopened(self, client, link_type, **labels):
        client = self._get_client_label(client)
        link_type = self._get_link_type_label(link_type)
        labels = {'client': client, 'link_types': link_type, **labels, **self._STATIC_LABELS}
        self._tasks_reopened.labels(**labels).inc()

    def increment_tasks_forwarded(self, client, link_type, **labels):
        client = self._get_client_label(client)
        link_type = self._get_link_type_label(link_type)
        labels = {'client': client, 'link_types': link_type, **labels, **self._STATIC_LABELS}
        self._tasks_forwarded.labels(**labels).inc()

    def increment_tasks_autoresolved(self, client, link_type, troubles, **labels):
        client = self._get_client_label(client)
        link_type = self._get_link_type_label(link_type)
        trouble = self._get_trouble_label(troubles)
        labels = {'client': client, 'link_types': link_type, 'trouble': trouble, **labels, **self._STATIC_LABELS}
        self._tasks_autoresolved.labels(**labels).inc()
