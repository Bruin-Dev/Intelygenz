## Unpause ticket task for Ixia device

```python
logger.info(f"Unpausing detail of ticket {ticket_id} related to serial number {service_number}...")
```

* If there's an error while asking for the data to the `bruin-bridge`:
  ```python
  err_msg = (
      f"An error occurred when unpausing detail of ticket {ticket_id} related to serial number "
      f"{service_number}. Error: {e}"
  ) 
  [...]
  logger.error(err_msg)
  ```
  END

* If response status for unpause ticket task is ok:
  ```python
  logger.info(f"Detail of ticket {ticket_id} related to serial number {service_number}) was unpaused!")
  ```
* Otherwise:
  ```python
  err_msg = (
      f"Error while unpausing detail of ticket {ticket_id} related to serial number {service_number}) in "
      f"{self._config.ENVIRONMENT_NAME.upper()} environment. "
      f"Error: Error {response_status} - {response_body}"
  )
  [...]
  logger.error(err_msg)
  ```