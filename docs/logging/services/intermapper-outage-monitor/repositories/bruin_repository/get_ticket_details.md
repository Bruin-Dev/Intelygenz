## Get ticket details

```python
self._logger.info(f"Getting details of ticket {ticket_id} from Bruin...")
```

* If there's an error while asking for the data to the `bruin-bridge`:
  ```python
  err_msg = f"An error occurred when requesting ticket details from Bruin API for ticket {ticket_id} -> {e}" 
  [...]
  self._logger.error(err_msg)
  ```
  END

```python
self._logger.info(f"Got details of ticket {ticket_id} from Bruin!")
```

* If response status for get ticket details is not ok:
  ```python
  err_msg = (
      f"Error while retrieving details of ticket {ticket_id} in "
      f"{self._config.ENVIRONMENT_NAME.upper()} environment: "
      f"Error {response_status} - {response_body}"
  )
  [...]
  self._logger.error(err_msg)
  ```