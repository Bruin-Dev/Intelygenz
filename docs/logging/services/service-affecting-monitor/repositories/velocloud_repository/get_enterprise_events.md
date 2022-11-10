## Get all edges' events for a specific enterprise in a VeloCloud host (VCO)

```python
logger.info(
    f"Getting events of host {host} and enterprise id {enterprise_id} having any type of {event_types} "
    f"that took place between {past_moment} and {now} from Velocloud..."
)
```

* If there's an error while asking for the data to the `velocloud-bridge`:
  ```python
  err_msg = (
      f"An error occurred when requesting edge events from Velocloud for host {host} "
      f"and enterprise id {enterprise_id} -> {e}"
  ) 
  [...]
  logger.error(err_msg)
  ```
  END

* If response status for get enterprise events is not ok:
  ```python
  err_msg = (
      f"Error while retrieving events of host {host} and enterprise id {enterprise_id} having any type "
      f"in {event_types} that took place between {past_moment} and {now} "
      f"in {self._config.ENVIRONMENT_NAME.upper()}"
      f"environment: Error {response_status} - {response_body}"
  )
  [...]
  logger.error(err_msg)
  ```
  END  

```python
logger.info(
    f"Got events of host {host} and enterprise id {enterprise_id} having any type in {event_types} "
    f"that took place between {past_moment} and {now} from Velocloud!"
)
```