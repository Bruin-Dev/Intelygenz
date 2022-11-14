## Get overview for a specific ticket

```python
logger.info(f"Getting info of ticket {ticket_id}...")
```

* If there's an error while asking for the data to the `bruin-bridge`:
  ```python
  err_msg = f"An error occurred when requesting info of ticket {ticket_id} -> {e}"
  [...]
  logger.error(err_msg)
  ```
  END

* If response status for get overview of ticket is ok:
  ```python
  logger.info(f"Got info of ticket {ticket_id} from Bruin!")
  ```
* Otherwise:
  ```python
  err_msg = (
      f"Error while retrieving info of ticket {ticket_id} in "
      f"{self._config.CURRENT_ENVIRONMENT.upper()} environment: "
      f"Error {response_status} - {response_body}"
  )
  [...]
  logger.error(err_msg)
  ```