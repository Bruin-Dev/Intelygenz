## Get tickets

```python
self._logger.info(f"Getting all tickets of ticket id {ticket_id} from Bruin...")
```

* If there's an error while asking for the data to the `bruin-bridge`:
  ```python
  err_msg = f"An error occurred when requesting all tickets of ticket id {ticket_id} from Bruin API -> {e}"
  [...]
  self._logger.error(err_msg)
  ```
  END

* If response status for get tickets is not ok:
  ```python
  err_msg = (
      f"Error while retrieving all tickets of ticket id {ticket_id} in "
      f"{self._config.ENVIRONMENT_NAME.upper()} environment: "
      f"Error {response_status} - {response_body}"
  )
  [...]
  self._logger.error(err_msg)
  ```
* Otherwise:
  ```python
  self._logger.info(f"Got all tickets of ticket id {ticket_id} from Bruin")
  ```