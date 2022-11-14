## Append Triage note to ticket

```python
logger.info(f"Appending Triage note to ticket {ticket_id} for edge {serial_number}...")
```

[VelocloudRepository::get_last_edge_events](../../repositories/velocloud_repository/get_last_edge_events.md)

* If response status for get last edge events is not ok:
  ```python
  logger.error(
      f"Error while getting last events for edge {serial_number}: {recent_events_response}. "
      f"Skipping append Triage note..."
  )
  ```
  END

[BruinRepository::get_ticket_details](../../repositories/bruin_repository/get_ticket_details.md)

* If response status for get ticket details is not ok:
  ```python
  logger.error(
      f"Error while getting details of ticket {ticket_id}: {ticket_details_response}. "
      f"Skipping append Triage note..."
  )
  ```
  END

[BruinRepository::append_triage_note](../../repositories/bruin_repository/append_triage_note.md)

```python
logger.info(f"Triage note appended to ticket {ticket_id} for edge {serial_number}")
```