## Subject: bruin.ticket.details.request

_Message arrives at subject_

* If message body doesn't have `ticket_id`:
  ```python
  logger.error(f"Cannot get ticket_details using {json.dumps(msg)}. JSON malformed")
  ```
  END

```python
logger.info(f"Collecting ticket details for ticket id: {ticket_id}...")
```

[get_ticket_details](../repositories/bruin_repository/get_ticket_details.md)

```python
logger.info(f"Ticket details for ticket id: {ticket_id} sent!")
```
