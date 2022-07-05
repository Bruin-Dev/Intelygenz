## Mark email as read
```
self._logger.info(f"Marking message {msg_uid} from the inbox of {email_account} as read")
```
* If Exception:
  ```
  self._logger.error(f"An error occurred while marking message {msg_uid} as read -> {e}")
  ```
* If status ok:
  ```
  self._logger.info(f"Marked message {msg_uid} as read")
  ```
* Else:
  ```
  self._logger.error(f"Error marking message {msg_uid} as read in "
                    f"{self._config.ENVIRONMENT_NAME.upper()} environment: "
                    f"Error {response_status} - {response_body}")
  ```