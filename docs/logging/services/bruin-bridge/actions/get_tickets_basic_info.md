## Subject: bruin.ticket.basic.request

_Message arrives at subject_

* If message doesn't have a body:
  ```python
  self._logger.error(f"Cannot get tickets basic info using {json.dumps(msg)}. JSON malformed")
  ```
  END

* If message body doesn't have `ticket_statuses` filter:
  ```python
  self._logger.error(
      f"Cannot get tickets basic info using {json.dumps(msg)}. Need a list of ticket statuses to keep going."
  )
  ```
  END

```python
self._logger.info(
    f'Fetching basic info of all tickets with statuses {", ".join(ticket_statuses)} and matching filters '
    f"{json.dumps(bruin_payload)}..."
)
```

[get_tickets_basic_info](../repositories/bruin_repository/get_tickets_basic_info.md)

```python
self._logger.info(f'Publishing {len(response_msg["body"])} tickets to the event bus...')
```
