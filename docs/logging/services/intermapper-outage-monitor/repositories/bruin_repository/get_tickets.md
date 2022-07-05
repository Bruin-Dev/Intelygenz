## Get tickets
```
self._logger.info(f"Getting all tickets of ticket id {ticket_id} from Bruin...")
```
* If Exception:
  ```
  self._logger.error(f"An error occurred when requesting all tickets of ticket id {ticket_id} from Bruin API -> {e}")
  ```
* If status not Ok:
  ```
  self._logger.error(f"Error while retrieving all tickets of ticket id {ticket_id} in "
                    f"{self._config.ENVIRONMENT_NAME.upper()} environment: "
                    f"Error {response_status} - {response_body}")
  ```
* Else: 
  ```
  self._logger.info(f"Got all tickets of ticket id {ticket_id} from Bruin")
  ```