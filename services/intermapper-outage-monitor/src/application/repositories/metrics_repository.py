from prometheus_client import Counter

COMMON_LABELS = ["feature", "system", "topic", "severity", "event", "is_piab"]
CREATE_LABELS = []
REOPEN_LABELS = []
FORWARD_LABELS = ["target_queue"]
AUTORESOLVE_LABELS = []


class MetricsRepository:
    _tasks_created = Counter("tasks_created", "Tasks created", COMMON_LABELS + CREATE_LABELS)
    _tasks_reopened = Counter("tasks_reopened", "Tasks reopened", COMMON_LABELS + REOPEN_LABELS)
    _tasks_forwarded = Counter("tasks_forwarded", "Tasks forwarded", COMMON_LABELS + FORWARD_LABELS)
    _tasks_autoresolved = Counter("tasks_autoresolved", "Tasks autoresolved", COMMON_LABELS + AUTORESOLVE_LABELS)

    def __init__(self):
        self._STATIC_LABELS = {
            "feature": "InterMapper Outage Monitor",
            "system": "InterMapper",
            "topic": "VOO",
            "severity": 2,
        }

    def increment_tasks_created(self, **labels):
        labels = {**labels, **self._STATIC_LABELS}
        self._tasks_created.labels(**labels).inc()

    def increment_tasks_reopened(self, **labels):
        labels = {**labels, **self._STATIC_LABELS}
        self._tasks_reopened.labels(**labels).inc()

    def increment_tasks_forwarded(self, **labels):
        labels = {**labels, **self._STATIC_LABELS}
        self._tasks_forwarded.labels(**labels).inc()

    def increment_tasks_autoresolved(self, **labels):
        labels = {**labels, **self._STATIC_LABELS}
        self._tasks_autoresolved.labels(**labels).inc()
