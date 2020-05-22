from prometheus_client import Counter


class MetricsRepository:  # pragma: no cover
    _tickets_created = Counter('affecting_ticket_counter', 'Affecting tickets created')

    def increment_tickets_created(self):
        self._tickets_created.inc()
