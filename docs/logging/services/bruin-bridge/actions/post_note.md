## Subject: bruin.ticket.note.append.request

_Message arrives at subject_

* If message body doesn't have `ticket_id` or `note`:
  ```python
  self._logger.error(f"Cannot post a note to ticket using {json.dumps(msg)}. JSON malformed")  
  ```
  END

```python
self._logger.info(f"Putting note in: {ticket_id}...")
```

[post_ticket_note](../repositories/bruin_repository/post_ticket_note.md)

```python
self._logger.info(f"Note successfully posted to ticketID:{ticket_id} ")
```
