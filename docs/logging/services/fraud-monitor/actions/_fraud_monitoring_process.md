## Fraud monitoring process

```
logger.info(f'Processing all unread email from {self._config.FRAUD_CONFIG["inbox_email"]}')
```
* [get_unread_emails](../repositories/notifications_repository/get_unread_emails.md)
* If status is no Ok:
  ```python
  logger.warning(f"Bad status calling to get unread emails. Skipping fraud monitor process")
  ```
* for email in emails:
  * If message is none or uid -1:
    ```python
    logger.error(f"Invalid message: {email}")
    ```
  * If not email regex:
    ```python
    logger.info(f"Email with msg_uid {msg_uid} is not a fraud warning. Skipping...")
    ``` 
  * If not found body:
    ```python
    logger.error(f"Email with msg_uid {msg_uid} has an unexpected body")
    ```  
  ```python
  logger.info(f"Processing email with msg_uid {msg_uid}")
  ```
  * [_process_fraud](_process_fraud.md)
  * If processed and PRODUCTION:
    * If mark email as read status is Ok:
      ```python
      logger.error(f"Could not mark email with msg_uid {msg_uid} as read")
      ```
  * If processed:
    ```python
    logger.info(f"Processed email with msg_uid {msg_uid}")
    ```
  * Else:
    ```python
    logger.info(f"Failed to process email with msg_uid {msg_uid}")
    ```
```python
logger.info(
    f'Finished processing all unread email from {self._config.FRAUD_CONFIG["inbox_email"]}. '
    f"Elapsed time: {round((stop - start) / 60, 2)} minutes"
)
```