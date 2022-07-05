## Forward_ticket_to_hnoc_queue
```
self._logger.info(f"Checking if ticket_id {ticket_id} for serial {serial_number} is resolved before "
                  f"attempting to forward to HNOC...")
```
* [get_ticket_details](../../repositories/bruin_repository/get_ticket_details.md)
* If ticket details status is not OK
  ```
  self._logger.info(f"Getting ticket details of ticket_id {ticket_id} and serial {serial_number} "
                    f"from Bruin failed: {ticket_details_response}. "
                    f"Retrying forward to HNOC...")
  ```
* If detail is resolved:
  ```
  self._logger.info(f"Ticket id {ticket_id} for serial {serial_number} is resolved. " f"Skipping forward to HNOC...")
  ```
```
self._logger.info(f"Ticket id {ticket_id} for serial {serial_number} is not resolved. " f"Forwarding to HNOC...")
```
* [change_detail_work_queue_to_hnoc](change_detail_work_queue_to_hnoc.md)
* If Exception:
```
self._logger.error(f"An error occurred while trying to forward ticket_id {ticket_id} for serial {serial_number} to HNOC"
                   f" -> {e}")
```