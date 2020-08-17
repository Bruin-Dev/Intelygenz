from prometheus_client import Counter
from prometheus_client import Gauge


class OutageMonitoringMetricsRepository:  # pragma: no cover
    _tickets_created = Counter('outage_ticket_counter', 'Tickets created')
    _tickets_autoresolved = Counter('autoresolve_counter', 'Tickets auto-resolved')
    _tickets_reopened = Counter('reopened_counter', 'Tickets reopened')
    _edges_processed = Counter('outage_monitoring_edge_counter', 'Edges processed')
    _retry_errors = Counter('max_retry_error_counter', 'Times that max retries were exceeded')
    _temp_cache_errors = Counter('temp_cache_error_counter', 'Errors adding to temp cache')
    _first_triage_errors = Counter('first_triage_error_counter', 'Errors adding first triage')
    _last_cycle_duration = Gauge('cycle_runtime_gauge', 'How many minutes last cycle took to run')

    def increment_tickets_created(self):
        self._tickets_created.inc()

    def increment_tickets_autoresolved(self):
        self._tickets_autoresolved.inc()

    def increment_tickets_reopened(self):
        self._tickets_reopened.inc()

    def increment_edges_processed(self):
        self._edges_processed.inc()

    def increment_retry_errors(self):
        self._retry_errors.inc()

    def increment_temp_cache_errors(self):
        self._temp_cache_errors.inc()

    def increment_first_triage_errors(self):
        self._first_triage_errors.inc()

    def set_last_cycle_duration(self, minutes: int):
        self._last_cycle_duration.set(minutes)
