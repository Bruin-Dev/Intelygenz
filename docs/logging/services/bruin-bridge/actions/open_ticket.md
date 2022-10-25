## Subject: bruin.ticket.status.open

_Message arrives at subject_

* If message body doesn't have `ticket_id` or `detail_id`:
  ```python
  self._logger.error(f"Cannot open a ticket using {json.dumps(msg)}. JSON malformed")
  ```
  END

```python
self._logger.info(f"Updating the ticket status for ticket id: {ticket_id} to OPEN")
```

[open_ticket](../repositories/bruin_repository/open_ticket.md)
