## Change detail work queue

```python
logger.info(
    "Changing task result of serial {service_number} in ticket {ticket_id} " f"to {task_result}..."
)
```
* If Exception:
  ```python
  logger.error(
      f"An error occurred when changing task result of serial {service_number} "
      f"in ticket {ticket_id} to {task_result} -> {e}"
  )
  ```
* If status ok:
  ```python
  logger.info(
      f"Task result of detail serial {service_number} in ticket {ticket_id} "
      f"changed to {task_result} successfully!"
  )
  ```
* Else:
  ```python
  logger.error(
      f"Error while changing task result of serial {service_number} in ticket "
      f"{ticket_id} to {task_result} in {self._config.ENVIRONMENT_NAME.upper()} "
      f"environment: Error {response_status} - {response_body}"
  )
  ```