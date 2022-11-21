## Get prediction
```
self._logger.info(f"Claiming T7 prediction for ticket {ticket_id}...")
```
* If Exception:
  ```
  self._logger.error(f"An error occurred when claiming T7 prediction for ticket {ticket_id}. Error: {e}")
  ```
```
self._logger.info(f"Got T7 prediction for ticket {ticket_id}!")
```
* If status not 200:
  ```
  self._logger.error(f"Error while claiming T7 prediction for ticket {ticket_id} in "
                    f"{self._config.ENVIRONMENT_NAME.upper()} environment. "
                    f"Error: Error {response_status} - {response_body}")
  ```