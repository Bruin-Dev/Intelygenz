## Subject: rta.save_outputs.request

_Message arrives at subject_

* If message doesn't have a body:
  ```python
  logger.error(f"Cannot post automation outputs using {json.dumps(payload)}. JSON malformed")
  ```
  END

[save_outputs](../repositories/repair_ticket_repository/save_outputs.md)

```python
logger.info(f'Save outputs response for email {payload["email_id"]} published in event bus!')
```
