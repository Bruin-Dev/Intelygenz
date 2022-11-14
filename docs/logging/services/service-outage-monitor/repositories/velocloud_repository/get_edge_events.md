## Get events for edge

```python
logger.info(
    f"Getting events of edge {json.dumps(edge_full_id)} having any type of {event_types} that took place "
    f"between {from_} and {to} from Velocloud..."
)
```

* If there's an error while asking for the data to the `velocloud-bridge`:
  ```python
  err_msg = (
      f"An error occurred when requesting edge events from Velocloud for edge "
      f"{json.dumps(edge_full_id)} -> {e}"
  )
  [...]
  logger.error(err_msg)
  ```
  END

```python
logger.info(
    f"Got events of edge {json.dumps(edge_full_id)} having any type in {event_types} that took place "
    f"between {from_} and {to} from Velocloud!"
)
```

* If response status for get edge events is not ok:
  ```python
  err_msg = (
      f"Error while retrieving events of edge {json.dumps(edge_full_id)} having any type in "
      f"{event_types} that took place between {from_} and {to} in "
      f"{self._config.CURRENT_ENVIRONMENT.upper()} environment: "
      f"Error {response_status} - {response_body}"
  )
  [...]
  logger.error(err_msg)
  ```