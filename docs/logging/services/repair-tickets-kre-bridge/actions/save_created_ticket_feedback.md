## Subject: rta.created_ticket_feedback.request

_Message arrives at subject_

* If message doesn't have a body or doesn't have `ticket_id` in body:
  ```python
  logger.error(f"Error cannot save feedback for ticket: {ticket_id}. error JSON malformed")
  ```
  END

[save_created_ticket_feedback](../repositories/repair_ticket_repository/save_created_ticket_feedback.md)

```python
logger.info(f"Save created tickets result for ticket {ticket_id} published in event bus!")
```
