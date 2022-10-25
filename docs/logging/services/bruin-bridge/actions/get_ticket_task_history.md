## Subject: bruin.ticket.get.task.history

_Message arrives at subject_

* If message doesn't have a body:
  ```python
  self._logger.error(f"Cannot get ticket task history using {json.dumps(msg)}. JSON malformed")
  ```
  END

* If message body doesn't have `ticket_id`:
  ```python
  self._logger.info(f"Cannot get get ticket task history using {json.dumps(filters)}. Need 'ticket_id'")
  ```
  END

```python
self._logger.info(f"Getting ticket task history with filters: {json.dumps(filters)}")
```

[get_ticket_task_history](../repositories/bruin_repository/get_ticket_task_history.md)

```python
self._logger.info(
            f"get ticket task history published in event bus for request {json.dumps(msg)}. "
            f"Message published was {response}"
        )
```
