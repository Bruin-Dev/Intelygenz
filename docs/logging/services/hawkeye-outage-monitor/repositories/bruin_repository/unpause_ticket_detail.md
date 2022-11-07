## Unpause ticket task for Ixia device

```python
logger.info(f"Unpausing detail {detail_id} (serial {service_number}) of ticket {ticket_id}...")
```

* If there's an error while asking for the data to the `bruin-bridge`:
  ```python
  err_msg = (
      f"An error occurred when unpausing detail {detail_id} (serial {service_number}) of ticket {ticket_id}. "
      f"Error: {e}"
  ) 
  [...]
  logger.error(err_msg)
  ```
  END

* If response status for unpause ticket task is ok:
  ```python
  logger.info(f"Detail {detail_id} (serial {service_number}) of ticket {ticket_id} was unpaused!")
  ```
* Otherwise:
  ```python
  err_msg = (
      f"Error while unpausing detail {detail_id} (serial {service_number}) of ticket {ticket_id} in "
      f"{self._config.ENVIRONMENT_NAME.upper()} environment. "
      f"Error: Error {response_status} - {response_body}"
  )
  [...]
  logger.error(err_msg)
  ```