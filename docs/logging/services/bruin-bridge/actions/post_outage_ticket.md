## Subject: bruin.ticket.creation.outage.request

_Message arrives at subject_

* If message body doesn't have `service_number` or `client_id`:
  ```python
  self._logger.error(
                f"Cannot post ticket using payload {json.dumps(msg)}. " 'Need "client_id" and "service_number"'
            )
  ```
  END
* If `client_id` is None or `service_number` is None:
  ```python
  self._logger.error(
                f"Cannot post ticket using payload {json.dumps(msg)}."
                f'"client_id" and "service_number" must have non-null values.'
            )
  ```
```python
self._logger.info(f"Posting outage ticket with payload: {json.dumps(msg)}")
```

[post_outage_ticket](../repositories/bruin_repository/post_outage_ticket.md)

```python
self._logger.info(f"Outage ticket posted using parameters {json.dumps(msg)}")

self._logger.info(f"Outage ticket published in event bus for request {json.dumps(msg)}")
```
