## Reboot link
```
self._logger.info(f"Rebooting DiGi link of ticket {ticket_id} from Bruin...")
```
* If Exception:
  ```
  self._logger.error(f"An error occurred when attempting a DiGi reboot for ticket {ticket_id} -> {e}")
  ```
```
self._logger.info(f"Got details of ticket {ticket_id} from Bruin!")
 ```
* If status not ok:
  ```
  self._logger.error(f"Error while attempting a DiGi reboot for ticket {ticket_id} in 
  {self._config.CURRENT_ENVIRONMENT.upper()} environment: Error {response_status} - {response_body}")
  ```