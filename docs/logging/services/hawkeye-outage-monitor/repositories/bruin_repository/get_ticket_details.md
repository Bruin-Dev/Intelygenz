## Get ticket details
```
self._logger.info(f"Getting details of ticket {ticket_id} from Bruin...")
```
* If Exception:
  ```
  self._logger.error(f"An error occurred when requesting ticket details from Bruin API for ticket {ticket_id} 
  -> {e}")
  ```
```
self._logger.info(f"Got details of ticket {ticket_id} from Bruin!")
```
* If status not 200:
  ```
  self._logger.error(f"Error while retrieving details of ticket {ticket_id} in 
  {self._config.CURRENT_ENVIRONMENT.upper()} environment: Error {response_status} - {response_body}")
  ```