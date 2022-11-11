## Get unread emails

```python
logger.info(
    f"Getting the unread emails from the inbox of {email_account} sent from the users: " f"{email_filter}"
)
```
* If Exception:
  ```python
  logger.error(f"An error occurred while getting the unread emails from the inbox of {email_account} -> {e}")
  ```
* If status ok:
  ```python
  logger.info(f"Got the unread emails from the inbox of {email_account}")
  ```
* Else:
  ```python
  logger.error(
      f"Error getting the unread emails from the inbox of {email_account} in "
      f"{self._config.ENVIRONMENT_NAME.upper()} environment: Error {response_status} - {response_body}"
  )
  ```