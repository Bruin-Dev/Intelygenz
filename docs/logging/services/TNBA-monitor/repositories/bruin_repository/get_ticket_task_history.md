## Get ticket task history
```
self._logger.info(f"Getting task history of ticket {ticket_id} from Bruin...")
```
* If Exception:
  ```
  self._logger.error(f"An error occurred when requesting task history from Bruin API for ticket {ticket_id} -> {e}")
  ```
```
self._logger.info(f"Got task history of ticket {ticket_id} from Bruin!")
```
* If status not 200:
  ```
  self._logger.error(f"Error while retrieving task history of ticket {ticket_id} in "
                    f"{self._config.ENVIRONMENT_NAME.upper()} environment: "
                    f"Error {response_status} - {response_body}")
  ```