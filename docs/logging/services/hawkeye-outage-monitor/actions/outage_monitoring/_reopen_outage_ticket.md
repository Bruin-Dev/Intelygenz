## Re-open task from Service Outage ticket

```python
logger.info(f"Reopening task from ticket {ticket_id} for device {device['cached_info']['serial_number']}...")
```

[BruinRepository::get_ticket_details](../../repositories/bruin_repository/get_ticket_details.md)

* If response status for get ticket details is not ok:
  ```python
  logger.error(
      f"Error while getting details of ticket {ticket_id}: {ticket_details_response}. "
      f"Skipping task re-open..."
  )
  ```
  END

[BruinRepository::open_ticket](../../repositories/bruin_repository/open_ticket.md)

* If response status for re-opening ticket task is ok:
  ```python
  logger.info(f"Task from ticket {ticket_id} for device {device['cached_info']['serial_number']} re-opened!")
  ```
  _[BruinRepository::append_note_to_ticket](../../repositories/bruin_repository/append_note_to_ticket.md) is called to append a Re-Open note_
* Otherwise:
  ```python
  logger.error(
      f"Re-open failed for task from ticket {ticket_id} for device {device['cached_info']['serial_number']}"
  )
  ```