## Post live automation metrics
```
self._logger.info(f"Posting live metric for ticket {ticket_id} to T7...")
```
* If Exception:
  ```
  self._logger.error(f"An error occurred when posting live metrics for ticket {ticket_id} to T7. Error: {e}")
  ```
* If status is OK:
  ```
  self._logger.info(f"Live metrics posted for ticket {ticket_id}!")
  ```
* If status not 200:
  ```
  self._logger.error(f"Error when posting live metrics for ticket {ticket_id} to T7 in "
                    f"{self._config.ENVIRONMENT_NAME.upper()} "
                    f"environment. Error: Error {response_status} - {response_body}")
  ```