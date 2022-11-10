## Change detail work queue

```python
logger.info(
    f"Changing work queue for ticket {ticket_id}, detail {detail_id} and serial number {serial_number} "
    f"to the {target_queue} queue..."
)
```

* If Exception:
  ```python
  err_msg = (
     f"An error occurred when changing work queue for ticket {ticket_id}, detail {detail_id} "
     f"and serial number {serial_number} -> {e}"
  )
  logger.error(err_msg)
  ```
  END
  
* If status ok:
  ```python
  success_msg = (
     f"Work queue changed for ticket {ticket_id}, detail {detail_id} and serial number {serial_number} "
     f"to the {target_queue} queue successfully!"
  )
  logger.info(success_msg)
  ```
* Else:
  ```python
  err_msg = (
     f"Error while changing work queue for ticket {ticket_id}, detail {detail_id} "
     f"and serial number {serial_number} to the {target_queue} queue in "
     f"{self._config.CURRENT_ENVIRONMENT.upper()} environment: "
     f"Error {response_status} - {response_body}"
  )
  logger.error(err_msg)
  ```