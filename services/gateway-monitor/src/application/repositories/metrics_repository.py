from prometheus_client import Counter

COMMON_LABELS = ["feature", "system", "host"]
CREATE_LABELS = []
REOPEN_LABELS = []


class MetricsRepository:
    _tasks_created = Counter("tasks_created", "Tasks created", COMMON_LABELS + CREATE_LABELS)
    _tasks_reopened = Counter("tasks_reopened", "Tasks reopened", COMMON_LABELS + REOPEN_LABELS)

    def __init__(self):
        self._STATIC_LABELS = {
            "feature": "Gateway Monitor",
            "system": "VeloCloud",
        }

    def increment_tasks_created(self, **labels):
        labels = {**labels, **self._STATIC_LABELS}
        self._tasks_created.labels(**labels).inc()

    def increment_tasks_reopened(self, **labels):
        labels = {**labels, **self._STATIC_LABELS}
        self._tasks_reopened.labels(**labels).inc()
