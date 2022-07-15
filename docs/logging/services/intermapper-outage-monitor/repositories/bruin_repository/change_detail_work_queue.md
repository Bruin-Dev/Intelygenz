## Change detail work queue

```python
self._logger.info(
    f"Changing task result for ticket {ticket_id} for device {serial_number} to {task_result}..."
)
```

* If there's an error while posting the data to the `bruin-bridge`:
  ```python
  err_msg = f"An error occurred when changing task result for ticket {ticket_id} and serial {serial_number}"
  [...]
  self._logger.error(err_msg)
  ```
  END

* If response status for change detail work queue is ok:
  ```python
  self._logger.info(
      f"Ticket {ticket_id} and serial {serial_number} task result changed to {task_result} successfully!"
  )
  ```
* Otherwise:
  ```python
  err_msg = (
      f"Error while changing task result for ticket {ticket_id} and serial {serial_number} in "
      f"{self._config.CURRENT_ENVIRONMENT.upper()} environment: "
      f"Error {response_status} - {response_body}"
  )
  [...]
  self._logger.error(err_msg)
  ```