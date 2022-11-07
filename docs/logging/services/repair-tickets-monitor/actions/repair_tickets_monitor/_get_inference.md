## Get inference

prediction_response = [RepairTicketKreRepository:get_email_inference](../../repositories/repair_ticket_kre_repository/get_email_inference.md)

* if prediction_response["status"] != 200
  ```python
  log.info(
                "email_id=%s Error prediction response status code %s %s",
                email.id,
                prediction_response["status"],
                prediction_response["body"],
            )
  ```