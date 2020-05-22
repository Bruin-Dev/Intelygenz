from prometheus_client import Counter


class TriageMetricsRepository:  # pragma: no cover
    _tickets_with_triage_processed = Counter('tickets_with_triage_counter', 'Tickets with triage processed')
    _tickets_without_triage_processed = Counter('tickets_without_triage_counter', 'Tickets without triage processed')
    _notes_appended = Counter('triage_note_counter', 'Triage notes appended')
    _open_tickets_errors = Counter('open_ticket_error_counter', 'Errors while getting open tickets')
    _note_append_errors = Counter('triage_error_note_counter', 'Errors while appending triage notes')
    _monitoring_map_errors = Counter('monitor_map_error_counter', 'Errors in monitor map')

    def increment_tickets_with_triage_processed(self):
        self._tickets_with_triage_processed.inc()

    def increment_tickets_without_triage_processed(self):
        self._tickets_without_triage_processed.inc()

    def increment_notes_appended(self):
        self._notes_appended.inc()

    def increment_open_tickets_errors(self):
        self._open_tickets_errors.inc()

    def increment_note_append_errors(self):
        self._note_append_errors.inc()

    def increment_monitoring_map_errors(self):
        self._monitoring_map_errors.inc()
