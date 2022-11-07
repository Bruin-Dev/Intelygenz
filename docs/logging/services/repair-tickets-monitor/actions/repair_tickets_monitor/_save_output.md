## Save output

output_response = [RepairTicketKreRepository:save_outputs](../../repositories/repair_ticket_kre_repository/save_outputs.md)

* if output_response["status"] not equal 200
    ```python
    log.error("email_id=%s Error while saving output %s", output.email_id, output_response)
    ```