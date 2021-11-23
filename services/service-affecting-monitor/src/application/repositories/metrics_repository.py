from prometheus_client import Counter


class MetricsRepository:  # pragma: no cover
    _tickets_created = Counter('affecting_ticket_counter', 'Tickets created')
    _tickets_reopened = Counter('reopened_counter', 'Tickets reopened')

    def increment_tickets_created(self):
        self._tickets_created.inc()

    def increment_tickets_reopened(self):
        self._tickets_reopened.inc()
