## Saved closed ticket feedback

response = [BruinRepository:get_status_and_cancellation_reasons](../../repositories/bruin_repository/get_status_and_cancellation_reasons.md)

* if response['status'] not in range 200 and 300:
    ```python
    log.error(f"Error while while getting ticket status for {ticket_id}")
    ```

response = [RepairTicketKreRepository:save_closed_ticket_feedback](../../repositories/repair_ticket_kre_repository/save_closed_ticket_feedback.md)

* if response['status'] not in range 200 and 300:
    ```python
    log.error(f"Error while saving closed ticket feedback for {ticket_id}")
    ```
