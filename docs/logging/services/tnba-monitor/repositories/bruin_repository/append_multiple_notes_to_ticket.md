## Append multiple notes to ticket
```
self._logger.info(f"Posting multiple notes for ticket {ticket_id}...")
```
* If Exception:
  ```
  self._logger.error(f"An error occurred when appending multiple ticket notes to ticket {ticket_id}. "
                f"Notes: {notes}. Error: {e}")
  ```
```
self._logger.info(f"Posted multiple notes for ticket {ticket_id}!")
```
* Else:
  ```
  self._logger.error(f"Error while appending multiple notes to ticket {ticket_id} in "
                    f"{self._config.ENVIRONMENT_NAME.upper()} environment. Notes were {notes}. "
                    f"Error: Error {response_status} - {response_body}")
  ```