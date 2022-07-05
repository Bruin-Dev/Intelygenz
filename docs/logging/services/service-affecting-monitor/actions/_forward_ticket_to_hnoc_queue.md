## Forward ticket to HNOC Documentation

```
self._logger.info(
                f"Checking if ticket_id {ticket_id} for serial {serial_number} is resolved before "
                f"attempting to forward to HNOC..."
            )
```

* [Get ticket details](../repositories/bruin_repository/get_ticket_details.md)

* if ticket_details_response["status"] not in range(200, 300)
  ```
  self._logger.error(
                    f"Getting ticket details of ticket_id: {ticket_id} and serial: {serial_number} "
                    f"from Bruin failed: {ticket_details_response}. "
                    f"Retrying forward to HNOC..."
                )
  ```

* if is_task_resolved
  ```
  self._logger.info(
                    f"Ticket_id: {ticket_id} for serial: {serial_number} is resolved. " f"Skipping forward to HNOC..."
                )
  ```

```
self._logger.info(
                f"Ticket_id: {ticket_id} for serial: {serial_number} is not resolved. " f"Forwarding to HNOC..."
            )
```

* [Change detail work queue to hnoc](../repositories/bruin_repository/change_detail_work_queue_to_hnoc.md)

* if change_work_queue_response["status"] not in range(200, 300)
  ```
  self._logger.error(
                    f"Failed to forward ticket_id: {ticket_id} and "
                    f"serial: {serial_number} to HNOC Investigate due to bruin "
                    f"returning {change_work_queue_response} when attempting to forward to HNOC."
                )
  ```

* if `Exception`
  ```
  self._logger.error(
                f"An error occurred while trying to forward ticket_id {ticket_id} for serial {serial_number} to HNOC"
                f" -> {e}"
            )
  ```
