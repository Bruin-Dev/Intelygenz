## Subject: bruin.change.ticket.severity

_Message arrives at subject_

* If message doesn't have a body:
  ```python
  self._logger.error(f"Cannot change ticket severity level using {json.dumps(msg)}. JSON malformed")
  ```
  END

* If message body doesn't have `ticket_id`, `severity` and `reason` filters:
  ```python
  self._logger.error(
      f"Cannot change ticket severity level using {json.dumps(msg)}. "
      'Need fields "ticket_id", "severity" and "reason".'
  )
  ```
  END

```python
self._logger.info(f"Changing ticket severity level using parameters {json.dumps(payload)}...")
```

[change_ticket_severity](../repositories/bruin_repository/change_ticket_severity.md)

```python
self._logger.info(
    f"Publishing result of changing severity level of ticket {ticket_id} using payload {json.dumps(payload)} "
    "to the event bus..."
)
```
