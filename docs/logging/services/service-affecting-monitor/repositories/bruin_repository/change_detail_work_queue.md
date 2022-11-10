## Change work queue for ticket task

```python
logger.info(
    f"Changing task result of detail {detail_id} / serial {service_number} in ticket {ticket_id} "
    f"to {task_result}..."
)
```

* If there's an error while posting the data to the `bruin-bridge`:
  ```python
  err_msg = (
      f"An error occurred when changing task result of detail {detail_id} / serial {service_number} "
      f"in ticket {ticket_id} to {task_result} -> {e}"
  )
  [...]
  logger.error(err_msg)
  ```
  END

* If response status for change work queue for ticket task is ok:
  ```python
  logger.info(
      f"Task result of detail {detail_id} / serial {service_number} in ticket {ticket_id} "
      f"changed to {task_result} successfully!"
  )
  ```
* Otherwise:
  ```python
  err_msg = (
      f"Error while changing task result of detail {detail_id} / serial {service_number} in ticket "
      f"{ticket_id} to {task_result} in {self._config.ENVIRONMENT_NAME.upper()} "
      f"environment: Error {response_status} - {response_body}"
  )
  [...]
  logger.error(err_msg)
  ```