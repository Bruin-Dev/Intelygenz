## Append triage note to ticket if there's not one already

```python
logger.info(f"Checking ticket {ticket_id} to see if device {serial_number} has a triage note already...")
```

[BruinRepository::get_ticket_details](../../repositories/bruin_repository/get_ticket_details.md)

* If response status for get ticket details is not ok:
  ```python
  logger.error(
      f"Error while getting details of ticket {ticket_id}: {ticket_details_response}. "
      f"Skipping append triage note..."
  )
  ```
  END

* If there is a Triage note appended to the ticket task linked to the Ixia device:
  ```python
  logger.info(
      f"Triage note already exists in ticket {ticket_id} for serial {serial_number}, so no triage "
      f"note will be appended."
  )
  ```
  END

```python
logger.info(
    f"No triage note was found for serial {serial_number} in ticket {ticket_id}. Appending triage note..."
)
```

[BruinRepository::append_triage_note_to_ticket](../../repositories/bruin_repository/append_triage_note_to_ticket.md)

```python
logger.info(f"Triage note for device {serial_number} appended to ticket {ticket_id}!")
```