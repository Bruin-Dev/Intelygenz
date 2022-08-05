# Get all events

* If event types filter is defined:
  ```python
  logger.info(f"Using event type filter {filter_events_status_list} to get all events from host {host}")
  ```

```python
logger.info(f"Getting all events from host {host} using filters {body}")
```

[get_all_events](../../clients/velocloud_client/get_all_events.md)

* If response status for get all events is not ok:
  ```python
  logger.error(f"Could not get all events from {host} using filters {body}. Response: {response}")
  ```