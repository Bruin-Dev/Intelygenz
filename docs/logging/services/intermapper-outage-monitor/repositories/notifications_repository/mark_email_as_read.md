## Mark email as read

```python
self._logger.info(f"Marking message {msg_uid} from the inbox of {email_account} as read")
```

* If there's an error while posting the data to the `email-bridge`:
  ```python
  err_msg = f"An error occurred while marking message {msg_uid} as read -> {e}"
  [...]
  self._logger.error(err_msg)
  ```
  END

* If response status for mark email as read is not ok:
  ```python
  err_msg = (
      f"Error marking message {msg_uid} as read in "
      f"{self._config.ENVIRONMENT_NAME.upper()} environment: "
      f"Error {response_status} - {response_body}"
  )
  [...]
  self._logger.error(err_msg)
  ```
* Otherwise:
  ```python
  self._logger.info(f"Marked message {msg_uid} as read")
  ```