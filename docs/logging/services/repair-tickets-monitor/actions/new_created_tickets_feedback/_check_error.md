## Check error

* if error_code is 404
  error_counter = [NewCreatedTicketsRepository:increase_ticket_error_counter](../../repositories/new_created_tickets_repository/increase_ticket_error_counter.md)
  * if error_counter exceeds threshold of `MONITOR_CONFIG`'s field `max_retries_error_404`
    [NewCreatedTicketsRepository:delete_ticket_error_counter](../../repositories/new_created_tickets_repository/delete_ticket_error_counter.md)