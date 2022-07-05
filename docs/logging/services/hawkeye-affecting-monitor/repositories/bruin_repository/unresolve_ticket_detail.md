## Unesolve ticket detail
```
self._logger.info(f"Unresolving detail {detail_id} of ticket {ticket_id}...")
```
* If Exception:
  ```
  self._logger.error(f"An error occurred when unresolving detail {detail_id} of affecting ticket {ticket_id} -> {e}")
  ```
* If status ok:
  ```
  self._logger.info(f"Detail {detail_id} of ticket {ticket_id} unresolved successfully!")
  ```
* Else:
  ```
  self._logger.error(f"Error while unresolving detail {detail_id} of affecting ticket {ticket_id} in "
                    f"{self._config.CURRENT_ENVIRONMENT.upper()} environment: "
                    f"Error {response_status} - {response_body}")
  ```