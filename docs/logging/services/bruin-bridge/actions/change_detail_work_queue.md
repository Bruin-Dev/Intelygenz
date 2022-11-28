## Subject: bruin.ticket.change.work

_Message arrives at subject_

* If message doesn't have a body:
  ```python
  logger.error(f"Cannot change detail work queue using {json.dumps(msg)}. JSON malformed")
  ```
  END

* If message body doesn't have `ticket_id`, `queue_name` or doesn't have `service_number` or `detail_id`:
  ```python
  logger.error(
      f"Cannot change detail work queue using {json.dumps(msg_body)}. "
      f'Need all these parameters: "service_number" or "detail_id", "ticket_id", "queue_name"'
  )
  ```
  END

```python
logger.info(f"Changing work queue of ticket {ticket_id} with filters: {json.dumps(msg_body)}")
```

[change_detail_work_queue](../repositories/bruin_repository/change_detail_work_queue.md)

```python
logger.info(
    f"Result of changing work queue of ticket {ticket_id} with filters {json.dumps(msg_body)} "
    "published in event bus!"
)
```
