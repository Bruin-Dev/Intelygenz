from typing import List, Optional

from application import AffectingTroubles
from prometheus_client import Counter

COMMON_LABELS = ["feature", "system", "topic", "severity", "client", "host", "trouble", "has_byob", "link_types"]
CREATE_LABELS = []
REOPEN_LABELS = []
FORWARD_LABELS = ["target_queue"]
AUTORESOLVE_LABELS = []


class MetricsRepository:
    _tasks_created = Counter("tasks_created", "Tasks created", COMMON_LABELS + CREATE_LABELS)
    _tasks_reopened = Counter("tasks_reopened", "Tasks reopened", COMMON_LABELS + REOPEN_LABELS)
    _tasks_forwarded = Counter("tasks_forwarded", "Tasks forwarded", COMMON_LABELS + FORWARD_LABELS)
    _tasks_autoresolved = Counter("tasks_autoresolved", "Tasks autoresolved", COMMON_LABELS + AUTORESOLVE_LABELS)
    _reports_signet_execution_OK = Counter("reports_signet_execution_OK", "Successfully sent bandwidth reports")
    _reports_signet_execution_KO = Counter("reports_signet_execution_KO", "Failed to send bandwidth reports")

    def __init__(self, config):
        self._config = config

        self._STATIC_LABELS = {
            "feature": "Service Affecting Monitor",
            "system": "VeloCloud",
            "topic": "VAS",
            "severity": 3,
            "host": self._config.VELOCLOUD_HOST,
        }

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
    def _get_link_type_label(link_type: Optional[str]) -> str:
        if not link_type:
            return "Unknown"
        else:
            return link_type.capitalize()

    @staticmethod
    def _get_trouble_label(troubles: List[AffectingTroubles]) -> str:
        if not troubles:
            return "Unknown"
        elif len(troubles) == 1:
            return troubles[0].value
        else:
            return "Multiple"

    def increment_tasks_created(self, client, link_type, **labels):
        client = self._get_client_label(client)
        link_type = self._get_link_type_label(link_type)
        labels = {"client": client, "link_types": link_type, **labels, **self._STATIC_LABELS}
        self._tasks_created.labels(**labels).inc()

    def increment_tasks_reopened(self, client, link_type, **labels):
        client = self._get_client_label(client)
        link_type = self._get_link_type_label(link_type)
        labels = {"client": client, "link_types": link_type, **labels, **self._STATIC_LABELS}
        self._tasks_reopened.labels(**labels).inc()

    def increment_tasks_forwarded(self, client, link_type, **labels):
        client = self._get_client_label(client)
        link_type = self._get_link_type_label(link_type)
        labels = {"client": client, "link_types": link_type, **labels, **self._STATIC_LABELS}
        self._tasks_forwarded.labels(**labels).inc()

    def increment_tasks_autoresolved(self, client, link_type, troubles, **labels):
        client = self._get_client_label(client)
        link_type = self._get_link_type_label(link_type)
        trouble = self._get_trouble_label(troubles)
        labels = {"client": client, "link_types": link_type, "trouble": trouble, **labels, **self._STATIC_LABELS}
        self._tasks_autoresolved.labels(**labels).inc()

    def increment_reports_signet_execution_OK(self):
        self._reports_signet_execution_OK.inc()

    def increment_reports_signet_execution_KO(self):
        self._reports_signet_execution_KO.inc()
