## Remove job for autoresolved task

* If there is a job scheduled for the work queue:
  ```python
  logger.info(
      f"Found job to forward to {target_queue} scheduled for autoresolved ticket {ticket_id}"
      f" related to serial number {serial_number}! Removing..."
  )
  ```