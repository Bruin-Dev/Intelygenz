## Change detail work queue Documentation

```
self._logger.info(
                f"Changing task result of detail {detail_id} / serial {service_number} in ticket {ticket_id} "
                f"to {task_result}..."
            )
```

* if `Exception`
  ```
  self._logger.error(
                f"An error occurred when changing task result of detail {detail_id} / serial {service_number} "
                f"in ticket {ticket_id} to {task_result} -> {e}"
            )
  ```

* if response_status in range(200, 300)
  ```
  self._logger.info(
                    f"Task result of detail {detail_id} / serial {service_number} in ticket {ticket_id} "
                    f"changed to {task_result} successfully!"
                )
  ```
* else
  ```
  self._logger.error(
                    f"Error while changing task result of detail {detail_id} / serial {service_number} in ticket "
                    f"{ticket_id} to {task_result} in {self._config.ENVIRONMENT_NAME.upper()} "
                    f"environment: Error {response_status} - {response_body}"
                )
  ```