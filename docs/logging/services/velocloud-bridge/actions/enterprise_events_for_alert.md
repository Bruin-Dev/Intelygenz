## Subject: alert.request.event.enterprise

_Message arrives at subject_

* If message doesn't have a body:
  ```python
  logger.error(f"Cannot get enterprise events with {json.dumps(payload)}. JSON malformed")
  ```
  END

* If message body doesn't have `host`, `enterprise_id` `start_date`, or `end_date` filters:
  ```python
  logger.error(
      f'Cannot get edge events with {json.dumps(payload)}. Need parameters "host", "enterprise_id", '
      f'"start_date" and "end_date"'
  )
  ```
  END

* If `filter` field is specified in filters to pull specific event types:
  ```python
  logger.info(
      f"Event types filter {filter_} will be used to get events for enterprise {enterprise_id} of host {host}"
  )
  ```

* If `limit` field is specified in filters to pull a certain number of events:
  ```python
  logger.info(f"Will fetch up to {limit} events for enterprise {enterprise_id} of host {host}")
  ```

```python
logger.info(f"Getting events for enterprise {enterprise_id} of host {host}...")
```

[get_all_enterprise_events](../repositories/velocloud_repository/get_all_enterprise_events.md)

```python
logger.info(f"Enterprise events published for request {json.dumps(payload)}. Message published was {response}")
```
