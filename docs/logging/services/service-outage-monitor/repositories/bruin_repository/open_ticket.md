## Open ticket
```
self._logger.info(f"Opening ticket {ticket_id} (affected detail ID: {detail_id})...")
```
* If Exception:
  ```
  self._logger.error(f"An error occurred when opening outage ticket {ticket_id} -> {e}")
  ```
```
self._logger.info(f"Ticket {ticket_id} opened!")
```     
* If status ok:
  ```
  self._logger.info(f"Ticket {ticket_id} and serial {serial_number} task result changed to  {task_result}")
  ```
* Else:
  ```
  self._logger.error(f"Error while opening outage ticket {ticket_id} in "
                     f"{self._config.CURRENT_ENVIRONMENT.upper()} environment: "
                     f"Error {response_status} - {response_body}")
  ```