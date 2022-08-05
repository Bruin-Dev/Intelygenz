## Subject: alert.request.event.edge

_Message arrives at subject_

* If message doesn't have a body:
  ```python
  logger.error(f"Cannot get edge events with {json.dumps(payload)}. JSON malformed")
  ```
  END

* If message body doesn't have `edge`, `start_date`, or `end_date` filters:
  ```python
  logger.error(
      f'Cannot get edge events with {json.dumps(payload)}. Need parameters "edge", "start_date" and '
      f'"end_date"'
  )
  ```
  END

* If `filter` field is specified in filters to pull specific event types:
  ```python
  logger.info(f"Event types filter {filter_} will be used to get events for edge {edge}")
  ```

* If `limit` field is specified in filters to pull a certain number of events:
  ```python
  logger.info(f"Will fetch up to {limit} events for edge {edge}")
  ```

```python
logger.info(f"Getting events for edge {edge}...")
```

[get_all_edge_events](../repositories/velocloud_repository/get_all_edge_events.md)

```python
logger.info(f"Edge events published for request {json.dumps(payload)}. Message published was {response}")
```
