## Resolve ticket detail
```
self._logger.info(f"Resolving detail {detail_id} of ticket {ticket_id}...")
```
* If Exception:
  ```
  self._logger.error(f"An error occurred when resolving detail {detail_id} of affecting ticket {ticket_id} -> {e}")
  ```
```
self._logger.info(f"Ticket {ticket_id} resolved!")
```
* If status not ok:
  ```
  self._logger.error(f"Error while resolving detail {detail_id} of ticket {ticket_id} in "
                    f"{self._config.ENVIRONMENT_NAME.upper()} environment: "
                    f"Error {response_status} - {response_body}")
  ```
* Else:
  ```
  self._logger.info(f"Detail {detail_id} of ticket {ticket_id} resolved successfully!")
```