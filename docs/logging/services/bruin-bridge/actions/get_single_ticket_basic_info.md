## Subject: bruin.single_ticket.basic.request

_Message arrives at subject_

* If message doesn't have a body:
  ```python
  logger.error(f"Cannot get tickets basic info using {json.dumps(msg)}. JSON malformed")
  ```
  END

* If message body doesn't have `ticket_id`:
  ```python
  logger.error(
                f"Cannot get tickets basic info using {json.dumps(msg)}. Need a TicketId to keep going."
            )
  ```
  END

```python
logger.info(f"Fetching basic info for ticket {ticket_id}")
```

[get_single_ticket_basic_info](../repositories/bruin_repository/get_single_ticket_basic_info.md)

```python
logger.info(f"Publishing ticket data to the event bus...")
```
