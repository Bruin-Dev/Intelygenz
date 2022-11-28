## Subject: bruin.ticket.unpause

_Message arrives at subject_

* If message body doesn't have `service_number` or `detail_id`:
  ```python
  logger.error(f"Cannot unpause a ticket using {json.dumps(msg)}. JSON malformed")
  ```
  END

```python
logger.info(
    f"Unpause the ticket for ticket id: {ticket_id}, "
    f"serial number: {serial_number} and detail id: {detail_id}"
)
```

[unpause_ticket](../repositories/bruin_repository/unpause_ticket.md)

```python
logger.info(
    f"Response from unpause: {response} to the ticket with ticket id: {ticket_id}, "
    f"serial number: {serial_number} and detail id {detail_id}"
)
```
