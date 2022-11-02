## Subject: rta.prediction.request

_Message arrives at subject_

* If message doesn't have a body or doesn't have `email_id` in body:
  ```python
  logger.error(f"Cannot get inference using {json.dumps(payload)}. JSON malformed")
  ```
  END

[get_email_inference](../repositories/repair_ticket_repository/get_email_inference.md)

```python
logger.info(f"Inference for email {email_id} published in event bus!")
```
