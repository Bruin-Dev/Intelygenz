## Mark e-mail as read

```python
logger.info(f"Marking message {msg_uid} from the inbox of {email_account} as read")
```

* If there's an error while asking for the data to the `email-bridge`:
  ```python
  err_msg = f"An error occurred while marking message {msg_uid} as read -> {e}" 
  [...]
  logger.error(err_msg)
  ```
  END

* If response status for mark e-mail as read is ok:
  ```python
  logger.info(f"Marked message {msg_uid} as read")
  ```
* Otherwise:
  ```python
  err_msg = 
  logger.error(
      f"Error marking message {msg_uid} as read in {self._config.ENVIRONMENT_NAME.upper()} environment: "
      f"Error {response_status} - {response_body}"
  )
  ```