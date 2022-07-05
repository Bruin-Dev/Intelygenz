## Change detail work queue
```
self._logger.info(f"Changing task result for ticket {ticket_id} and detail id {detail_id} for device 
{serial_number} to {task_result}...")
```
* If Exception:
  ```
  self._logger.error(f"An error occurred when changing task result for ticket {ticket_id} and serial{serial_number}")
  ```
* If status ok:
  ```
  self._logger.info(f"Ticket {ticket_id} and serial {serial_number} task result changed to  {task_result}")
  ```
* Else:
  ```
  self._logger.info(f"Error while changing task result for ticket {ticket_id} and serial {serial_number} in "
                    f"{self._config.CURRENT_ENVIRONMENT.upper()} environment: "
                    f"Error {response_status} - {response_body}")
  ```