## Forward ticket to queue

```python
logger.info(
    f"Checking if ticket_id {ticket_id} for serial {serial_number} is resolved before "
    f"attempting to forward to {target_queue} queue..."
)
```

* While there are retries left to try to forward to the work queue:
  * [change_detail_work_queue](change_detail_work_queue.md)

* If the maximum number of retries was exceeded:
  ```python
  logger.error(
      f"An error occurred while trying to forward ticket_id {ticket_id} for serial {serial_number} to"
      f" {target_queue} queue -> {e}"
  )
  ```