from typing import List, Optional

from prometheus_client import Counter

COMMON_LABELS = [
    "feature",
    "system",
    "topic",
    "client",
    "host",
    "outage_type",
    "severity",
    "has_digi",
    "has_byob",
    "link_types",
]
CREATE_LABELS = []
REOPEN_LABELS = []
FORWARD_LABELS = ["target_queue"]
AUTORESOLVE_LABELS = []


class MetricsRepository:
    _tasks_created = Counter("tasks_created", "Tasks created", COMMON_LABELS + CREATE_LABELS)
    _tasks_reopened = Counter("tasks_reopened", "Tasks reopened", COMMON_LABELS + REOPEN_LABELS)
    _tasks_forwarded = Counter("tasks_forwarded", "Tasks forwarded", COMMON_LABELS + FORWARD_LABELS)
    _tasks_autoresolved = Counter("tasks_autoresolved", "Tasks autoresolved", COMMON_LABELS + AUTORESOLVE_LABELS)

    def __init__(self, config):
        self._config = config

        self._STATIC_LABELS = {
            "feature": "Service Outage Monitor",
            "system": "VeloCloud",
            "topic": "VOO",
            "host": self._config.VELOCLOUD_HOST,
        }

    @staticmethod
    def _set_default_label(**labels):
        return {key: value if value is not None else "Unknown" for key, value in labels.items()}

    def _get_client_label(self, client: str) -> str:
        umbrella_clients = self._config.UMBRELLA_HOSTS.values()
        relevant_clients = self._config.METRICS_RELEVANT_CLIENTS

        for umbrella_client in umbrella_clients:
            if client.startswith(umbrella_client):
                return umbrella_client

        if client in relevant_clients:
            return client
        else:
            return "Other"

    @staticmethod
    def _get_link_types_label(link_types: Optional[List[str]]) -> str:
        if link_types is None:
            return "Unknown"
        elif len(link_types) == 0:
            return "None"
        elif len(link_types) == 1:
            return link_types[0].capitalize()
        else:
            return "Both"

    def increment_tasks_created(self, client, link_types, **labels):
        client = self._get_client_label(client)
        link_types = self._get_link_types_label(link_types)
        labels = self._set_default_label(**labels)
        labels = {"client": client, "link_types": link_types, **labels, **self._STATIC_LABELS}
        self._tasks_created.labels(**labels).inc()

    def increment_tasks_reopened(self, client, link_types, **labels):
        client = self._get_client_label(client)
        link_types = self._get_link_types_label(link_types)
        labels = self._set_default_label(**labels)
        labels = {"client": client, "link_types": link_types, **labels, **self._STATIC_LABELS}
        self._tasks_reopened.labels(**labels).inc()

    def increment_tasks_forwarded(self, client, link_types, **labels):
        client = self._get_client_label(client)
        link_types = self._get_link_types_label(link_types)
        labels = self._set_default_label(**labels)
        labels = {"client": client, "link_types": link_types, **labels, **self._STATIC_LABELS}
        self._tasks_forwarded.labels(**labels).inc()

    def increment_tasks_autoresolved(self, client, link_types, **labels):
        client = self._get_client_label(client)
        link_types = self._get_link_types_label(link_types)
        labels = self._set_default_label(**labels)
        labels = {"client": client, "link_types": link_types, **labels, **self._STATIC_LABELS}
        self._tasks_autoresolved.labels(**labels).inc()
