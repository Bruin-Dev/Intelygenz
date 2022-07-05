## Resolve ticket detail
```
self._logger.info(f"Resolving ticket {ticket_id} (affected detail ID: {detail_id})...")
```
* If Exception:
  ```
  self._logger.error(f"An error occurred when resolving ticket {ticket_id} -> {e}")
  ```
```
self._logger.info(f"Ticket {ticket_id} resolved!")
```
* If status not ok:
  ```
  self._logger.error(f"Error while resolving ticket {ticket_id} in {self._config.CURRENT_ENVIRONMENT.upper()} "
                    f"environment: Error {response_status} - {response_body}")
  ```