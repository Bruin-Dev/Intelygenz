## Append latest trouble as a note to ticket

```python
logger.info(
    f"Appending Service Affecting trouble note to ticket {ticket_id} for {trouble.value} trouble detected in "
    f"interface {interface} of edge {serial_number}..."
)
```

* If a note for the same trouble was already appended in the current documentation cycle:
  ```python
  logger.info(
      f"No Service Affecting trouble note will be appended to ticket {ticket_id} for {trouble.value} trouble "
      f"detected in interface {interface} of edge {serial_number}. A note for this trouble was already "
      f"appended to the ticket after the latest re-open (or ticket creation)"
  )
  ```
  END

[BruinRepository::append_note_to_ticket](../../repositories/bruin_repository/append_note_to_ticket.md)

* If response status for append note to ticket is not ok:
  ```python
  logger.error(
      f"Error while appending latest trouble for edge {serial_number} as a note to ticket {ticket_id}: "
      f"{append_note_response}"
  )
  ```
  END

```python
logger.info(
    f"Service Affecting trouble note for {trouble.value} trouble detected in interface {interface} "
    f"of edge {serial_number} was successfully appended to ticket {ticket_id}!"
)
```