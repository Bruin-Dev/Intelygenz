## Change severity of ticket

```python
logger.info(f"Changing severity level of ticket {ticket_id} to {severity_level}...")
```

* If there's an error while asking for the data to the `bruin-bridge`:
  ```python
  err_msg = (
      f"An error occurred when changing the severity level of ticket {ticket_id} to {severity_level} -> {e}"
  )
  [...]
  logger.error(err_msg)
  ```
  END

* If response status for change ticket severity is ok:
  ```python
  logger.info(f"Severity level of ticket {ticket_id} successfully changed to {severity_level}!")
  ```
* Otherwise:
  ```python
  err_msg = (
      f"Error while changing severity of ticket {ticket_id} to {severity_level} in "
      f"{self._config.CURRENT_ENVIRONMENT.upper()} environment: "
      f"Error {response_status} - {response_body}"
  )
  [...]
  logger.error(err_msg)
  ```