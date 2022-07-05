# Change severity

```
self._logger.info(f"Changing severity level of ticket {ticket_id} to {severity_level}...")
```

* If Exception:
  ```
  self._logger.error(f"An error occurred when changing the severity level of ticket {ticket_id} to 
  {severity_level} -> {e}")
  ```
* If status is 200:
  ```
  self._logger.info(f"Severity level of ticket {ticket_id} successfully changed to {severity_level}!")
  ```
* Else:
  ```
  self._logger.error(f"Error while changing severity of ticket {ticket_id} to {severity_level} in "
                     f"{self._config.CURRENT_ENVIRONMENT.upper()} environment: "
                     f"Error {response_status} - {response_body}")
  ```