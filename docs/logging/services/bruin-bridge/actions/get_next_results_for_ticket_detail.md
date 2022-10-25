## Subject: bruin.ticket.detail.get.next.results

_Message arrives at subject_

* If message doesn't have a body:
  ```python
  self._logger.error(f"Cannot get next results for ticket detail using {json.dumps(msg)}. JSON malformed")
  ```
  END

* If message body doesn't have `ticket_id`, `detail_id`, or `service_number`:
  ```python
  self._logger.info(
                f"Cannot get next results for ticket detail using {json.dumps(request_body)}. "
                f'Need "ticket_id", "detail_id", "service_number"'
            )
  ```
  END

```python
self._logger.info(f"Claiming all available next results for ticket {ticket_id} and detail {detail_id}...")
```

[get_next_results_for_ticket_detail](../repositories/bruin_repository/get_next_results_for_ticket_detail.md)

```python
self._logger.info(f"Next results for ticket {ticket_id} and detail {detail_id} published in event bus!")
```
