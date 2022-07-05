## Change detail work queue
```
self._logger.info(
                f"Changing task result of serial {service_number} in ticket {ticket_id} " f"to {task_result}..."
            )
```
* If Exception:
  ```
  self._logger.error(f"An error occurred when changing task result of serial {service_number} "
                f"in ticket {ticket_id} to {task_result} -> {e}")
  ```
* If status ok:
  ```
  self._logger.info(f"Task result of detail serial {service_number} in ticket {ticket_id} "
                    f"changed to {task_result} successfully!")
  ```
* Else:
  ```
  self._logger.error(f"Error while changing task result of serial {service_number} in ticket "
                    f"{ticket_id} to {task_result} in {self._config.ENVIRONMENT_NAME.upper()} "
                    f"environment: Error {response_status} - {response_body}")
  ```