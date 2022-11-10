## Get ticket details

```python
logger.info(f"Getting details of ticket {ticket_id} from Bruin...")
```

* If there's an error while asking for the data to the `bruin-bridge`:
  ```python
  err_msg = f"An error occurred when requesting ticket details from Bruin API for ticket {ticket_id} -> {e}" 
  [...]
  logger.error(err_msg)
  ```
  END

```python
logger.info(f"Got details of ticket {ticket_id} from Bruin!")
```

* If response status for get Hawkeye's customer cache is not ok, or the cache is still building:
  ```python
  err_msg = (
      f"Error while retrieving details of ticket {ticket_id} in "
      f"{self._config.ENVIRONMENT_NAME.upper()} environment: "
      f"Error {response_status} - {response_body}"
  )
  [...]
  logger.error(err_msg)
  ```
  END