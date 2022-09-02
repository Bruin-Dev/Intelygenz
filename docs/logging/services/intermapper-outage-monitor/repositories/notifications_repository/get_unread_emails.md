## Get unread emails

```python
self._logger.info(
    f"Getting the unread emails from the inbox of {email_account} sent from the users: "
    f"{email_filter} in the last {lookup_days} days"
)
```

* If there's an error while asking for the data to the `email-bridge`:
  ```python
  err_msg = f"An error occurred while getting the unread emails from the inbox of {email_account} -> {e}"
  [...]
  self._logger.error(err_msg)
  ```
  END

* If response status for get unread emails is not ok:
  ```python
  err_msg = (
      f"Error getting the unread emails from the inbox of {email_account} in "
      f"{self._config.ENVIRONMENT_NAME.upper()} environment: "
      f"Error {response_status} - {response_body}"
  )
  [...]
  self._logger.error(err_msg)
  ```
* Otherwise:
  ```python
  self._logger.info(f"Got the unread emails from the inbox of {email_account}")
  ```