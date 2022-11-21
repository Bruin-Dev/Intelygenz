## Unpause ticket detail
```
self._logger.info(f"Unpausing detail {detail_id} (serial {service_number}) of ticket {ticket_id}...")
```
* If Exception:
  ```
  self._logger.error(f"An error occurred when unpausing detail {detail_id} (serial {service_number}) of ticket {ticket_id}. "
                f"Error: {e}")
  ```
* If status ok:
  ```
  self._logger.info(f"Detail {detail_id} (serial {service_number}) of ticket {ticket_id} was unpaused!")
  ```
* Else:
  ```
  self._logger.error(f"Error while unpausing detail {detail_id} (serial {service_number}) of ticket {ticket_id} in "
                    f"{self._config.CURRENT_ENVIRONMENT.upper()} environment. "
                    f"Error: Error {response_status} - {response_body}")
  ```