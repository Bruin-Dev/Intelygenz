## Re-open ticket task for edge

```python
logger.info(f"Reopening task for serial {serial_number} from ticket {ticket_id}...")
```

[BruinRepository::get_ticket_details](../../repositories/bruin_repository/get_ticket_details.md)

* If response status for get ticket details is not ok:
  ```python
  logger.error(
      f"Error while getting details of ticket {ticket_id}: {ticket_details_response}. "
      f"Skipping re-opening ticket task..."
  )
  ```
  END

[BruinRepository::open_ticket](../../repositories/bruin_repository/open_ticket.md)

* If response status for re-open ticket task for edge is ok:
    ```python
    logger.info(f"Task for edge {serial_number} of ticket {ticket_id} re-opened!")
    ```
  
    [_append_triage_note](_append_triage_note.md) (stylized as a Re-Open note)

  * Otherwise:
    ```python
    logger.error(
        f"Error while re-opening task for edge {serial_number} of ticket {ticket_id}: "
        f"{ticket_reopening_response}"
    )
    ```