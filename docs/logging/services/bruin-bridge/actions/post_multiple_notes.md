## Subject: bruin.ticket.multiple.notes.append.request

_Message arrives at subject_

* If message doesn't have a body:
  ```python
  logger.error(f"Cannot post a note to ticket using {json.dumps(msg)}. JSON malformed")
  ```
  END

```python
logger.info(f"Posting multiple notes for ticket {ticket_id}...")
```

[post_multiple_ticket_notes](../repositories/bruin_repository/post_multiple_ticket_notes.md)
